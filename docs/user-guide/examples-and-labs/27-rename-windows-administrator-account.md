# Windows 인스턴스의 Administrator 계정 이름 바꾸기

이 문서는 Windows 인스턴스의 기본 관리자 계정 `Administrator`의 이름을 바꾸는 실습입니다. `Administrator`는 누구나 아는 이름이라 비밀번호 대입 공격의 첫 대상이 됩니다. 이름을 바꾸면 이런 시도를 줄일 수 있습니다.

Cloud:iA는 Windows 게스트의 계정을 만들거나 관리하지 않습니다. 인스턴스를 만들 때 입력한 `사용자 이름`·`비밀번호`도 Windows에는 적용되지 않습니다. 그래서 관리자 계정 이름은 게스트 OS 안에서 직접 바꿉니다.

## 사전 준비
- Cloud:iA 웹콘솔 접근 가능
- Windows 인스턴스가 `실행 중`이고 `그래픽 콘솔`로 접속할 수 있어야 함
- Windows 첫 설정 화면을 마쳐 `Administrator` 비밀번호가 정해져 있어야 함
- 관련 실습
  - [윈도우 가상머신 ISO 생성 및 콘솔 확인](./04-create-windows-instance-from-iso-and-open-console.md)
  - [ISO로 설치한 Windows 인스턴스를 이미지로 만들기 전 준비하기](./19-prepare-windows-instance-for-golden-image.md)

> 참고
>
> 이 문서는 첫 설정 화면에서 `Administrator` 비밀번호를 정하는 Windows Server를 기준으로 합니다. Windows 11·Windows 10은 첫 설정 화면에서 새 계정을 만들고 `Administrator` 계정은 꺼 두므로 바꿀 필요가 없습니다. 같은 방법으로 다른 로컬 계정의 이름도 바꿀 수 있습니다.

## 개요
1. [관리자 권한 PowerShell 열기](#step-1)
2. [계정 이름 바꾸기](#step-2)
3. [새 이름으로 다시 로그인](#step-3)
4. [골든 이미지로 만든 인스턴스에서 바꾸기](#step-4)

<a id="step-1"></a>
## 1단계: 관리자 권한 PowerShell 열기
**수행 계정/화면:** `Administrator` / `그래픽 콘솔`

이 문서의 명령은 모두 **PowerShell**에서 실행합니다. 명령 프롬프트(`cmd`)에서는 `Rename-LocalUser`를 찾을 수 없다는 오류가 납니다.

1. Cloud:iA 웹에서 인스턴스의 `그래픽 콘솔`을 엽니다.
2. `Administrator`로 로그인합니다. 잠금 화면에서는 그래픽 콘솔 왼쪽 도구 막대에서 `기타 키들 보이기`를 누르고 `Ctrl+Alt+Del 보내기`를 누른 뒤 비밀번호를 입력합니다.
3. `Windows 키 + R`을 눌러 `실행` 창을 열고 `powershell`을 입력한 뒤 `Ctrl+Shift+Enter`를 눌러 관리자 권한으로 엽니다. `사용자 계정 컨트롤` 창이 나타나면 `예`를 누릅니다.
4. 창 제목이 `Administrator: Windows PowerShell`(한국어 Windows는 `관리자: Windows PowerShell`)인지 확인합니다. 제목이 `Administrator:`나 `관리자:`로 시작하지 않으면 관리자 권한이 아닙니다. 이 상태에서는 2단계의 이름 바꾸기가 `액세스가 거부되었습니다`(`Access denied`) 오류로 실패하므로 창을 닫고 3번을 다시 합니다.
5. 프롬프트가 `PS C:\Users\Administrator>`처럼 `PS`로 시작하는지 확인합니다. `PS` 없이 `C:\Users\Administrator>`로 시작하면 명령 프롬프트(`cmd`)입니다. 이때는 `powershell`을 입력해 PowerShell로 바꿉니다.
6. 로컬 계정 목록을 확인합니다.

```powershell
Get-LocalUser
```

### 확인
- 목록에 `Administrator`가 있고 `Enabled`가 `True`입니다.

<a id="step-2"></a>
## 2단계: 계정 이름 바꾸기
**수행 계정/화면:** `Administrator` / 관리자 권한 **PowerShell**

아래 예시는 이름을 `cadmin`으로 바꿉니다. 원하는 이름으로 바꿔 입력합니다.

```powershell
Rename-LocalUser -Name "Administrator" -NewName "cadmin"
Get-LocalUser
```

새 이름은 다음 규칙을 따릅니다.
- 20자 이하
- `" / \ [ ] : ; | = , + * ? < > @` 문자는 쓰지 않습니다.
- 이미 있는 계정·그룹 이름이나 컴퓨터 이름과 같으면 안 됩니다.

> 참고
>
> `Rename-LocalUser`는 Windows Server 2016 이상에 들어 있습니다. Windows Server 2012·2012 R2에서는 명령을 찾을 수 없다는 오류가 나므로 아래 화면 방법을 씁니다.
>
> 명령 대신 화면에서 바꿀 수도 있습니다. `Windows 키 + R`로 `실행` 창을 열고 `lusrmgr.msc`를 입력해 `로컬 사용자 및 그룹`(`Local Users and Groups`)을 엽니다. `사용자`(`Users`)에서 `Administrator`를 마우스 오른쪽 단추로 눌러 `이름 바꾸기`(`Rename`)를 고르고 새 이름을 입력합니다.

### 확인
- 목록에 `Administrator`가 없고 새 이름(`cadmin`)이 보입니다. 설명(`Description`)은 `Built-in account for administering the computer/domain` 그대로입니다.

> 참고
>
> 이름만 바뀌고 계정 자체는 그대로입니다. 비밀번호, 관리자 권한, 바탕 화면·문서 같은 사용자 파일이 모두 유지됩니다. 사용자 폴더 경로는 `C:\Users\Administrator` 그대로 남고, PowerShell 창 제목의 `Administrator:`(한국어 Windows는 `관리자:`)도 관리자 권한으로 열렸다는 표시라 바뀌지 않습니다. 이름이 바뀌지 않은 것이 아닙니다.

<a id="step-3"></a>
## 3단계: 새 이름으로 다시 로그인
**수행 계정/화면:** 새 이름 / `그래픽 콘솔`

1. PowerShell에서 `logoff`를 입력해 로그아웃합니다.
2. 그래픽 콘솔 왼쪽 도구 막대에서 `기타 키들 보이기`를 누르고 `Ctrl+Alt+Del 보내기`를 누릅니다.
3. 로그인 화면에 새 이름(`cadmin`)이 보이면 기존 비밀번호로 로그인합니다. 다른 이름이 보이면 `다른 사용자`(`Other user`)를 고르고 새 이름을 입력합니다.
4. 1단계처럼 PowerShell을 열고 현재 계정을 확인합니다.

```powershell
whoami
```

### 확인
- `whoami` 결과가 `<컴퓨터 이름>\cadmin`입니다.
- 이제 `Administrator`로는 로그인할 수 없습니다.

> 주의
>
> [원격 데스크톱](./26-access-windows-instance-with-rdp.md)으로 접속할 때, 직렬 콘솔(EMS)의 `SAC>`에서 명령 프롬프트 채널에 로그인할 때, 스크립트나 예약 작업에 계정을 적어 둔 곳에서도 새 이름을 써야 합니다. 이름을 바꾸기 전에 `Administrator`를 쓰는 곳이 있는지 확인합니다.

<a id="step-4"></a>
## 4단계: 골든 이미지로 만든 인스턴스에서 바꾸기
**수행 계정/화면:** `Administrator` / 관리자 권한 **PowerShell**

> ⚠️ **주의:** `Sysprep`(`/generalize`)을 실행하면 관리자 계정 이름이 `Administrator`로 되돌아갑니다. 골든 이미지를 만들기 전에 이름을 바꿔 두어도 이 이미지로 만든 인스턴스에는 남지 않습니다.

골든 이미지로 만든 인스턴스는 **인스턴스마다** 아래 순서로 바꿉니다.

1. 첫 설정 화면에서 `Administrator` 비밀번호를 정합니다. 화면의 `User name`은 `Administrator`로 고정되어 있습니다. 첫 설정 순서는 [ISO로 설치한 Windows 인스턴스를 이미지로 만들기 전 준비하기 — 새 인스턴스의 첫 부팅에서 할 일](./19-prepare-windows-instance-for-golden-image.md#first-boot)을 참고합니다.
2. `Administrator`로 로그인한 뒤 [1단계](#step-1)~[3단계](#step-3)를 따라 이름을 바꿉니다.

### 확인
- 새 인스턴스에서 `Get-LocalUser` 결과에 새 이름이 보입니다.
