# 게스트 부팅 디스크 복구

가상머신의 운영체제가 부팅 디스크 문제로 시작되지 않을 때, 가상머신을 종료한 뒤 노드에서 부팅 디스크를 직접 열어 점검·복구하는 절차입니다. 루트 파일시스템 손상, 잘못된 `/etc/fstab`, 디스크 드라이버가 빠진 initramfs를 다룹니다.

부팅 디스크는 노드에 설치된 `guestfish`로 엽니다. `guestfish`는 별도의 작은 가상 환경 안에서 디스크를 엽니다. 그래서 게스트의 LVM 볼륨은 그 안에서만 활성화되고, 노드 커널이 손상된 파일시스템을 마운트하지도 않습니다. 부팅 디스크가 `CEPH` 스토리지 도메인에 있든 파일 기반(`LOCAL`, `GFS2`, `NFS`, `CEPHFS`) 스토리지 도메인에 있든 같은 방법으로 복구합니다.

> ⚠️ 주의: Linux 게스트의 XFS·ext4 파일시스템이 대상입니다. Windows 게스트, 게스트 안에서 암호화한 디스크(LUKS 등), 그 밖의 파일시스템은 이 문서에서 다루지 않습니다.

> ⚠️ 주의: 복구하는 동안 부팅 디스크에 쓰는 곳은 한 곳뿐이어야 합니다. 가상머신이 어느 노드에서든 실행 중일 때 디스크를 수정하면 디스크가 다시 손상됩니다.

## 증상과 원인

게스트가 emergency 모드에 머물러도 가상머신 자체는 켜져 있으므로 관리자 콘솔의 상태는 `실행 중`으로 표시됩니다. 콘솔(noVNC) 화면에는 GRUB의 `Booting ...` 줄만 보이고 진행되지 않을 수도 있습니다. 게스트 설정에 따라 부팅 메시지가 시리얼 콘솔로만 나오는 경우입니다. 이때는 가상머신이 떠 있는 노드(`물리 머신`)에서 시리얼 콘솔 기록을 확인합니다. 종료하면 도메인 정의가 사라지므로, 이 확인은 1)에서 종료하기 전에 합니다. `<ID>`는 아래 사전 확인 값의 가상머신 ID입니다.

```bash
virsh list --name | grep '_id_<ID>_'                # 도메인 이름 확인
virsh dumpxml '<도메인>' | grep 'console.log'         # 시리얼 콘솔 기록 경로 확인
tail -n 50 '<시리얼 콘솔 기록 경로>'
```

시리얼 콘솔 기록에는 이전 부팅 내용도 이어서 쌓이므로 마지막 부분을 봅니다.

| 시리얼 콘솔 메시지 | 원인 | 복구 단계 |
| --- | --- | --- |
| `Timed out waiting for device ...`, `Dependency failed for local-fs.target` 뒤 `You are in emergency mode` | `/etc/fstab`에 존재하지 않는 장치가 등록되어 있습니다. | 6) 부팅 설정 복구 |
| `XFS (...): Corruption ... Shutting down filesystem`, `Failed to mount sysroot.mount` 뒤 `Entering emergency mode` | 루트 파일시스템이 손상되었습니다. | 5) 파일시스템 점검·복구 |
| `dracut-initqueue: starting timeout scripts`, `Could not boot`, `/dev/mapper/... does not exist` | initramfs에 디스크 드라이버가 없는 경우가 대표적입니다. | 6) 부팅 설정 복구 |

> 💡 참고: 파일시스템 손상은 노드 페일오버 뒤에 주로 발견됩니다. 같은 가상머신이 두 노드에서 동시에 실행되면 디스크가 손상되므로, 1)에서 함께 확인합니다. initramfs 드라이버 누락은 다른 가상화 플랫폼에서 만든 이미지를 들여와 쓸 때 주로 발생합니다.

> 💡 참고: 게스트 콘솔에 root로 로그인할 수 있으면 emergency 셸에서 직접 고쳐도 됩니다. 이 문서는 로그인할 수 없을 때의 절차입니다.

## 사전 확인 값 (관리자 콘솔)
| 값 | 확인 위치 |
| --- | --- |
| **가상머신 이름** | `인스턴스 > 인스턴스 상세 > 기본 정보 > 이름` |
| **가상머신 ID** | `인스턴스 > 인스턴스 상세 > 기본 정보 > ID` |
| **물리 머신**(배치 노드) | `인스턴스 > 인스턴스 상세 > 기본 정보 > 물리 머신` |
| **풀 이름**(`CEPH`) | `스토리지 > 스토리지 도메인 > 목록 > 풀 이름` |
| **마운트 포인트**(파일 기반) | `스토리지 > 스토리지 도메인 > 목록 > 마운트 포인트`. `CEPHFS`는 노드에서 `findmnt -t ceph`로 확인합니다. |

> 💡 참고: 부팅 디스크 이름에는 가상머신 ID(`_id_<ID>_`)가 들어가고 `_blk`로 끝납니다. 파일 기반 스토리지 도메인에서는 여기에 `.qcow2`가 붙습니다. 이름은 다른 가상머신과 겹칠 수 있으므로 ID로 찾습니다.

## 복구 절차

명령은 `root` 권한으로 실행합니다. `CEPH` 부팅 디스크는 Ceph 명령을 실행할 수 있는 관리 노드에서, 파일 기반 부팅 디스크는 그 파일이 보이는 노드에서 작업합니다. `LOCAL` 스토리지 도메인은 해당 물리 머신에서만 파일이 보입니다. 아래에서 `<부팅 디스크 파일>`은 파일의 전체 경로입니다.

작업할 노드에 `guestfish`가 없으면(`command -v guestfish`로 확인) 설치 저장소에서 설치합니다. 구성에 따라 관리 노드에만 설치되어 있을 수 있습니다.

```bash
dnf install -y --disablerepo='*' --enablerepo=closed_network guestfs-tools
```

### 1) 가상머신 종료와 중복 실행 확인
1. 관리자 콘솔에서 인스턴스를 **종료**하고, 상태가 `종료됨`이 될 때까지 기다립니다. 게스트가 emergency 모드에 있어도 종료됩니다.
2. 상태가 `종료됨`인지 다시 확인합니다. `종료됨` 인스턴스는 자동 재시작과 페일오버로는 다시 켜지지 않습니다. 상태가 `정지됨`이나 `에러`이면 자동 재시도 대상일 수 있으므로, **종료**를 눌러 `종료됨`으로 만든 뒤 진행합니다. 다른 관리자가 이 인스턴스를 **실행**하지 않도록 작업 중임을 알립니다.
3. 인스턴스가 속한 프로젝트의 `스케줄러 > 일정`에 이 인스턴스를 켜는 일정이 있으면 비활성화합니다. 일정에 의한 실행은 상태와 관계없이 인스턴스를 켭니다. 7)에서 다시 활성화합니다.
4. 가상머신을 실행할 수 있는 모든 노드에서 이 가상머신이 남아 있지 않은지 확인합니다. 정상적으로 종료되었다면 아무것도 출력되지 않습니다.

   ```bash
   virsh list --all | grep '_id_<ID>_'
   ```

   종료 직후에는 잠시 남아 있을 수 있습니다. 1분쯤 뒤에 다시 확인해도 출력되는 노드가 있으면, 그 노드에 남은 것은 관리되지 않는 유령(orphan)입니다. 노드 페일오버 과정에서 같은 가상머신이 두 노드에서 동시에 실행되면 생깁니다. 해당 노드에서 직접 정리합니다.

   ```bash
   virsh destroy  '<도메인>'
   virsh undefine --keep-nvram --keep-tpm '<도메인>'
   ```

   > ⚠️ 주의: `virsh undefine`에는 반드시 `--keep-nvram --keep-tpm`을 붙입니다. vTPM 상태는 공유 스토리지에 있어서, 유령을 정리하면서 지우면 실제 가상머신이 vTPM에 저장한 정보(디스크 암호화 키 등)를 잃습니다. `--nvram`이나 `--tpm`은 쓰지 않습니다.

5. 가상머신이 실행 중이던 노드에 접속할 수 없으면, 그 노드의 전원이 꺼졌음을 BMC 등으로 확인하기 전에는 진행하지 않습니다. `CEPH`는 2)의 차단 방법도 쓸 수 있습니다.

### 2) 부팅 디스크 찾기와 사용 중 확인
부팅 디스크를 찾고, 아무도 디스크를 쓰고 있지 않은지 확인합니다. 부팅 디스크가 어느 스토리지 도메인에 있는지 모르면 두 방법으로 모두 찾아봅니다.

**CEPH**

```bash
rbd ls <풀 이름> | grep -E '_id_<ID>_.*_blk$'
rbd status <풀 이름>/<부팅 디스크>          # Watchers: none 이어야 합니다
```

`Watchers`가 남아 있으면 1)로 돌아가 실행 중인 곳을 정리합니다. 그 노드에 접속할 수 없어 정리할 수 없으면, `Watchers` 줄의 `watcher=` 뒤 주소(`<ip:0/nonce>`)로 그 클라이언트만 차단합니다. IP 전체를 차단하지 않습니다.

```bash
ceph osd blocklist add <ip:0/nonce>
```

**파일 기반**

```bash
find <마운트 포인트> -maxdepth 2 -name '*_id_<ID>_*_blk.qcow2'
qemu-img info <부팅 디스크 파일>
```

`qemu-img info`가 `Failed to get shared "write" lock` 오류를 내면 다른 프로세스가 아직 디스크를 쓰고 있는 것입니다. 1)로 돌아가 실행 중인 곳을 정리합니다. 이 오류가 없다고 안전이 보장되지는 않으므로, 판단 기준은 1)의 확인입니다.

> 💡 참고: 파일 기반 부팅 디스크는 원본 이미지를 바탕(backing file)으로 하는 차분 파일입니다. 바탕 파일 전체는 `qemu-img info --backing-chain <부팅 디스크 파일>`로 확인합니다. 이 절차는 가상머신의 차분 파일만 수정하며, 같은 이미지로 만든 다른 가상머신이 함께 쓰는 바탕 파일은 바꾸지 않습니다.

### 3) 백업
복구 명령은 되돌릴 수 없으므로 먼저 백업합니다.

```bash
BK=before-repair-$(date +%Y%m%d-%H%M)      # 이번 작업의 백업 이름

# CEPH
rbd snap create <풀 이름>/<부팅 디스크>@$BK

# 파일 기반 (차분 파일만 복사하면 됩니다)
cp --sparse=always <부팅 디스크 파일> <부팅 디스크 파일>.$BK
```

백업 이름에 작업 시각을 붙여 이전 작업의 백업과 섞이지 않게 합니다. 7)에서 같은 이름을 쓰므로, 셸을 새로 열 때를 대비해 `echo $BK`로 이름을 적어 둡니다.

### 4) 디스크 열기
**CEPH**: 부팅 디스크를 노드에 연결(map)하고, 출력된 장치를 엽니다.

```bash
export LIBGUESTFS_BACKEND=direct           # libvirt를 거치지 않고 바로 엽니다
DEV=$(rbd device map <풀 이름>/<부팅 디스크>)
echo $DEV                                   # 예: /dev/rbd0
guestfish -a $DEV
```

**파일 기반**: 부팅 디스크 파일을 바로 엽니다.

```bash
export LIBGUESTFS_BACKEND=direct
guestfish -a <부팅 디스크 파일>
```

`guestfish` 프롬프트(`><fs>`)에서 디스크를 시작하고 파일시스템 목록을 확인합니다.

```
><fs> run
><fs> list-filesystems
/dev/sda1: unknown
/dev/sda2: xfs
/dev/rl/root: xfs
/dev/rl/swap: swap
><fs> inspect-os
/dev/rl/root
```

- 디스크 하나만 열었으므로 `guestfish` 안에서는 디스크가 `/dev/sda`로 보입니다.
- 루트 파일시스템은 이미지에 따라 LVM 볼륨(위 예의 `/dev/rl/root`)이거나 파티션(`/dev/sda4` 등)입니다. 파티션 번호를 짐작하지 말고 `inspect-os` 결과로 확인합니다.
- 루트가 심하게 손상되어 `inspect-os`가 루트를 찾지 못하면, `list-filesystems`의 XFS·ext4 후보를 하나씩 읽기 전용으로 마운트해 봅니다. `is-file` 결과가 `true`인 후보가 루트입니다. `/boot`·`/home` 같은 다른 볼륨에는 `/etc/fstab`이 없습니다. 마운트되지 않는 후보가 손상된 루트일 가능성이 높지만, 다른 후보를 모두 확인해 제외한 뒤에 복구합니다.

  ```
  ><fs> mount-ro <후보 장치> /
  ><fs> is-file /etc/fstab
  ><fs> umount /
  ```
- 위 예에서 `/dev/sda2`는 `/boot`입니다. `/boot`도 XFS나 ext4이면 루트와 같은 방법으로 점검할 수 있습니다.
- `unknown`으로 표시되는 작은 파티션(BIOS boot)과 EFI 시스템 파티션(vfat)은 건드리지 않습니다.

### 5) 파일시스템 점검·복구
먼저 점검만 하고, 손상이 있을 때 복구합니다. 아래 예의 `/dev/rl/root` 자리에 4)에서 확인한 루트 장치를 넣습니다.

**XFS (Rocky / RHEL 계열)**

```
><fs> xfs-repair /dev/rl/root nomodify:true
1
><fs> xfs-repair /dev/rl/root
0
><fs> xfs-repair /dev/rl/root nomodify:true
0
```

| 명령 | 동작과 결과 |
| --- | --- |
| `xfs-repair <루트 장치> nomodify:true` | 점검만 합니다. `1`이면 손상이 있고, `0`이면 정상입니다. |
| `xfs-repair <루트 장치>` | 복구합니다. `0`이면 복구가 끝난 것입니다. 복구 뒤 다시 점검해 `0`이 나오는지 확인합니다. |
| `mount <루트 장치> /` 후 `umount /` | 로그 재생이 필요하다는 오류로 복구가 거부될 때 씁니다. 마운트하면서 로그를 재생한 뒤 다시 복구합니다. |
| `xfs-repair <루트 장치> forcelogzero:true` | 위의 마운트도 실패할 때만 씁니다(`xfs_repair -L`과 같습니다). 로그에 남은 최근 변경을 버리므로 3) 백업을 먼저 확인합니다. |

**ext4 (Ubuntu 계열)**

```
><fs> e2fsck <루트 장치> correct:true
><fs> e2fsck <루트 장치> forceall:true
```

- `correct:true`는 안전하게 고칠 수 있는 문제만 자동으로 고칩니다.
- 그래도 오류가 남으면 `forceall:true`(모든 질문에 yes)로 복구합니다.
- 성공하면 아무것도 출력하지 않습니다. 고칠 수 없는 손상이면 `e2fsck` 오류 메시지가 출력됩니다.
- Ubuntu 클라우드 이미지의 루트는 보통 `/dev/sda1`입니다.

### 6) 부팅 설정 복구
파일시스템이 정상이면 `-i` 옵션으로 게스트의 파일시스템을 마운트한 상태로 엽니다. 이미 `guestfish`를 열어 두었다면 `exit`로 나온 뒤 다시 엽니다.

```bash
guestfish -a $DEV -i                      # 파일 기반: guestfish -a <부팅 디스크 파일> -i
```

```
><fs> mountpoints
/dev/rl/root: /
/dev/sda2: /boot
```

`mountpoints` 결과에서 `/`와 `/boot`가 각각 루트 장치와 `/boot` 파티션에 마운트되었는지 확인합니다.

`/etc/fstab`의 문법이 깨져 있으면 `-i`로 열 때 `inspect_os: /etc/fstab ... augeas parse failure` 오류가 나고 열리지 않습니다. 이때는 `-i` 없이 열고, 4)에서 확인한 장치를 직접 마운트합니다. initramfs를 다시 만들 때는 `/boot`도 마운트합니다.

```
><fs> run
><fs> mount <루트 장치> /
><fs> mount <boot 파티션> /boot
```

**fstab 수정**

```
><fs> cat /etc/fstab
><fs> edit /etc/fstab
```

`edit`는 편집기(vi)로 파일을 엽니다. 존재하지 않는 장치를 가리키는 줄을 지우거나, 없어도 부팅이 되어야 하는 장치에는 `nofail` 옵션을 붙입니다. 편집기 대신 줄을 지울 수도 있습니다.

```
><fs> sh "sed -i '/<문제 장치의 UUID>/d' /etc/fstab"
><fs> cat /etc/fstab
```

**initramfs 재생성 (RHEL 계열)**

RHEL 계열(Rocky 등)처럼 `dracut`을 쓰는 게스트가 대상입니다.

```
><fs> ls /lib/modules
6.12.0-211.55.1.el10_2.x86_64
><fs> sh "dracut -f --no-hostonly /boot/initramfs-<커널 버전>.img <커널 버전>"
><fs> sh "ls -l /boot/initramfs-<커널 버전>.img"
```

- `<커널 버전>`에는 `ls /lib/modules` 결과를 넣습니다. 커널이 여러 개면 부팅에 쓰는 커널(보통 가장 최신)을 다시 만듭니다.
- `--no-hostonly`를 꼭 붙입니다. 빠지면 `guestfish`의 임시 가상 환경을 기준으로 드라이버를 고르므로, 가상머신에 필요한 드라이버가 빠질 수 있습니다.
- 1분 정도 걸립니다. 끝나면 마지막 명령 결과의 수정 시각이 방금으로 바뀌었는지 확인합니다.

### 7) 닫기, 기동, 정리
1. `guestfish`를 닫고, `CEPH`이면 연결을 해제합니다. `rbd device list`에 장치가 남아 있지 않아야 합니다. 해제에 실패하면 인스턴스를 실행하지 않습니다.

   ```
   ><fs> exit
   ```

   ```bash
   rbd device unmap $DEV      # CEPH만
   rbd device list
   ```

2. 관리자 콘솔에서 인스턴스를 **실행**합니다.
3. 콘솔 로그인 화면이나 시리얼 콘솔 기록에서 정상 부팅을 확인합니다.
4. 복구 결과가 잘못되었으면 인스턴스를 다시 `종료됨`으로 만들고, 1)·2)의 확인을 다시 한 뒤 백업으로 되돌립니다. `CEPH`는 연결을 해제한 상태에서 되돌립니다.

   ```bash
   rbd snap rollback <풀 이름>/<부팅 디스크>@$BK                  # CEPH
   cp --sparse=always <부팅 디스크 파일>.$BK <부팅 디스크 파일>      # 파일 기반
   ```

5. 정상 부팅을 확인했으면 백업을 지웁니다.

   ```bash
   rbd snap rm <풀 이름>/<부팅 디스크>@$BK      # CEPH
   rm <부팅 디스크 파일>.$BK                    # 파일 기반
   ```

6. 1)에서 비활성화한 일정이 있으면 다시 활성화합니다.

## 주의 사항
- 3) 백업 없이 복구하지 않습니다. `forcelogzero:true`(`xfs_repair -L`)는 최후 수단입니다.
- 파일 기반 부팅 디스크의 바탕 파일(backing file)은 직접 열거나 수정하지 않습니다. 같은 이미지로 만든 다른 가상머신이 함께 망가집니다.
- 복구하는 동안 물리 머신 유지보수 복귀 작업을 진행하지 않습니다. 유지보수 중 종료된 인스턴스를 다시 켤 수 있습니다.
- 1)에서 유령을 정리했다면, 복구 뒤 그 시점에 노드 장애나 페일오버가 있었는지 확인합니다. 같은 원인이 남아 있으면 다시 손상될 수 있습니다.
