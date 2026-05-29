# Provider 설정 (Configuration)

> 본 문서의 예시는 Cloud:iA dev/test 환경 기준입니다. `<your-...>` 플레이스홀더와 실제 값 매핑은 [가이드 홈의 Reference 표](../README.md#reference-table)를 참고하세요.

`provider "cloudia"` 블록의 설정 방법을 설명합니다. 인증(`auth {}` 블록) 상세는 [인증](authentication.md) 가이드에서 다룹니다.

## required_providers 선언

모든 Terraform/OpenTofu 설정의 시작점입니다.

```hcl
terraform {
  required_providers {
    cloudia = {
      source  = "iacloud/cloudia"
      version = "~> 0.1"
    }
  }
}
```

`~> 0.1` constraint는 동일 minor(0.x) 안에서 최신 patch를 자동으로 추종합니다. 재현성이 더 중요한 경우(예: 프로덕션 배포 고정)에는 `version = "0.1.0"` 처럼 정확한 버전으로 핀 고정하세요.

## provider 인수

```hcl
provider "cloudia" {
  endpoint      = "<your-cloudia-endpoint>"
  api_base_path = "/cloudia"   # 선택 — subpath 마운트 환경에서만 필요
  project_id    = "<your-project-id>"  # 선택 — 기본 project context

  auth {
    type = "password"
    # 인증 상세는 authentication.md 참고
  }
}
```

| 항목 | 설명 | 필수 | 비고 |
|---|---|---|---|
| `endpoint` | Cloud:iA API endpoint URL | 필수 | 예: `<your-cloudia-endpoint>` |
| `api_base_path` | API base path prefix | 선택 | API가 subpath에 마운트된 경우만 설정 (예: `/cloudia`). 루트(`/`)에 마운트된 경우 빈 문자열 또는 생략. 잘못 설정하면 `http=405` 오류 발생 |
| `project_id` | 기본 project context ID | 선택 | 리소스에서 `project_id`를 명시하지 않을 때 fallback. 환경 변수 `CLOUDIA_PROJECT_ID`로도 주입 가능 |
| `tls_insecure` | TLS 인증서 검증 생략 | 선택 | 기본 `false`. dev 전용 — 운영 환경 금지. 아래 TLS / CA 인증서 섹션 참고 |
| `auth {}` | 인증 블록 | 필수 | 상세는 [인증](authentication.md) 참고 |

> 민감 정보(`password`, `client_secret` 등)는 HCL에 평문으로 적지 마세요. 환경 변수 또는 secret manager로 주입하세요.

## alias 패턴

같은 클러스터에 대해 권한이 다른 두 계정을 사용할 때 `alias`로 provider 인스턴스를 분리합니다. 프로젝트 생성·삭제와 같은 admin 전용 작업은 `admin` alias를, 프로젝트 범위 리소스(VPC, 인스턴스 등) 관리는 `user` alias를 사용하는 것이 권장 패턴입니다.

```hcl
# 관리자: project 생성/삭제 전용
provider "cloudia" {
  alias         = "admin"
  endpoint      = var.cloudia_endpoint
  api_base_path = var.cloudia_base_path

  auth {
    type = "password"
    # username/password는 환경 변수에서 주입
  }
}

# 일반 사용자: project-scoped 리소스 전용
provider "cloudia" {
  alias         = "user"
  endpoint      = var.cloudia_endpoint
  api_base_path = var.cloudia_base_path
  project_id    = cloudia_project.app.id

  auth {
    type = "password"
    # 일반 사용자 자격증명은 admin과 분리하여 별도로 주입
  }
}

resource "cloudia_project" "app" {
  provider = cloudia.admin
  name     = "app-prod"
}

resource "cloudia_vpc" "main" {
  provider = cloudia.user
  name     = "main"
  cidr     = "<your-vpc-cidr>"
}
```

리소스에서 특정 alias를 참조하려면 `provider = cloudia.admin` 처럼 `<provider이름>.<alias>` 형식으로 지정합니다.

권한이 동일한 단일 계정이라면 alias 없이 기본 provider 하나만 운영할 수도 있습니다.

## 환경 변수

모든 provider 인수는 HCL 대신 환경 변수로 주입할 수 있습니다. HCL 값이 항상 환경 변수보다 우선합니다.

| 환경 변수 | 대응 provider 인수 | 기본값 | 설명 |
|---|---|---|---|
| `CLOUDIA_ENDPOINT` | `endpoint` | (없음) | Cloud:iA API endpoint URL |
| `CLOUDIA_API_BASE_PATH` | `api_base_path` | `""` | API base path prefix (예: `/cloudia`) |
| `CLOUDIA_PROJECT_ID` | `project_id` | (없음) | 기본 project context. 리소스에서 `project_id`를 명시하지 않을 때 fallback으로 사용 |
| `CLOUDIA_POLL_TIMEOUT_SECONDS` | `poll_timeout` | `600` | 비동기 작업 polling timeout (초). 대용량 리소스 생성 등 오래 걸리는 작업 시 늘려 설정 |
| `CLOUDIA_TLS_INSECURE` | `tls_insecure` | `false` | TLS 인증서 검증 생략 (dev 전용). 아래 TLS 섹션 참고 |

인증 관련 환경 변수(`CLOUDIA_AUTH_*`)는 [인증](authentication.md) 가이드를 참고하세요.

## TLS / CA 인증서

Cloud:iA dev/test 환경은 보통 self-signed 인증서를 사용합니다. 두 가지 방법 중 하나를 선택하세요.

**옵션 A — CA를 시스템 trust store에 등록 (권장)**: Cloud:iA 운영자에게 CA 인증서(`<your-ca-bundle>`)를 발급받아 OS 신뢰 저장소에 등록합니다. 등록 절차는 [설치하기 §5 CA 인증서 받기](installation.md#ca-cert)에 정리되어 있습니다. 운영 환경에서는 이 방법을 사용하세요.

**옵션 B — TLS 검증 끄기 (dev 전용, 비권장)**: CA 등록이 번거로운 개발 환경에서만 `tls_insecure`를 켭니다. 운영 환경에서는 절대 사용하지 마세요 — MITM 공격에 그대로 노출됩니다.

```hcl
provider "cloudia" {
  endpoint     = "<your-cloudia-endpoint>"
  tls_insecure = true   # dev 전용. CA를 등록했다면 제거

  auth {
    type = "password"
  }
}
```

환경 변수로도 켤 수 있습니다: `export CLOUDIA_TLS_INSECURE=true`.

TLS 관련 오류(`x509: certificate signed by unknown authority` 등) 해결 방법은 [문제 해결 §TLS](troubleshooting.md#tls)를 참고하세요.

## 다음 단계

- [인증](authentication.md) — `auth {}` 블록 옵션, password/client_credentials, CI/CD 연동
- [시작하기](getting-started.md) — VPC → subnet → security group → instance 최소 흐름
