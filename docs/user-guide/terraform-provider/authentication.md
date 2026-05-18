# 인증 (Authentication)

> 영문 SSOT: `terraform-provider-cloudia/docs/guides/authentication.md`. 본 한국어 본은 그 sibling이며, 차이가 있을 경우 영문판이 우선합니다.
>
> 본 문서의 예시는 Cloud:iA dev/test 환경 기준입니다. `<your-...>` 플레이스홀더와 실제 값 매핑은 [가이드 홈의 Reference 표](README.md#reference-table)를 참고하세요.

Cloud:iA provider는 중첩된 `auth { ... }` 블록을 통해 OAuth2로 인증합니다. 두 가지 grant flow를 지원합니다.

- `type = "password"` (기본값) — Resource Owner Password Grant. 사람 운영자가 직접 쓸 때 사용. `username` / `password` / `client_id` / `client_secret` 모두 필요.
- `type = "client_credentials"` — 자동화/CI에서 쓰는 service account 토큰. `client_id` / `client_secret`만 필요.

토큰은 provider 내부 `TokenSource`가 관리합니다 (access token을 refresh skew와 함께 캐시하며, `refresh_token`이나 어떤 secret도 state에 절대 저장되지 않습니다).

## 필수 환경 변수

모든 `auth.*` 속성은 환경 변수로 대체 가능합니다 (HCL 값이 우선). credential은 반드시 secret manager에서 주입하고, provider HCL에 평문으로 적지 마세요.

| 환경 변수 | 설명 |
|---|---|
| `CLOUDIA_ENDPOINT` | Cloud:iA API base URL (예: `<your-endpoint>`) |
| `CLOUDIA_AUTH_TYPE` | `password` (기본값) 또는 `client_credentials` |
| `CLOUDIA_AUTH_USERNAME` | 로그인 사용자명 (`type = "password"`일 때 필수) |
| `CLOUDIA_AUTH_PASSWORD` | 로그인 비밀번호 (민감 정보, `type = "password"`일 때 필수) |
| `CLOUDIA_AUTH_CLIENT_ID` | OAuth2 client ID — `password`일 때는 login client, `client_credentials`일 때는 service-account client |
| `CLOUDIA_AUTH_CLIENT_SECRET` | OAuth2 client secret (민감 정보) |

<a id="optional-env-vars"></a>
## 선택 환경 변수

| 환경 변수 | 기본값 | 설명 |
|---|---|---|
| `CLOUDIA_API_BASE_PATH` | `""` | API base path prefix (예: `<your-api-base-path>` — dev/test는 `/cloudia`) |
| `CLOUDIA_PROJECT_ID` | (없음) | provider 기본 project context. 리소스에서 `project_id`를 명시하지 않을 때 fallback으로 사용 |
| `CLOUDIA_POLL_INTERVAL_SECONDS` | `5` | 비동기 `requestId` 응답에 대한 polling 주기 |
| `CLOUDIA_POLL_TIMEOUT_SECONDS` | `600` | 비동기 `requestId` 응답에 대한 polling timeout |
| `CLOUDIA_TLS_INSECURE` | `false` | TLS 인증서 검증 skip. **dev 전용**, 운영에서는 사용 금지 |

<a id="dev-env-example"></a>
## Cloud:iA dev/test 환경용 .env 예시

아래 예시는 dev/test (<your-cloudia-endpoint>) 환경 기준입니다. 민감 정보 자리는 `<your-...>` 플레이스홀더로 두었습니다 — 실제 값은 secret manager / 1Password / Cloud:iA 운영자에게서 가져와 채우세요. `.env` 파일은 git에 절대 커밋하지 마세요.

```bash
# Connection (dev/test cluster)
export CLOUDIA_ENDPOINT=<your-cloudia-endpoint>
export CLOUDIA_API_BASE_PATH=/cloudia
export CLOUDIA_TLS_INSECURE=true   # dev only. 운영에서는 제거하고 CA를 trust store에 등록

# Auth (password grant)
export CLOUDIA_AUTH_TYPE=password
export CLOUDIA_AUTH_USERNAME='<your-username>'
export CLOUDIA_AUTH_PASSWORD='<your-password>'
export CLOUDIA_AUTH_CLIENT_ID=<your-client-id>
export CLOUDIA_AUTH_CLIENT_SECRET='<your-client-secret>'

# (선택) 기본 project context
export CLOUDIA_PROJECT_ID='<your-project-id>'   # dev/test 예시: 25
```

운영 클러스터로 옮길 때 바뀌는 값:
- `CLOUDIA_ENDPOINT` — 운영 endpoint로 변경
- `CLOUDIA_API_BASE_PATH` — 운영 설치본이 root에 있으면 제거(또는 빈 문자열)
- `CLOUDIA_TLS_INSECURE` — **반드시 제거** + CA를 시스템 trust store에 등록 (자세한 절차: [문제 해결 §TLS](troubleshooting.md#tls))
- `CLOUDIA_AUTH_CLIENT_ID` — 클러스터마다 별도 발급될 수 있음. 운영자에게 확인

<a id="admin-user-alias"></a>
## Admin vs User alias 패턴

권장하는 운영 패턴은 `alias`로 두 개의 provider 인스턴스를 나누어, 관리 작업(project create/delete)과 일반 작업(project-scoped 리소스 CRUD)을 권한 경계에 따라 분리하는 것입니다.

```hcl
terraform {
  required_providers {
    cloudia = {
      source = "iacloud/cloudia"
    }
  }
}

variable "cloudia_endpoint"   { type = string }   # 예: <your-cloudia-endpoint>
variable "cloudia_base_path"  { type = string  default = "" }
variable "cloudia_tls_insecure" { type = bool  default = false }

# 관리자: project 생성/삭제용
provider "cloudia" {
  alias         = "admin"
  endpoint      = var.cloudia_endpoint
  api_base_path = var.cloudia_base_path
  tls_insecure  = var.cloudia_tls_insecure

  auth {
    type = "password"
    # username/password는 CLOUDIA_AUTH_USERNAME/_PASSWORD에서 가져옴
  }
}

# 일반 사용자: project-scoped 리소스용. project_id는 admin output을 참조.
provider "cloudia" {
  alias         = "user"
  endpoint      = var.cloudia_endpoint
  api_base_path = var.cloudia_base_path
  tls_insecure  = var.cloudia_tls_insecure
  project_id    = cloudia_project.app.id

  auth {
    type = "password"
    # 일반 사용자 자격증명은 별도 prefix의 환경변수에서 주입하거나
    # secret manager에서 별도로 가져와야 함 (admin 자격증명과 분리)
  }
}

# Service account: 무인 CI/CD 파이프라인용
provider "cloudia" {
  alias         = "ci"
  endpoint      = var.cloudia_endpoint
  api_base_path = var.cloudia_base_path
  tls_insecure  = var.cloudia_tls_insecure

  auth {
    type = "client_credentials"
    # client_id / client_secret은 CLOUDIA_AUTH_CLIENT_ID/_SECRET 환경변수에서 주입
  }
}

resource "cloudia_project" "app" {
  provider = cloudia.admin
  name     = "app-prod"
}

resource "cloudia_vpc" "main" {
  provider = cloudia.user
  name     = "main"
  cidr     = "<your-vpc-cidr>"   # 예: 10.250.0.0/16
}
```

권한이 동일한 단일 계정이라면 alias 없이 기본 provider 하나만 운영할 수도 있으나, 권장하지 않습니다.

## CI/CD 통합

GitHub Actions 예시 — secret은 repo Settings → Secrets에서 관리합니다. 평문 값은 절대 직접 적지 마세요.

```yaml
jobs:
  apply:
    runs-on: ubuntu-latest
    env:
      CLOUDIA_ENDPOINT:           ${{ secrets.CLOUDIA_ENDPOINT }}      # 예: <your-cloudia-endpoint>
      CLOUDIA_API_BASE_PATH:      ${{ secrets.CLOUDIA_API_BASE_PATH }} # 예: /cloudia
      CLOUDIA_AUTH_TYPE:          password
      CLOUDIA_AUTH_USERNAME:      ${{ secrets.CLOUDIA_AUTH_USERNAME }}
      CLOUDIA_AUTH_PASSWORD:      ${{ secrets.CLOUDIA_AUTH_PASSWORD }}
      CLOUDIA_AUTH_CLIENT_ID:     ${{ secrets.CLOUDIA_AUTH_CLIENT_ID }}
      CLOUDIA_AUTH_CLIENT_SECRET: ${{ secrets.CLOUDIA_AUTH_CLIENT_SECRET }}
      # 운영에서는 TLS_INSECURE 사용 금지. dev 환경 전용 job에서만 한정적으로:
      # CLOUDIA_TLS_INSECURE: 'true'
    steps:
      - uses: actions/checkout@v4
      - uses: opentofu/setup-opentofu@v1
      - run: tofu init && tofu apply -auto-approve
```

GitLab CI / Jenkins / CircleCI도 동일한 환경 변수를 주입하면 동일하게 동작합니다.

## 함께 보기

- [시작하기 (Getting Started)](getting-started.md) — VPC → subnet → security group → instance end-to-end 흐름
- [문제 해결 (Troubleshooting)](troubleshooting.md) — 인증/polling 관련 자주 보는 오류, CA bundle 등록 절차
- 영문 Provider Reference (Terraform Registry): `iacloud/cloudia`

## 비고

중첩된 `auth { ... }` 블록은 ADR-0006에서 채택되었습니다. 동일 구조는 향후 OIDC `authorization_code` 등 추가 flow를 도입할 때도 재사용되며, 신규 `type` 값만 추가될 뿐 기존 HCL은 변경 없이 동작합니다.
