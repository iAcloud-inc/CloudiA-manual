# 설치하기

`cloudiactl` 은 실행 파일 하나입니다. Cloud:iA 웹 콘솔이 자기와 같은 버전의 파일을 내려주며, 관리자 권한 없이 사용자 폴더에 설치됩니다.

## 지원 환경

| 운영체제 | 아키텍처 |
|---|---|
| Linux | amd64, arm64 |
| macOS | amd64(Intel), arm64(Apple Silicon) |
| Windows | amd64, arm64 |

## 명령으로 설치 (권장)

1. Cloud:iA 웹 콘솔에 로그인합니다.
2. 오른쪽 위 계정 메뉴에서 **CLI 다운로드**를 엽니다.
3. 창의 명령 옆 **복사**를 눌러 터미널에 붙여 넣습니다.

```bash
# Linux·macOS
curl -fsSL https://<웹 콘솔 주소>/downloads/cli/install.sh | sh
```

```powershell
# Windows PowerShell
irm https://<웹 콘솔 주소>/downloads/cli/install.ps1 | iex
```

스크립트는 운영체제에 맞는 파일을 받아 체크섬을 확인한 뒤 설치합니다. 설치 폴더는 Linux·macOS 가 `~/.local/bin`, Windows 가 `%LOCALAPPDATA%\Programs\cloudiactl` 입니다. 다른 폴더에 두려면 `CLOUDIA_INSTALL_DIR` 환경 변수를 지정합니다.

- 설치 폴더가 `PATH` 에 없으면 Linux·macOS 는 셸 설정 파일에 넣을 줄을 안내합니다. Windows 는 사용자 `PATH` 에 자동으로 넣습니다. 새 터미널을 열면 `cloudiactl` 을 쓸 수 있습니다.
- 웹 콘솔이 사설 인증서를 쓰면 관리자에게 CA 인증서를 받아 `CURL_CA_BUNDLE=<CA 파일>` 을 붙여 실행하고, 첫 `curl` 에도 `--cacert <CA 파일>` 을 줍니다.
- Windows 10 은 웹 콘솔이 쓰는 TLS 1.3 을 지원하지 않아 이 명령이 연결되지 않습니다. 아래 "파일로 받기"를 씁니다.

## 파일로 받기

**CLI 다운로드** 창의 **파일로 받기**에서 운영체제에 맞는 파일과 `SHA256SUMS` 를 받습니다. 웹 콘솔이 내려주는 CLI 는 그 Cloud:iA 와 같은 버전입니다.

### 파일 확인

```bash
# Linux
sha256sum -c SHA256SUMS --ignore-missing

# macOS
shasum -a 256 -c SHA256SUMS --ignore-missing
```

Windows PowerShell 에서는 아래 값이 `SHA256SUMS` 의 같은 파일 줄과 같은지 봅니다.

```powershell
Get-FileHash .\cloudiactl-<버전>-windows-amd64.exe -Algorithm SHA256
```

### 실행해서 설치

받은 파일을 인자 없이 실행하면 설치할지 묻습니다. `Enter`(또는 `y`)를 누르면 위 설치 폴더에 `cloudiactl` 로 설치합니다.

```bash
# Linux: 먼저 실행 권한을 줍니다
chmod +x cloudiactl-<버전>-linux-amd64
./cloudiactl-<버전>-linux-amd64

# macOS: 브라우저로 받은 파일의 격리 표시를 먼저 지웁니다
xattr -d com.apple.quarantine cloudiactl-<버전>-darwin-arm64
chmod +x cloudiactl-<버전>-darwin-arm64
./cloudiactl-<버전>-darwin-arm64
```

Windows 는 받은 `.exe` 를 더블클릭합니다. 처음 실행할 때 SmartScreen 경고가 나오면 **추가 정보 → 실행**을 누릅니다.

묻지 않고 바로 설치하려면 `install` 명령을 씁니다.

```bash
./cloudiactl-<버전>-linux-amd64 install            # 기본 폴더
./cloudiactl-<버전>-linux-amd64 install --dir /opt/bin
```

## 업데이트

Cloud:iA 를 업데이트하면 웹 콘솔이 새 버전의 CLI 를 내려줍니다. CLI 는 하루에 한 번 콘솔의 버전을 확인해, 다르면 터미널에 다음 안내를 한 줄 보여 줍니다.

```text
A different cloudiactl (<버전>) is available from https://<웹 콘솔 주소>. Run: cloudiactl update
```

`cloudiactl update` 를 실행하면 콘솔과 같은 버전을 받아 체크섬을 확인한 뒤 설치된 파일을 바꿉니다. 로그인은 그대로 유지됩니다.

```bash
cloudiactl update --check   # 바꾸지 않고 콘솔 버전과 다른지만 확인
cloudiactl update           # 콘솔과 같은 버전으로 바꿈
cloudiactl version
```

- 안내는 사람이 보는 터미널에만 나옵니다. 스크립트나 AI 에이전트는 `cloudiactl update --check -o json` 의 `updateAvailable` 로 확인합니다.
- 안내를 끄려면 `CLOUDIA_NO_UPDATE_CHECK=1` 을 설정합니다.
- 설치된 파일의 폴더에 쓸 권한이 없으면(예: `sudo` 로 `/usr/local/bin` 에 둔 경우) 바꾸지 않고 `cloudiactl install` 로 사용자 폴더에 다시 설치하라고 안내합니다.
- Windows 는 업데이트 뒤 같은 폴더에 `cloudiactl.exe.old` 가 남았다가 다음 실행 때 지워집니다.

## 셸 자동 완성 (선택)

```bash
# bash (bash-completion 이 설치돼 있어야 합니다)
mkdir -p ~/.local/share/bash-completion/completions
cloudiactl completion bash > ~/.local/share/bash-completion/completions/cloudiactl

# zsh (~/.zshrc 에 autoload -U compinit; compinit 이 있어야 합니다)
mkdir -p ~/.zsh/completions
cloudiactl completion zsh > ~/.zsh/completions/_cloudiactl
# ~/.zshrc 의 compinit 앞에 다음 줄을 넣습니다: fpath=(~/.zsh/completions $fpath)
```

## 관리자: 다운로드를 내부망으로 제한하기

`/downloads/cli/` 는 로그인 없이 열립니다. 파일에 비밀은 없지만 CLI 버전으로 Cloud:iA 버전을 알 수 있습니다. 외부에 드러내지 않으려면 웹 콘솔 앞단의 방화벽이나 프록시에서 `/downloads/cli/` 경로를 내부 대역에만 허용합니다.

## 다음 단계

[로그인](./login.md)으로 Cloud:iA 에 연결합니다.
