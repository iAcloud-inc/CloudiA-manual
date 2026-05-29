# 설치하기 (로컬 빌드 + dev_overrides)

> 본 문서는 Cloud:iA dev/test 환경 기준 예시입니다. `<your-...>` 플레이스홀더와 실제 값 매핑은 [가이드 홈의 Reference 표](../README.md#reference-table)를 참고하세요.

## 빠른 이동

1. [왜 직접 빌드해야 하나요?](#why-build)
2. [준비물](#prereqs)
3. [OpenTofu CLI 설치](#install-cli)
4. [Go 설치](#install-go)
5. [Provider 소스 받기 + 빌드](#build)
6. [dev_overrides 설정 (핵심)](#dev-overrides)
7. [CA 인증서 받기](#ca-cert)
8. [환경 변수 .env 파일](#env-file)
9. [전체 검증 — 첫 plan](#verify)
10. [자주 막히는 지점](#pitfalls)
11. [Provider 업데이트](#update-provider)

<a id="why-build"></a>
## 왜 직접 빌드해야 하나요?

Cloud:iA Terraform Provider는 아직 Terraform / OpenTofu Registry에 **게시되지 않은 상태**입니다 (2026-05 기준). 그래서 `tofu init`이 자동으로 다운로드받지 못합니다.

지금은 다음 흐름으로 사용합니다.

1. provider 소스를 GitHub에서 가져와
2. 로컬에서 빌드해서 바이너리를 만들고
3. OpenTofu/Terraform이 그 로컬 바이너리를 쓰도록 `dev_overrides`로 알려줍니다.

게시되면 이 절차는 사라지고 `tofu init` 한 번이면 끝납니다.

<a id="prereqs"></a>
## 0. 준비물

| 항목 | 최소 버전 | 확인 명령 | 설치 안내 |
|---|---|---|---|
| **Go** | 1.25 이상 | `go version` | https://go.dev/dl/ |
| **OpenTofu CLI** (권장) 또는 Terraform CLI | OpenTofu 최신 / Terraform 1.11+ | `tofu version` / `terraform version` | 아래 §1 |
| **git** | 아무거나 | `git --version` | OS 패키지 매니저 |

> Cloud:iA dev 클러스터(`<your-cloudia-endpoint>`)에 접근하려면 네트워크 접근 권한이 추가로 필요합니다. CA 인증서도 Cloud:iA 운영자에게서 받아두세요.

<a id="install-cli"></a>
## 1. OpenTofu CLI 설치

### macOS (Homebrew)

```bash
brew install opentofu
tofu version   # 출력 예: OpenTofu v1.x.x
```

### Linux (Debian/Ubuntu)

```bash
# 공식 가이드: https://opentofu.org/docs/intro/install/deb/
curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh | sudo bash -s -- --install-method deb
tofu version
```

### Windows

PowerShell (관리자):

```powershell
winget install -e --id OpenTofu.Tofu
tofu version
```

또는 Chocolatey: `choco install opentofu`.

> Terraform CLI를 이미 쓰고 계신다면 그대로 써도 됩니다. 명령어만 `tofu` → `terraform`으로 바꿔 읽으세요.

<a id="install-go"></a>
## 2. Go 설치

[https://go.dev/dl/](https://go.dev/dl/) 에서 OS에 맞는 패키지를 받아 설치한 뒤:

```bash
go version
# 출력 예: go version go1.25.x darwin/arm64

# Go가 빌드한 바이너리가 들어가는 위치 확인
go env GOPATH
# 예: /Users/<you>/go
```

`$GOPATH/bin` (예: `~/go/bin`)이 PATH에 포함돼 있으면 좋습니다. `.zshrc` 또는 `.bashrc`에 다음을 추가:

```bash
export PATH="$(go env GOPATH)/bin:$PATH"
```

<a id="build"></a>
## 3. Provider 소스 받기 + 빌드

```bash
# 1) 작업 디렉터리 만들기 (원하는 위치, 예: ~/iacloud/git/)
mkdir -p ~/iacloud/git
cd ~/iacloud/git

# 2) provider repo 클론 (저장소 URL은 Cloud:iA 운영자에게 문의 — 현재 private repo)
git clone <provider-repo-url>
cd terraform-provider-cloudia

# 3) $GOPATH/bin에 provider 바이너리 설치 (권장)
make install-dev

# 결과 확인 — 다음 경로에 바이너리가 생겼어야 합니다
ls "$(go env GOPATH)/bin/terraform-provider-cloudia"
```

> `make install-dev`는 내부적으로 `go install` 을 실행해 `$GOPATH/bin/terraform-provider-cloudia`를 만듭니다. 코드가 바뀔 때마다 다시 실행해서 바이너리를 최신으로 유지하세요.

<a id="dev-overrides"></a>
## 4. dev_overrides 설정 — 핵심 단계

OpenTofu(또는 Terraform)에게 "registry에서 받지 말고 내가 빌드한 로컬 바이너리를 써라" 라고 알려주는 설정입니다.

### macOS / Linux

`~/.terraformrc` 파일을 만듭니다 (또는 OpenTofu 전용으로 쓰려면 `~/.tofurc`).

```hcl
provider_installation {
  dev_overrides {
    "iacloud/cloudia" = "/Users/<you>/go/bin"   # ← `go env GOPATH`/bin 의 실제 경로
  }

  # dev_overrides 외 다른 provider는 정상 경로(registry)로 가져옴
  direct {}
}
```

`/Users/<you>/go/bin` 부분은 본인 `go env GOPATH`/bin 으로 실제 절대 경로를 적어야 합니다 — `~` 같은 단축 경로는 안 됩니다.

### Windows

`%APPDATA%\terraform.rc` (또는 `%APPDATA%\OpenTofu\tofurc`):

```hcl
provider_installation {
  dev_overrides {
    "iacloud/cloudia" = "C:\\Users\\<you>\\go\\bin"
  }
  direct {}
}
```

### 설정 검증

빈 디렉터리에서 간단히 확인합니다.

```bash
mkdir /tmp/cloudia-test && cd /tmp/cloudia-test
cat > main.tf <<'EOF'
terraform {
  required_providers {
    cloudia = {
      source = "iacloud/cloudia"
    }
  }
}
EOF

tofu plan
```

다음과 같이 노란 경고가 나오고 plan이 동작하면 성공입니다.

```
│ Warning: Provider development overrides are in effect
│
│ The following provider development overrides are set in the CLI configuration:
│   - iacloud/cloudia in /Users/<you>/go/bin
```

이 경고는 정상입니다 — dev_overrides가 활성화돼 있다는 알림입니다.

> ⚠️ dev_overrides가 활성화된 동안에는 `tofu init`이 의미가 없고, `terraform.lock.hcl` 파일도 만들어지지 않습니다. 그래서 처음 시도할 때 `tofu init` 단계를 **건너뛰고** 바로 `tofu plan`을 실행하면 됩니다. registry 게시 후에는 다시 `tofu init`이 필요합니다.

<a id="ca-cert"></a>
## 5. CA 인증서 받기 (dev/test 환경 사용 시)

Cloud:iA dev/test 환경은 self-signed 인증서를 씁니다. 둘 중 하나를 선택하세요.

### 옵션 A — 운영자 발급 CA를 시스템 trust store에 등록 (권장)

CA 인증서 파일(`<your-ca-bundle>`, Cloud:iA 운영자에게서 발급)을 받아둔 뒤:

**macOS:**
```bash
sudo security add-trusted-cert -d -r trustRoot \
    -k /Library/Keychains/System.keychain ~/cloudia-certs/ca-certificate.crt
```

**Linux (Debian/Ubuntu):**
```bash
sudo cp ~/cloudia-certs/ca-certificate.crt /usr/local/share/ca-certificates/cloudia-dev.crt
sudo update-ca-certificates
```

**Windows:**
파일 탐색기에서 `.crt` 파일을 더블클릭 → "인증서 설치" → "로컬 컴퓨터" → "신뢰할 수 있는 루트 인증 기관".

### 옵션 B — TLS 검증 끄기 (dev only, 비권장)

CA 등록이 번거롭다면 환경 변수 `CLOUDIA_TLS_INSECURE=true`만 켜면 됩니다. **운영 환경에서는 절대 쓰지 마세요** — MITM 공격에 그대로 노출됩니다.

<a id="env-file"></a>
## 6. 환경 변수 .env 파일 만들기

자격 증명을 매번 export하기 번거롭다면 `.env` 파일로 모아둡니다 (git에 커밋 금지).

`~/cloudia-dev.env`:

```bash
# Cloud:iA dev cluster (<your-cloudia-endpoint>) 접속용
export CLOUDIA_ENDPOINT=<your-cloudia-endpoint>
export CLOUDIA_API_BASE_PATH=/cloudia
export CLOUDIA_TLS_INSECURE=true   # CA 등록했다면 제거

# 인증 (password grant)
export CLOUDIA_AUTH_TYPE=password
export CLOUDIA_AUTH_USERNAME='<your-username>'      # 사내 Cloud:iA 계정명
export CLOUDIA_AUTH_PASSWORD='<your-password>'      # 절대 git에 올리지 말 것
export CLOUDIA_AUTH_CLIENT_ID=<your-client-id>
export CLOUDIA_AUTH_CLIENT_SECRET='<your-client-secret>'   # Cloud:iA 운영자에게 발급 요청

# (선택) 기본 project context
export CLOUDIA_PROJECT_ID='<your-project-id>'       # dev/test 예시: 25
```

사용:

```bash
source ~/cloudia-dev.env
tofu plan       # 이제 plan/apply가 정상적으로 endpoint에 붙음
```

> `.gitignore`에 `*.env`를 추가하세요. 그리고 절대 git에 커밋하지 마세요.

<a id="verify"></a>
## 7. 전체 검증 — 첫 plan 돌려보기

`/tmp/cloudia-test/main.tf`에 최소 예시를 적고 plan을 돌립니다 (실제로는 아무것도 안 만듭니다).

```hcl
terraform {
  required_providers {
    cloudia = {
      source = "iacloud/cloudia"
    }
  }
}

provider "cloudia" {
  endpoint      = "<your-cloudia-endpoint>"
  api_base_path = "/cloudia"
  tls_insecure  = true   # CA 등록했다면 제거

  auth {
    type = "password"
    # username/password 등은 환경 변수에서
  }
}

# 권한이 있는 프로젝트 ID로 변경
data "cloudia_projects" "all" {}

output "project_count" {
  value = data.cloudia_projects.all.count
}
```

```bash
tofu plan
```

성공 시 출력 예:
```
data.cloudia_projects.all: Reading...
data.cloudia_projects.all: Read complete after 1s

Changes to Outputs:
  + project_count = <known after apply>
```

여기까지 됐다면 설치 끝. [시작하기](getting-started.md)로 넘어가서 VPC와 인스턴스를 만들어 봅니다.

<a id="pitfalls"></a>
## 자주 막히는 지점

| 증상 | 원인 / 해결 |
|---|---|
| `Failed to query available provider packages` | dev_overrides 설정이 적용 안 됨. `~/.terraformrc` 경로와 절대 경로를 다시 확인 |
| `command not found: tofu` | OpenTofu CLI 설치 안 됨 또는 PATH에 없음. §1 참고 |
| `make: install-dev: No such target` | provider repo 디렉터리에서 실행했는지 확인 (`cd terraform-provider-cloudia`) |
| `go: command not found` | Go 설치 안 됨 또는 PATH에 없음. §2 참고 |
| `x509: certificate signed by unknown authority` | CA 미등록 + `TLS_INSECURE` 미설정. §5 참고 |
| `401 Unauthorized` | 환경 변수 잘못 설정. [문제 해결 §인증](troubleshooting.md#auth) 참고 |
| `connection refused` 또는 timeout | endpoint 오타 또는 VPN 미연결 |

<a id="update-provider"></a>
## 8. provider 업데이트 (소스 갱신 후)

provider 코드가 바뀌었을 때:

```bash
cd ~/iacloud/git/terraform-provider-cloudia
git pull
make install-dev   # 새 바이너리로 덮어씀
```

다음 `tofu plan`부터 새 바이너리가 자동으로 사용됩니다 (dev_overrides는 매번 그 시점의 바이너리를 읽습니다).

## 9. 다음 단계

- [인증](authentication.md) — `auth { ... }` 블록 옵션과 admin/user alias 패턴
- [시작하기](getting-started.md) — VPC → subnet → instance 까지 첫 빌드
- [문제 해결](troubleshooting.md) — 자주 보는 에러
