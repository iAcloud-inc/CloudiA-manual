# ISO로 설치한 Rocky 인스턴스를 골든 이미지로 준비하기

이 문서는 `ISO 파일`로 설치한 Rocky Linux 인스턴스를 골든 이미지로 사용할 수 있도록 준비하는 실습입니다. 필요한 패키지 설치, 이미지로 만들기 전 정리(일반화), 종료 방법, 이미지 생성, 새 인스턴스 확인까지 설명합니다. 인터넷이 없는 폐쇄망에서도 설치에 쓴 DVD로 패키지를 설치할 수 있습니다.

## 사전 준비
- Cloud:iA 웹콘솔 접근 가능
- 프로젝트 계정(`project-owner`)으로 로그인 가능
- Rocky Linux **DVD ISO**로 설치한 인스턴스가 준비되어 있어야 함
  - DVD ISO에는 `cloud-init`, `cloud-utils-growpart`, `qemu-guest-agent`가 들어 있습니다. `minimal ISO`에는 이 세 패키지가 없습니다.
  - 설치 방법은 [Rocky Linux ISO 업로드 후 VM 설치](./20-install-rocky-instance-from-iso.md)을 참고합니다. 설치할 때 IPv4를 수동(`Manual`)으로 설정해야 접속할 수 있습니다.
  - 설치 CD(CD-ROM)는 설치 뒤에도 인스턴스에 붙어 있습니다. 2단계에서 이 DVD를 패키지 저장소로 씁니다.
- 관련 실습을 먼저 확인하면 진행이 쉬움
  - [스냅샷 이미지 생성으로 골든 이미지 만들기 및 인스턴스 실행](./16-create-golden-image-from-snapshot.md)

## 개요
1. [설치 상태 확인](#step-1)
2. [필요한 패키지 설치](#step-2)
3. [직렬 콘솔 설정 확인](#step-3)
4. [일반화(이미지에 남기지 않을 정보 정리)](#step-4)
5. [Cloud:iA 웹에서 인스턴스 종료](#step-5)
6. [스냅샷과 이미지 생성](#step-6)
7. [골든 이미지로 만든 인스턴스 확인](#step-7)

> ⚠️ **주의:** 이 문서의 준비(패키지 설치와 일반화) 없이 만든 이미지로 인스턴스를 만들면 입력한 계정이 만들어지지 않아 로그인할 수 없습니다. 설치 때 만든 계정이 그대로 남고, 새로 배정한 IP가 적용되지 않아 **원본 인스턴스의 IP, 호스트 이름, machine-id**로 뜹니다. 원본이 켜져 있으면 IP가 충돌합니다.

<a id="step-1"></a>
## 1단계: 설치 상태 확인
**수행 계정/화면:** `인스턴스 콘솔` / `Rocky Linux`

### 절차
1. 인스턴스 상세 화면에서 `콘솔`을 클릭하고 메뉴에서 `그래픽 콘솔`을 선택해 root 또는 sudo 권한이 있는 계정으로 로그인합니다.
2. 필요한 패키지가 설치되어 있는지 확인합니다.

   ```bash
   rpm -q cloud-init cloud-utils-growpart qemu-guest-agent
   systemctl is-active qemu-guest-agent
   ```

3. 설치할 때 만든 고정 IP 연결 프로필 이름을 확인해 적어 둡니다. 4단계에서 이 프로필을 삭제합니다.

   ```bash
   nmcli con show
   ```

### 확인
- 설치된 패키지는 버전이 표시되고, 설치되지 않은 패키지는 `is not installed`로 표시됩니다. 설치되지 않은 패키지가 있으면 2단계에서 설치합니다.
- `qemu-guest-agent`는 Rocky 설치 프로그램이 자동으로 설치하므로 보통 이미 설치되어 있고, `systemctl is-active`가 `active`를 출력합니다.
- `nmcli con show`에 설치 때 만든 연결 프로필이 보입니다. NIC(장치) 이름은 보통 `enp1s0`이며 환경에 따라 다를 수 있습니다.

<a id="step-2"></a>
## 2단계: 필요한 패키지 설치
**수행 계정/화면:** `인스턴스 콘솔` / `Rocky Linux`

1단계에서 설치되지 않은 패키지가 있을 때 진행합니다. 인터넷이 되는 환경이면 아래 한 줄로 설치하고 3단계로 넘어갑니다.

```bash
sudo dnf install -y cloud-init cloud-utils-growpart qemu-guest-agent
```

폐쇄망에서는 인스턴스에 붙어 있는 설치 DVD를 로컬 저장소로 씁니다. 의존 패키지도 DVD에서 함께 설치됩니다.

### 절차
1. DVD 장치를 확인합니다. `lsblk`에서 크기가 큰 `rom` 장치가 설치 DVD입니다. 아래 예시는 `/dev/sr0`입니다.

   ```bash
   lsblk
   ```

2. DVD를 마운트합니다.

   ```bash
   sudo mount -o ro /dev/sr0 /mnt
   ```

3. DVD 저장소 파일을 만듭니다.

   ```bash
   sudo tee /etc/yum.repos.d/dvd.repo <<'EOF'
   [dvd-BaseOS]
   name=DVD BaseOS
   baseurl=file:///mnt/BaseOS
   gpgcheck=1
   gpgkey=file:///mnt/RPM-GPG-KEY-Rocky-9
   [dvd-AppStream]
   name=DVD AppStream
   baseurl=file:///mnt/AppStream
   gpgcheck=1
   gpgkey=file:///mnt/RPM-GPG-KEY-Rocky-9
   EOF
   ```

4. DVD 저장소만 사용해 패키지를 설치합니다.

   ```bash
   sudo dnf --disablerepo='*' --enablerepo='dvd-*' install -y cloud-init cloud-utils-growpart qemu-guest-agent
   ```

### 확인
- `rpm -q cloud-init cloud-utils-growpart qemu-guest-agent`에 세 패키지의 버전이 모두 표시됩니다.

> 💡 **참고:** 기본 저장소 설정은 인터넷 미러를 가리키므로 폐쇄망에서는 `--disablerepo='*'`가 필요합니다. 빼면 인터넷 미러에 접속하지 못해 설치가 진행되지 않을 수 있습니다. DVD는 OS를 설치한 DVD와 같은 판(버전)이어야 합니다. 예시의 `RPM-GPG-KEY-Rocky-9`는 Rocky 9 기준이므로 다른 판이면 `/mnt`에 있는 키 파일 이름으로 바꿉니다.

<a id="step-3"></a>
## 3단계: 직렬 콘솔 설정 확인
**수행 계정/화면:** `인스턴스 콘솔` / `Rocky Linux`

ISO로 설치한 Rocky는 직렬 콘솔 설정이 기본으로 빠져 있습니다. 이 인스턴스로 골든 이미지를 만들면 설정이 이미지에 담겨, 그 이미지로 만든 인스턴스에서도 `직렬 콘솔`과 `콘솔 로그 다운로드`를 바로 쓸 수 있습니다. 4단계 일반화 뒤에는 재부팅하면 안 되므로 이 단계를 먼저 마칩니다.

### 절차
1. `cat /proc/cmdline` 출력에 `console=ttyS0,115200`이 있는지 확인합니다.
2. 없으면 [Rocky Linux ISO 업로드 후 VM 설치 — 7단계](./20-install-rocky-instance-from-iso.md#step-7)를 따라 설정하고 인스턴스를 재부팅합니다.

### 확인
- `cat /proc/cmdline` 출력에 `console=ttyS0,115200`이 포함됩니다.

<a id="step-4"></a>
## 4단계: 일반화(이미지에 남기지 않을 정보 정리)
**수행 계정/화면:** `인스턴스 콘솔` / `Rocky Linux`

일반화는 이 인스턴스에만 있는 정보(DVD 저장소, 계정, cloud-init 이력, SSH 호스트 키, machine-id, 고정 IP 설정)를 지워 새 인스턴스에 그대로 복사되지 않게 하는 작업입니다. 마지막 단계에서 네트워크가 끊기므로 인스턴스 상세의 **`콘솔 > 그래픽 콘솔`에서** 진행합니다. SSH로 접속했다면 6번 `nmcli con delete`를 마지막에 실행합니다.

### 절차
1. DVD 저장소를 지우고, DVD를 마운트했다면 해제합니다.

   ```bash
   sudo rm -f /etc/yum.repos.d/dvd.repo
   if mountpoint -q /mnt; then sudo umount /mnt; fi
   ```

2. 이미지에 남기지 않을 계정을 삭제하고 root 비밀번호를 잠급니다. 설치 때 정한 root 비밀번호가 이미지로 만든 모든 인스턴스에 똑같이 남기 때문입니다. 로그인 중인 계정은 삭제되지 않으므로 다른 계정(예: `root`)으로 로그인해 진행합니다.

   ```bash
   sudo userdel -r <계정>
   sudo passwd -l root
   ```

3. cloud-init 실행 이력과 로그를 지웁니다.

   ```bash
   sudo cloud-init clean --logs --seed
   ```

4. SSH 호스트 키를 지웁니다. 새 인스턴스의 첫 부팅 때 새로 만들어집니다.

   ```bash
   sudo rm -f /etc/ssh/ssh_host_*
   ```

5. machine-id 파일을 **지우지 않고 비웁니다.**

   ```bash
   sudo truncate -s 0 /etc/machine-id
   ```

6. 설치 때 만든 고정 IP 연결 프로필을 삭제합니다. `<프로필 이름>`은 1단계에서 확인한 이름입니다.

   ```bash
   sudo nmcli con delete "<프로필 이름>"
   ```

7. 디스크에 쓰기를 마칩니다. SSH로 접속했다면 이 명령을 6번보다 먼저 실행합니다.

   ```bash
   sync
   ```

### 확인
- 명령이 오류 없이 끝납니다. `nmcli con delete` 이후에는 네트워크가 끊기는 것이 정상입니다.
- 이 단계가 끝난 뒤에는 인스턴스를 재부팅하지 않고 바로 5단계로 진행합니다.

> ⚠️ **주의:** `/etc/machine-id`는 파일을 삭제하지 말고 비웁니다. 파일을 지우면 `dbus`가 시작하지 못해 네트워크가 올라오지 않습니다.

> ⚠️ **주의:** 6번을 빠뜨리면 이 이미지로 만든 새 인스턴스가 새로 배정한 IP가 아니라 원본 IP로 뜰 수 있습니다. `nmcli con show`로 남은 프로필이 없는지 확인합니다.

> ⚠️ **주의:** 설치 때 만든 첫 사용자(UID `1000`)는 2번에서 삭제하고 이미지에 남기지 않습니다. 남겨 두면 이 이미지로 인스턴스를 만들 때 입력한 `사용자 이름`이 그 계정과 다를 경우, 첫 부팅에서 Cloud:iA가 입력한 계정을 UID `1000`으로 만들면서 남겨 둔 계정을 홈 디렉터리째 삭제합니다. `getent passwd 1000`의 출력이 비어 있는지 확인합니다.

<a id="step-5"></a>
## 5단계: Cloud:iA 웹에서 인스턴스 종료
**수행 계정/화면:** `프로젝트 계정` / `가상머신 > 인스턴스`

### 절차
1. Cloud:iA 웹에서 대상 인스턴스를 선택하고 `종료`를 클릭합니다.
2. 상태가 `종료됨`으로 바뀔 때까지 기다립니다.

### 확인
- 인스턴스 상태가 `종료됨`으로 표시되고, 1분이 지나도 다시 `실행 중`으로 바뀌지 않습니다.

> ⚠️ **주의:** 일반화한 뒤에는 게스트 안에서 `poweroff`나 `shutdown`으로 끄지 말고, 반드시 Cloud:iA 웹의 `종료`로 끕니다. 게스트 안에서 끄면 Cloud:iA가 비정상 종료로 보고 30~60초 안에 인스턴스를 다시 켭니다. 다시 켜진 첫 부팅에서 machine-id, SSH 호스트 키, cloud-init 이력이 새로 만들어져 일반화가 무효가 됩니다. 실수로 다시 켜졌다면 4단계를 처음부터 다시 진행합니다.

<a id="step-6"></a>
## 6단계: 스냅샷과 이미지 생성
**수행 계정/화면:** `프로젝트 계정` / `프로젝트 페이지`

### 절차
1. 인스턴스가 `종료됨` 상태인지 확인합니다. 스냅샷은 `종료됨` 상태에서 만듭니다.
2. 인스턴스 상세 화면의 `인스턴스 구성 요소 > 스냅샷`에서 스냅샷을 만듭니다.
3. [스냅샷 이미지 생성으로 골든 이미지 만들기 및 인스턴스 실행 — 2단계](./16-create-golden-image-from-snapshot.md#step-2)와 [3단계](./16-create-golden-image-from-snapshot.md#step-3)를 따라 스냅샷에서 이미지를 만들고 목록에서 확인합니다.
4. `스토리지 > 이미지`에서 만든 이미지를 열어 상세 정보를 확인합니다.

### 확인
- 이미지 상세에서 `cloud-init`과 `qemu-guest-agent`가 `설치됨`으로 표시됩니다. 준비하지 않은 이미지는 `cloud-init`이 `미설치`로 표시됩니다.
- 이미지 상세의 `OS 타입`은 설치에 쓴 ISO의 OS 타입(예: `Rocky Linux 9`)으로 표시됩니다.

<a id="step-7"></a>
## 7단계: 골든 이미지로 만든 인스턴스 확인
**수행 계정/화면:** `프로젝트 계정` / `가상머신 > 인스턴스`

### 절차
1. `생성`을 클릭하고 `OS 이미지`로 6단계에서 만든 이미지를 선택합니다.
2. 인스턴스 이름, `서브넷`, `IP 주소`, `보안그룹`, `사용자 이름`, `비밀번호`를 입력하고 생성한 뒤 인스턴스를 `실행`합니다.
3. 입력한 사용자 이름과 비밀번호로 로그인합니다.
4. 다음 명령으로 일반화 결과를 확인합니다.

   ```bash
   hostname
   ip a
   cat /etc/machine-id
   ls /etc/ssh/ssh_host_*
   sudo passwd -S root
   df -h /
   ```

### 확인
- 입력한 사용자 이름과 비밀번호로 로그인됩니다. 4단계에서 삭제한 설치 계정은 없습니다.
- `ip a`에 새로 배정된 IP가 표시되고, `hostname`이 인스턴스 이름으로 바뀌어 있습니다.
- `/etc/machine-id`에 새 값이 있고 `/etc/ssh/ssh_host_*` 호스트 키가 새로 만들어져 있습니다.
- `sudo passwd -S root`가 `LK`(잠김)로 표시됩니다.
- 인스턴스 상세의 `콘솔 > 직렬 콘솔`과 `콘솔 로그 다운로드`에 부팅 기록이 남습니다.

> 💡 **참고:** `디스크 크기 설정`에서 이미지보다 크게 지정해 만들면 첫 부팅에서 루트 파일 시스템이 늘어납니다. Rocky 설치 기본 분할인 LVM 루트도 Cloud:iA가 파티션, LVM 물리 볼륨·논리 볼륨, 파일 시스템 순서로 늘립니다. 2단계에서 설치한 `cloud-utils-growpart`가 필요합니다. `df -h /`로 크기를 확인하고, 늘어나지 않았다면 [인스턴스 부팅 디스크 증설하기 — 4단계](./23-grow-boot-disk.md#step-4)로 직접 늘립니다.
