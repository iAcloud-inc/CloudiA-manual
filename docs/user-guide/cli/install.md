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
3. 창의 명령 옆 복사 아이콘을 눌러 터미널에 붙여 넣습니다. 창에는 명령이 한 줄로 줄여 보이고(**펼치기**로 전체 보기), 복사 아이콘은 늘 전체 명령을 복사합니다. 명령은 손으로 입력하지 말고 창에서 복사합니다.

웹 콘솔 인증서는 Cloud:iA 가 설치할 때 만든 사설 CA 가 발급합니다. 창의 명령은 이 CA 인증서를 먼저 받아 창에 들어 있는 지문(SHA-256)과 맞춰 보고, 같을 때만 그 CA 로 나머지 파일을 검증하며 받습니다. CA 인증서를 미리 설치할 필요가 없습니다. 지문이 다르면 `cloudiactl: CA certificate fingerprint does not match` 가 나오고 설치하지 않습니다.

스크립트는 운영체제에 맞는 파일을 받아 체크섬을 확인한 뒤 설치합니다. 설치 폴더는 Linux·macOS 가 `~/.local/bin`, Windows 가 `%LOCALAPPDATA%\Programs\cloudiactl` 입니다. 다른 폴더에 두려면 `CLOUDIA_INSTALL_DIR` 환경 변수를 지정합니다.

- 설치가 끝나면 마지막에 `Next steps:` 아래 번호를 붙여 할 일을 모아 보여 줍니다. 위에서부터 차례로 합니다.
- 설치 폴더가 `PATH` 에 없으면 Linux·macOS 는 셸 설정 파일에 넣을 줄을 안내합니다. Windows 는 사용자 `PATH` 에 자동으로 넣습니다. 새 터미널을 열면 `cloudiactl` 을 쓸 수 있습니다.
- 설치하면서 웹 콘솔 주소와 CA 인증서를 cloudiactl 설정에 남깁니다. 이어서 `cloudiactl login` 만 실행하면 됩니다. 지금 쓰는 프로필이 다른 웹 콘솔을 가리키면(다른 Cloud:iA 에서 다시 받아 설치한 경우) 이 웹 콘솔용 프로필로 바꿉니다.
  - 이 웹 콘솔 주소를 가진 프로필이 이미 있으면 그 프로필을, 없으면 웹 콘솔 주소(예: `console.example`)를 이름으로 새 프로필을 만들어 현재 프로필로 씁니다.
  - 원래 프로필과 그 로그인은 그대로 남습니다. 돌아가려면 `cloudiactl config use <원래 프로필>` 을 실행합니다.
  - 프로필을 바꾸지 않으려면 `--keep-profile`(또는 `CLOUDIA_KEEP_PROFILE=1`)로 설치합니다. `--profile`·`CLOUDIA_PROFILE` 로 프로필을 직접 고른 경우에도 바꾸지 않습니다. 이때는 이 웹 콘솔에 로그인할 명령만 안내합니다.
- 이미 설치돼 있어도 같은 명령을 다시 실행하면 됩니다. 웹 콘솔이 내주는 버전으로 덮어써 설치하고(재설치·업데이트), 로그인 정보는 그대로 둡니다.
- Linux·macOS 명령은 `curl` 과 `openssl` 이 필요합니다. 셸 종류(bash·zsh·fish 등)와 상관없이 붙여 넣으면 됩니다.
- Windows 명령은 `curl.exe` 8 이상이 필요합니다. 최신 업데이트를 받은 Windows 11·Server 2022 이상이 해당합니다. `curl.exe --version` 으로 확인하고, 안 되면 아래 "파일로 받기"를 씁니다.
- Windows 10 은 웹 콘솔이 쓰는 TLS 1.3 을 지원하지 않아 이 명령이 연결되지 않습니다. 아래 "파일로 받기"를 씁니다.

## 파일로 받기

명령을 쓸 수 없을 때(인터넷이 막힌 PC로 옮겨 설치하는 경우 등) 씁니다. **CLI 다운로드** 창의 **파일로 받기**에서 운영체제와 칩 종류에 맞는 파일(예: macOS (Apple Silicon))을 고르면 그 파일의 설치 단계가 나옵니다. 단계의 명령은 고른 파일 이름으로 채워져 있으니 옆 복사 아이콘으로 복사해 씁니다. 웹 콘솔이 내려주는 CLI 는 그 Cloud:iA 와 같은 버전입니다.

실행 파일에는 아직 운영체제의 코드 서명이 없습니다. 그래서 브라우저로 받은 파일을 그대로 실행하면 macOS 는 Gatekeeper 가 실행을 막고, Windows 는 탐색기에서 열 때 SmartScreen 경고가 나옵니다. 위의 명령으로 설치하면 브라우저를 거치지 않아 이런 경고가 없으므로, 명령을 쓸 수 있는 PC 에서는 명령으로 설치합니다. 파일로 받을 때는 아래 단계를 그대로 따릅니다.

1. 실행 파일, `SHA256SUMS`, CA 인증서(`cloudia-ca.crt`)를 받습니다. CA 인증서는 웹 콘솔이 사설 CA 를 쓸 때만 보입니다. 다운로드 폴더에 같은 이름의 옛 파일이 있으면 먼저 지웁니다(남아 있으면 브라우저가 새 파일 이름에 `(1)` 을 붙여 명령이 옛 파일을 씁니다).
2. 터미널에서 파일을 받은 폴더로 이동합니다. 파일이 손상되지 않았는지 확인하는 단계는 선택입니다. 명령으로 설치하면 체크섬을 자동으로 확인하고, 파일로 받을 때는 다운로드가 끊겨 파일이 깨졌는지 보는 용도입니다. BusyBox 를 쓰는 시스템(Alpine 등)은 `sha256sum` 에 `--ignore-missing` 이 없으므로 건너뜁니다.
3. 실행할 수 있게 준비하고, `install --endpoint <웹 콘솔 주소> --ca-bundle cloudia-ca.crt` 로 설치합니다. 웹 콘솔 주소와 CA 가 설정에 남아 이어서 `cloudiactl login` 만 실행하면 됩니다. 웹 콘솔이 공인 인증서를 써서 창에 CA 인증서 버튼이 없으면 `--ca-bundle cloudia-ca.crt` 를 빼고 실행합니다(창의 명령은 이미 맞춰져 있습니다).

```bash
# macOS (Apple Silicon 예)
cd ~/Downloads
shasum -a 256 -c SHA256SUMS --ignore-missing   # (선택) 파일 손상 확인
xattr -c cloudiactl-<버전>-darwin-arm64   # 브라우저가 붙인 격리 표시를 지운다. 지우지 않으면 macOS 가 실행을 막는다
chmod +x cloudiactl-<버전>-darwin-arm64
./cloudiactl-<버전>-darwin-arm64 install --endpoint https://<웹 콘솔 주소> --ca-bundle cloudia-ca.crt
cloudiactl login

# Linux (x86_64 예)
cd ~/Downloads
sha256sum -c SHA256SUMS --ignore-missing   # (선택) 파일 손상 확인. BusyBox(Alpine 등)는 건너뛴다
chmod +x cloudiactl-<버전>-linux-amd64
./cloudiactl-<버전>-linux-amd64 install --endpoint https://<웹 콘솔 주소> --ca-bundle cloudia-ca.crt
cloudiactl login
```

```powershell
# Windows PowerShell (x64 예)
cd "$env:USERPROFILE\Downloads"
if ((Get-FileHash .\cloudiactl-<버전>-windows-amd64.exe -Algorithm SHA256).Hash -eq ((Select-String -Path SHA256SUMS -SimpleMatch 'cloudiactl-<버전>-windows-amd64.exe').Line -split '\s+')[0]) { 'OK' } else { 'MISMATCH' }   # (선택) 파일 손상 확인
.\cloudiactl-<버전>-windows-amd64.exe install --endpoint https://<웹 콘솔 주소> --ca-bundle cloudia-ca.crt
# 새 PowerShell 창에서
cloudiactl login
```

- Windows 는 PowerShell 에서 실행하므로 탐색기에서 더블클릭할 때 나오는 SmartScreen 경고를 거치지 않습니다.
- macOS 에서 `xattr` 대신 실행이 막혔을 때 시스템 설정 > 개인정보 보호 및 보안에서 **그래도 열기**를 눌러도 됩니다.
- 다른 폴더에 설치하려면 `install` 에 `--dir <폴더>` 를 붙입니다.

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

## 셸 자동 완성

`cloudiactl install` 이 지금 쓰는 셸을 보고 Tab 자동 완성 파일도 함께 설치합니다. zsh 는 `~/.zshrc` 에 두 줄을 붙여 자동 완성을 켭니다. bash·fish 는 셸 설정 파일을 고치지 않습니다. 하위 명령과 옵션이 완성됩니다(예: `cloudiactl inst` Tab Tab → `install`·`instance`·`instance-snapshot`·`instance-type`(서버에 따라 `instance-cdrom` 도), `cloudiactl instance` Tab Tab → `create`·`list`·`start` …).

| 셸 | 설치 위치 | 할 일 |
|---|---|---|
| bash | `~/.local/share/bash-completion/completions/cloudiactl` | 새 터미널을 엽니다. bash 4.2 이상과 `bash-completion` 2.x 가 있어야 합니다. macOS 기본 bash(3.2)에서는 동작하지 않으므로 `brew install bash bash-completion@2` 뒤에 씁니다 |
| zsh | `~/.local/share/zsh/site-functions/_cloudiactl` | 새 터미널을 열거나 `exec zsh` 를 실행합니다. 설치가 `~/.zshrc` 에 등록해 둡니다 |
| fish | `~/.config/fish/completions/cloudiactl.fish` | 새 터미널을 엽니다 |

zsh 는 설치가 `~/.zshrc`(`ZDOTDIR` 을 설정했으면 그 폴더의 `.zshrc`) 끝에 다음 두 줄을 붙입니다. 폴더는 실제 경로입니다. 다시 설치해도 같은 줄이 있으면 더 붙이지 않습니다. `.zshrc` 가 심볼릭 링크면 링크가 가리키는 파일에 붙습니다.

```bash
# cloudiactl Tab completion (added by cloudiactl install; delete these two lines to undo)
fpath=("/Users/<사용자>/.local/share/zsh/site-functions" $fpath); autoload -Uz compinit && compinit
```

- 되돌리려면 이 두 줄을 지웁니다. 다시 설치하면 다시 붙으므로, 계속 끄려면 아래처럼 고치지 않는 설치를 씁니다.
- 이미 다른 방법(oh-my-zsh 등)으로 자동 완성을 켰다면 고치지 않는 설치를 써도 됩니다.
- `.zshrc` 를 고치지 않으려면 `cloudiactl install --no-shell-config` 로 설치하거나, 웹 콘솔에서 복사한 명령 맨 앞에 `CLOUDIA_NO_SHELL_CONFIG=1 ` 을 붙여 실행합니다(예: `CLOUDIA_NO_SHELL_CONFIG=1 sh -c '…'`). 그러면 붙일 줄을 `Next steps:` 에 안내만 합니다.
- `.zshrc` 에 쓰지 못하면 `warning:` 한 줄과 함께 붙일 명령을 안내하고 설치는 그대로 끝납니다.

- `XDG_DATA_HOME`·`XDG_CONFIG_HOME` 을 설정했으면 그 폴더를 씁니다.
- 자동 완성 파일을 쓰지 못해도 설치는 끝나고 `warning:` 한 줄만 나옵니다.
- Windows PowerShell 은 `cloudiactl completion powershell --help` 의 안내대로 프로필에 등록합니다.
- 리소스 이름·ID(`cloudiactl instance get` 뒤의 인스턴스 이름)는 아직 완성되지 않습니다.

## 관리자: 다운로드를 내부망으로 제한하기

`/downloads/cli/` 는 로그인 없이 열립니다. 파일에 비밀은 없지만 CLI 버전으로 Cloud:iA 버전을 알 수 있습니다. 외부에 드러내지 않으려면 웹 콘솔 앞단의 방화벽이나 프록시에서 `/downloads/cli/` 경로를 내부 대역에만 허용합니다.

## 다음 단계

[로그인](./login.md)으로 Cloud:iA 에 연결합니다.
