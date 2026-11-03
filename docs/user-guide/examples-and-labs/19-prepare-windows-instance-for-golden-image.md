# ISO로 설치한 Windows 인스턴스를 골든 이미지로 준비하기

이 문서는 `ISO 파일`로 설치한 Windows 인스턴스를 골든 이미지로 사용할 수 있도록 준비하는 실습입니다. `BitLocker` 확인, `Sysprep` 적용, 이미지 생성 전 종료 상태 정리까지 설명합니다.

## 사전 준비
- Cloud:iA 웹콘솔 접근 가능
- 프로젝트 계정(`project-owner`)으로 로그인 가능
- Windows ISO로 설치한 인스턴스가 준비되어 있어야 함
- Windows VM에서는 `virtio-win.iso`가 CloudiA에 의해 자동으로 바인드됨
- 관련 실습을 먼저 확인하면 진행이 쉬움
  - [윈도우 가상머신 ISO 생성 및 콘솔 확인](./04-create-windows-instance-from-iso-and-open-console.md)
  - [스냅샷 이미지 생성으로 골든 이미지 만들기 및 인스턴스 실행](./16-create-golden-image-from-snapshot.md)

## 개요
1. [VirtIO 드라이버와 Guest Agent 확인](#step-1)
2. [BitLocker 상태 확인 및 복호화](#step-2)
3. [Sysprep 적용 후 종료 준비](#step-3)
4. [스냅샷과 이미지 생성으로 이어가기](#step-4)

<a id="step-1"></a>
## 1단계: VirtIO 드라이버와 Guest Agent 확인
**수행 계정/화면:** `인스턴스 콘솔` / `Windows`

### 절차
1. Windows에 로그인합니다.
2. 드라이버 CD(`virtio-win`)에 있는 `virtio-win-guest-tools`를 실행합니다. `장치 관리자`에서 드라이버를 하나씩 설치하는 방법보다 권장합니다. 네트워크, 저장소(SCSI 포함), `Balloon`, `Serial` 드라이버와 `QEMU Guest Agent`가 한 번에 설치되며, 이미지로 만든 인스턴스가 부팅하는 데 필요한 저장소 드라이버가 함께 설치됩니다.
3. `장치 관리자`에서 네트워크, 스토리지 장치가 정상 인식되는지 확인합니다.
4. 필요하면 `Services`에서 `QEMU Guest Agent`가 정상 실행 중인지 확인합니다.

### 확인
- 네트워크, 스토리지 장치에 경고 표시가 없습니다.
- `QEMU Guest Agent` 서비스 상태를 확인할 수 있습니다.

> 주의
>
> 골든 이미지로 만들기 전에 반드시 `virtio-win-guest-tools`를 설치합니다. 설치하지 않은 채 만든 이미지로 인스턴스를 만들면 부팅하지 못할 수 있습니다.

<a id="step-2"></a>
## 2단계: BitLocker 상태 확인 및 복호화
**수행 계정/화면:** `인스턴스 콘솔` / `관리자 권한 CMD 또는 PowerShell`

Windows 11 템플릿 또는 골든 이미지 생성 전에는 `BitLocker` 자동 암호화 여부를 확인합니다. 암호화가 켜져 있으면 복호화가 끝날 때까지 기다린 뒤 다음 단계로 진행합니다.

> 참고
>
> 이 단계는 Windows 11 같은 클라이언트 OS 대상입니다. Windows Server는 BitLocker 기능이 기본으로 설치되어 있지 않으므로, 기능을 직접 설치하지 않았다면 이 단계를 건너뜁니다.

### 절차
1. 관리자 권한으로 명령 프롬프트 또는 PowerShell을 엽니다.
2. `BitLocker` 상태를 확인합니다.

```cmd
manage-bde -status C:
```

3. 장치 암호화 자동 적용을 방지합니다.

```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Control\BitLocker" /v PreventDeviceEncryption /t REG_DWORD /d 1 /f
```

4. OS 디스크에 `BitLocker`가 사용 중이면 복호화를 시작합니다.

```cmd
manage-bde -off C:
```

5. 데이터 디스크가 암호화되어 있으면 같은 방식으로 복호화를 시작합니다.

```cmd
manage-bde -off D:
manage-bde -off E:
```

6. 각 디스크의 복호화가 완료될 때까지 상태를 반복 확인합니다.

```cmd
manage-bde -status C:
manage-bde -status D:
manage-bde -status E:
```

### 확인
- `BitLocker` 보호가 해제되었습니다.
- 암호화 비율이 `0%`인지 확인했습니다.

> 주의
>
> `manage-bde -off`는 보호를 일시 중지하는 것이 아니라 실제 복호화를 시작합니다. 복호화가 끝나기 전에는 스냅샷 생성 또는 이미지 캡처를 진행하지 않습니다.

<a id="step-3"></a>
## 3단계: Sysprep 적용 후 종료 준비
**수행 계정/화면:** `인스턴스 콘솔` / `관리자 권한 CMD`

> 참고
>
> 이 이미지로 만든 인스턴스에서 직렬 콘솔을 쓰려면 Sysprep 전에 EMS를 켜 둡니다. EMS 설정은 Sysprep을 거쳐도 유지되어, 이 이미지로 만든 인스턴스의 `직렬 콘솔`에 `SAC>`가 나타납니다. 방법은 [윈도우 가상머신 ISO 생성 및 콘솔 확인 — 5단계](./04-create-windows-instance-from-iso-and-open-console.md#step-5)를 참고하세요.

### 절차
1. `Sysprep` 폴더로 이동합니다.
2. `Sysprep`을 실행합니다.

```cmd
cd \Windows\System32\Sysprep
sysprep.exe /generalize /oobe /quit
```

`/quit`은 `Sysprep`이 끝난 뒤에도 Windows를 켜 둔 채로 둡니다. 보통 1~2분 안에 끝납니다.

3. `Sysprep`은 성공하면 `C:\Windows\System32\Sysprep\Sysprep_succeeded.tag` 파일을 만듭니다. 이 파일이 생기면 끝난 것입니다. `C:\Windows\System32\Sysprep\Panther\setupact.log` 끝에도 `Successfully created tag file` 기록이 남습니다.
4. Cloud:iA 웹에서 인스턴스를 `종료`합니다.
5. 스냅샷 생성 또는 이미지 캡처 전까지 인스턴스를 다시 켜지 않습니다.

### 확인
- `Sysprep`이 완료되었습니다.
- 인스턴스가 골든 이미지 생성 전 종료 상태로 정리되었습니다. 상태가 `종료됨`이고 다시 `실행 중`으로 바뀌지 않습니다.

> 주의
>
> `Sysprep`을 `/shutdown`이나 `/reboot` 옵션으로 실행하거나, `Sysprep` 창의 기본값 `다시 시작`을 쓰지 않습니다. Windows 안에서 꺼지면 Cloud:iA가 비정상 종료로 보고 30~60초 안에 인스턴스를 다시 켭니다. 다시 켜지는 순간 Windows가 첫 부팅 설정을 진행해 일반화 상태가 사라집니다. 반드시 `/quit`으로 마치고 Cloud:iA 웹의 `종료`로 끕니다. 실수로 켜졌다면 `Sysprep`을 다시 실행합니다. 스냅샷은 인스턴스를 다시 켜기 전에 만듭니다.

> 참고
>
> `/generalize`는 SID, 장치 고유 상태, 하드웨어 종속 정보를 정리합니다. 이때 네트워크 어댑터에 입력한 고정 IP도 지워집니다. `/oobe`는 새 인스턴스의 첫 부팅에서 Windows 첫 설정 화면이 나오게 합니다.

<a id="step-4"></a>
## 4단계: 스냅샷과 이미지 생성으로 이어가기
**수행 계정/화면:** `프로젝트 계정` / `프로젝트 페이지`

Windows 인스턴스를 복제 가능한 상태로 준비했다면, 다음 문서로 이어서 스냅샷과 이미지를 생성합니다.

- [스냅샷 이미지 생성으로 골든 이미지 만들기 및 인스턴스 실행](./16-create-golden-image-from-snapshot.md)

### 권장 순서
1. 인스턴스가 `종료됨` 상태인지 확인합니다.
2. 필요하면 인스턴스 스냅샷을 생성합니다.
3. 스냅샷에서 이미지를 생성합니다.
4. 생성한 이미지를 `OS 이미지`로 선택해 새 인스턴스를 생성합니다.

### 이미지 확인
이미지를 만든 뒤 `스토리지 > 이미지`의 이미지 상세에 다음과 같이 표시됩니다. 실패가 아닙니다.

| 항목 | 표시 | 설명 |
|---|---|---|
| `OS 타입` | 설치에 쓴 ISO의 OS (예: `Windows Server 2022`) | 원본 인스턴스의 OS 타입을 따릅니다. 이 이미지로 만든 인스턴스는 Windows용 장치 구성으로 만들어집니다. |
| `cloud-init`, `qemu-guest-agent` | `미확인` | 이 판별은 Linux 이미지에서만 합니다. |

### 새 인스턴스의 첫 부팅에서 할 일
이 이미지로 만든 인스턴스를 처음 실행하면 그래픽 콘솔에 Windows 첫 설정 화면이 나타납니다. Windows Server는 지역·언어·키보드 → 라이선스 → `Administrator` 비밀번호 순서입니다. Windows 11은 `Administrator` 대신 새 계정을 만드는 화면이 나오며, 네트워크 연결을 요구하면 [Windows 11 네트워크 연결 요구 사항 우회](./04-create-windows-instance-from-iso-and-open-console.md#step-3)를 따릅니다. 컴퓨터 이름은 새로 정해집니다. EMS(직렬 콘솔) 설정은 `Sysprep` 뒤에도 남아 있습니다.

| 할 일 | 방법 |
|---|---|
| 관리자 계정 설정 | 첫 설정 화면에서 정합니다(Windows Server는 `Administrator` 비밀번호, Windows 11은 새 계정). 인스턴스를 만들 때 `사용자 이름`·`비밀번호`를 입력했더라도 Windows에는 적용되지 않습니다. |
| IP 주소 직접 입력 | 새 인스턴스는 IP가 비어 있습니다(`169.254`로 시작하는 자동 주소). `Sysprep`이 고정 IP를 지우므로 **인스턴스마다** 배정 IP, 서브넷의 게이트웨이와 DNS를 직접 입력합니다. 방법은 [VirtIO 드라이버 설치와 IP 직접 입력](./04-create-windows-instance-from-iso-and-open-console.md#step-4)을 참고합니다. EMS를 켜 두었다면 직렬 콘솔의 `SAC>`에서도 입력할 수 있습니다([직렬 콘솔(EMS) 사용 설정](./04-create-windows-instance-from-iso-and-open-console.md#step-5) 참고). |
| `C:` 드라이브 확장 | 디스크 크기를 이미지보다 크게 지정해도 `C:` 드라이브는 자동으로 늘어나지 않습니다. [인스턴스 부팅 디스크 증설하기 — 5단계](./22-grow-boot-disk.md#step-5)의 Windows 수동 확장(`diskmgmt.msc`의 `볼륨 확장`)을 따릅니다. |

> 주의
>
> IP를 입력하기 전에는 새 인스턴스에 네트워크로 접속할 수 없습니다. 그래픽 콘솔로 접속해 먼저 IP를 입력합니다.
