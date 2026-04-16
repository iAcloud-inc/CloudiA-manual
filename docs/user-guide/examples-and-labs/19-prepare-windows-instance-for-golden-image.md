# ISO로 설치한 Windows 인스턴스를 골든 이미지로 준비하기

이 문서는 `ISO 파일`로 설치한 Windows 인스턴스를 골든 이미지로 사용할 수 있도록 준비하는 실습입니다. `BitLocker` 확인, `Sysprep` 적용, 이미지 생성 전 종료 상태 정리까지 설명합니다.

## 사전 준비
- Cloud:iA 웹콘솔 접근 가능
- 프로젝트 계정(`project-owner`)으로 로그인 가능
- Windows ISO로 설치한 인스턴스가 준비되어 있어야 함
- 필요하면 `virtio-win.iso`를 준비하거나 연결 가능한 환경이어야 함
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
2. `virtio-win-guest-tools`를 실행하거나 `장치 관리자`에서 `virtio-win` 드라이버를 설치합니다.
3. `장치 관리자`에서 네트워크, 스토리지 장치가 정상 인식되는지 확인합니다.
4. 필요하면 `Services`에서 `QEMU Guest Agent`가 정상 실행 중인지 확인합니다.

### 확인
- 네트워크, 스토리지 장치에 경고 표시가 없습니다.
- `QEMU Guest Agent` 서비스 상태를 확인할 수 있습니다.

<a id="step-2"></a>
## 2단계: BitLocker 상태 확인 및 복호화
**수행 계정/화면:** `인스턴스 콘솔` / `관리자 권한 CMD 또는 PowerShell`

Windows 11 템플릿 또는 골든 이미지 생성 전에는 `BitLocker` 자동 암호화 여부를 확인합니다. 암호화가 켜져 있으면 복호화가 끝날 때까지 기다린 뒤 다음 단계로 진행합니다.

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

### 절차
1. `Sysprep` 폴더로 이동합니다.
2. `Sysprep`을 실행합니다.

```cmd
cd \Windows\System32\Sysprep
sysprep.exe /generalize
```

3. `Sysprep` 이후 인스턴스를 종료합니다.
4. 스냅샷 생성 또는 이미지 캡처 전까지 인스턴스를 다시 부팅하지 않습니다.

### 확인
- `Sysprep`이 완료되었습니다.
- 인스턴스가 골든 이미지 생성 전 종료 상태로 정리되었습니다.

> 참고
>
> `/generalize`는 SID, 장치 고유 상태, 하드웨어 종속 정보를 정리합니다.

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
