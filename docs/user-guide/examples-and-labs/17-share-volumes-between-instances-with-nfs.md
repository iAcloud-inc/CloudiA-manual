# 파일 시스템으로 인스턴스 간 공유 볼륨 구성

이 문서는 `NFS` 파일 시스템을 만들고 인스턴스 2대에 마운트해 공유 데이터를 확인하는 실습입니다. 게스트 OS에 `NFS` 클라이언트 패키지가 없으면 자동 마운트가 완료되지 않을 수 있으므로, 패키지 설치와 `/etc/fstab` 적용 절차도 함께 설명합니다.

## 사전 준비
- Cloud:iA 웹콘솔 접근 가능
- 프로젝트 계정(`project-owner`)으로 로그인 가능
- Linux 인스턴스 2대의 상태가 `종료됨`
- NFS 포트(2049) 인바운드 허용 보안그룹 준비

## 개요
1. [NFS 파일 시스템 생성](#step-1)
2. [인스턴스에 NFS 연결](#step-2)
3. [게스트 OS에 NFS 패키지 설치 및 fstab 적용](#step-3)
4. [공유 데이터와 마운트 상태 확인](#step-4)

<a id="step-1"></a>
## 1단계: NFS 파일 시스템 생성
**수행 계정/화면:** `프로젝트 계정` / `프로젝트 페이지`

### 절차
1. `스토리지 > 파일 시스템`에서 `생성`을 클릭합니다.
2. 이름, 타입 `NFS`, 크기를 입력합니다.
3. VPC/서브넷/보안그룹/IP 주소를 설정합니다.
4. `생성`을 클릭합니다.

### 입력 예시
| 항목 | 값 |
|---|---|
| 이름 | `example-fs-nfs-001` |
| 타입 | `NFS` |
| 크기 | `20 GiB` |
| 스토리지 도메인 | `NFS-SD` |
| VPC | `example-vpc` |
| 서브넷 | `example-subnet-001` |
| IP 주소 | `자동 할당` |
| 보안그룹 | `example-sg-nfs` |

### 확인
- 파일 시스템 목록에 `example-fs-nfs-001`이 표시됩니다.
- 상세에서 NFS 네트워크 정보가 확인됩니다.

<a id="step-2"></a>
## 2단계: 인스턴스에 NFS 연결
**수행 계정/화면:** `프로젝트 계정` / `프로젝트 페이지`

### 절차
1. 종료된 `example-vm-nfs-01`, `example-vm-nfs-02` 인스턴스 편집으로 이동합니다.
2. `고급 설정 > 스토리지 추가 > 파일 시스템`에서 NFS를 추가합니다.
3. 각 인스턴스에 마운트 경로를 지정하고 저장합니다.
4. 각 인스턴스를 실행합니다. 

### 입력 예시
| 항목 | 값 |
|---|---|
| 파일 시스템 | `example-fs-nfs-001` |
| 인스턴스1 마운트 경로 | `/mnt/shared-nfs` |
| 인스턴스2 마운트 경로 | `/mnt/shared-nfs` |

### 확인
- 인스턴스 상세 `연결된 리소스 > 파일 시스템`에 NFS가 표시됩니다.

<a id="step-3"></a>
## 3단계: 게스트 OS에 NFS 패키지 설치 및 fstab 적용
**수행 계정/화면:** `인스턴스 콘솔(2대)` / `터미널`

> 중요
>
> Cloud:iA가 파일 시스템 연결 정보를 `/etc/fstab`에 기록해도, 게스트 OS에 `NFS` 클라이언트 패키지가 없으면 자동 마운트가 완료되지 않을 수 있습니다. 이 경우 패키지를 설치한 뒤 `mount -a`로 기존 `fstab` 항목을 적용합니다.

### 절차
1. 각 인스턴스에서 `/etc/fstab`에 NFS 마운트 경로가 기록되어 있는지 확인합니다.
2. 각 인스턴스의 Linux 배포판에 맞는 `NFS` 클라이언트 패키지를 설치합니다.
3. `mount -a`를 실행해 `/etc/fstab`의 기존 NFS 항목을 적용합니다.
4. `findmnt`, `mount`, `df -hT`로 마운트 상태를 확인합니다.

### 배포판별 패키지 설치 명령
| 게스트 OS | 확인 명령 | 설치 명령 |
|---|---|---|
| Rocky Linux / RHEL 계열 | `rpm -q nfs-utils` | `sudo dnf install -y nfs-utils` |
| Ubuntu | `dpkg -l nfs-common` | `sudo apt-get update && sudo apt-get install -y nfs-common` |

### 적용 예시
`Rocky Linux` 또는 `RHEL` 계열:

```bash
grep '/mnt/shared-nfs' /etc/fstab
rpm -q nfs-utils || sudo dnf install -y nfs-utils
sudo mount -a
findmnt /mnt/shared-nfs
mount | grep /mnt/shared-nfs
df -hT | grep shared-nfs
```

`Ubuntu`:

```bash
grep '/mnt/shared-nfs' /etc/fstab
dpkg -l nfs-common || true
sudo apt-get update
sudo apt-get install -y nfs-common
sudo mount -a
findmnt /mnt/shared-nfs
mount | grep /mnt/shared-nfs
df -hT | grep shared-nfs
```

### 확인
- `/etc/fstab`에 NFS 마운트 경로가 기록되어 있습니다.
- `findmnt /mnt/shared-nfs` 결과가 표시됩니다.
- `df -hT` 결과에 NFS 파일 시스템이 보입니다.

<a id="step-4"></a>
## 4단계: 공유 데이터와 마운트 상태 확인
**수행 계정/화면:** `인스턴스 콘솔(2대)` / `터미널`

### 절차
1. 인스턴스1에서 테스트 파일을 생성합니다.
2. 인스턴스2에서 동일 경로의 파일을 확인합니다.
3. 두 인스턴스에서 `df -hT` 출력으로 동일 NFS 마운트 정보를 다시 확인합니다.

### 입력 예시
| 항목 | 값                                                                              |
|---|--------------------------------------------------------------------------------|
| 인스턴스1 파일 생성 | `echo "hello nfs" \| sudo tee /mnt/shared-nfs/example.txt`                     |
| 인스턴스2 파일 확인 | `cat /mnt/shared-nfs/example.txt`                                              |
| 용량 확인 | `df -hT \| grep shared-nfs` |

### 확인
- 인스턴스2에서 인스턴스1이 만든 파일이 조회됩니다.
- `df -hT`에 동일 NFS 마운트가 표시됩니다.

> 참고
>
> `mount -a` 이후에도 마운트가 되지 않으면 다음 항목을 함께 확인합니다.
>
> - 파일 시스템 보안그룹에서 `2049/tcp`가 허용되는지
> - 인스턴스와 파일 시스템이 같은 VPC 또는 통신 가능한 네트워크에 있는지
> - 인스턴스 상세의 `연결된 리소스 > 파일 시스템`에 NFS가 정상 표시되는지
