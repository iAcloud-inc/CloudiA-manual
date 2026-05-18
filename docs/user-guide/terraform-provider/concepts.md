# 개념 정리 — IaC가 처음이라면

> 본 문서는 Infrastructure as Code(IaC), Terraform / OpenTofu, HCL 같은 용어가 처음인 분들을 위한 입문용 정리입니다. 이미 익숙하시다면 [설치하기](install.md)로 건너뛰세요.

## 1. Infrastructure as Code (IaC)란?

Cloud:iA 인프라(VPC, 서브넷, 인스턴스 등)를 **콘솔 UI에서 클릭으로** 만드는 대신, **코드 파일로 선언해서 명령어로 만드는** 방식입니다.

| 비교 | UI로 작업 | IaC로 작업 |
|---|---|---|
| 만들기 | 메뉴 클릭 → 값 입력 → 생성 | 코드로 선언 → `apply` 명령 한 번 |
| 변경 추적 | 콘솔 로그/감사 로그에 의존 | git diff로 변경 이력 확인 |
| 같은 환경 재현 | 매뉴얼대로 다시 클릭 | 같은 코드를 다시 `apply` |
| 협업 | 누가 무엇을 만들었는지 사후 확인 | PR 리뷰로 사전 검토 |
| 실수 복구 | 콘솔에서 일일이 삭제 | `destroy` 한 번 또는 git revert |

**언제 IaC가 유리한가**: 환경을 여러 개 만들어야 할 때(dev/staging/prod), 같은 구성을 반복 생성할 때, 변경을 팀원과 함께 리뷰하고 싶을 때, 누가 무엇을 바꿨는지 기록이 필요할 때.

**언제 UI가 더 나은가**: 일회성 탐색, 잘 모르는 기능을 처음 써볼 때, 빠른 디버깅. → 익숙해진 뒤 IaC로 옮기는 흐름이 자연스럽습니다.

## 2. Terraform과 OpenTofu

같은 일을 하는 두 도구입니다.

- **Terraform** — HashiCorp가 만든 원조. 2023년 8월 라이선스가 BSL(Business Source License)로 변경되면서 일부 상용 사용 제한이 생겼습니다.
- **OpenTofu** — Terraform을 fork해 MPL-2.0(완전 오픈소스)로 운영하는 커뮤니티 버전. 명령어와 문법은 Terraform과 거의 동일(`terraform` → `tofu`로 바꿔도 동작).

**본 매뉴얼은 OpenTofu(`tofu` 명령)를 기본 예시로 사용**합니다. Terraform CLI를 써도 동일하게 동작합니다 (`tofu` → `terraform`으로 바꿔 읽으면 됩니다).

## 3. Provider, Resource, Data source

| 용어 | 뜻 | Cloud:iA 예 |
|---|---|---|
| **Provider** | 특정 플랫폼(클라우드)을 다루는 플러그인 | `cloudia` (= terraform-provider-cloudia) |
| **Resource** | provider가 **만들고/바꾸고/지울 수 있는** 객체 | `cloudia_vpc`, `cloudia_instance` |
| **Data source** | provider가 **읽기만** 하는 객체 (이미 있는 것을 조회) | `cloudia_image`, `cloudia_projects` |

코드에서는 이렇게 씁니다:

```hcl
# resource = 만든다
resource "cloudia_vpc" "main" {
  name = "my-vpc"
  cidr = "10.0.0.0/16"
}

# data = 조회만 한다 (이미 등록된 Ubuntu 이미지 찾기)
data "cloudia_image" "ubuntu" {
  name = "ubuntu-24.04"
}
```

## 4. HCL — 코드 작성에 쓰는 언어

Terraform/OpenTofu가 쓰는 설정 언어를 **HCL(HashiCorp Configuration Language)** 이라 부릅니다. 대략 JSON과 비슷하지만 사람이 읽기 쉽게 다듬어진 형태입니다.

기본 구조 4가지만 알면 됩니다.

```hcl
# (1) terraform 블록 — 어떤 provider를 쓸지 선언
terraform {
  required_providers {
    cloudia = {
      source = "iacloud/cloudia"
    }
  }
}

# (2) provider 블록 — provider 자체의 설정(endpoint, 인증 등)
provider "cloudia" {
  endpoint = "https://192.168.160.10"
}

# (3) resource 블록 — 만들고 싶은 객체
resource "cloudia_vpc" "main" {
  name = "my-vpc"
  cidr = "10.0.0.0/16"
}

# (4) variable / output / data 블록 — 보조 (variable: 입력값, output: 출력값, data: 조회)
variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

output "vpc_id" {
  value = cloudia_vpc.main.id   # ← 위에서 만든 vpc의 id를 다른 곳에서 쓸 수 있게 노출
}
```

**참조 문법**: 다른 리소스의 속성을 가져올 때는 `<리소스타입>.<이름>.<속성>` 형태로 적습니다.

```hcl
resource "cloudia_subnet" "default" {
  vpc_id = cloudia_vpc.main.id   # ← cloudia_vpc 리소스 "main"의 id 속성
  ...
}
```

## 5. State — Terraform의 머릿속 메모

Terraform은 "내가 만든 리소스가 지금 어떤 상태인지" 를 `terraform.tfstate`라는 JSON 파일에 기록합니다. 이걸 **state 파일** 이라고 합니다.

```
my-project/
├── main.tf              ← 사용자가 작성한 코드 (의도)
├── terraform.tfstate    ← Terraform이 만든 기록 (현실)
└── terraform.tfstate.backup
```

- **의도(`.tf`)** 와 **현실(`.tfstate`)** 을 비교해서 차이만큼만 작업합니다.
- state 파일에는 리소스 ID, 속성, 그리고 가끔 민감한 값도 포함됩니다 → **git에 절대 커밋하지 마세요** (`.gitignore`에 `*.tfstate*` 추가).
- 팀에서 같이 쓸 때는 state를 원격 저장소(S3, Terraform Cloud 등)에 두는 "remote backend"를 설정하지만, 처음에는 로컬 파일로 충분합니다.

## 6. 핵심 명령어 4개

| 명령 | 하는 일 |
|---|---|
| `tofu init` | provider 다운로드, 작업 디렉터리 초기화 (한 번만, provider 바뀌면 다시) |
| `tofu plan` | 코드(의도) vs state(현실)를 비교해서 **무엇을 만들/바꿀/지울지** 보여줌. 실제로는 아무것도 안 함 |
| `tofu apply` | `plan` 내용을 실제로 실행. 확인 프롬프트가 뜸 (`-auto-approve`로 생략 가능) |
| `tofu destroy` | state에 있는 리소스 전부 삭제 |

**일반적인 흐름:**

```
코드 작성 ──→ tofu plan으로 미리보기 ──→ tofu apply로 실행
                       ↓
                  잘못됐으면 코드 수정 후 plan부터 다시
```

<a id="async-polling"></a>
## 7. 비동기 작업과 polling

Cloud:iA 백엔드는 인스턴스 생성 같은 무거운 작업을 **비동기**로 처리합니다. 즉 `apply` 명령을 내려도 백엔드는 "받았어요. 진행 중입니다(requestId=...)"만 즉시 응답합니다.

provider가 사용자 대신 "완료됐는지" 를 주기적으로 물어봐(polling) 끝날 때까지 기다려 줍니다 — 그래서 사용자 입장에서는 `apply`가 한 번에 끝난 것처럼 보입니다. 기본 polling timeout은 10분(600초)이며, 느린 작업은 [문제 해결 §비동기 polling](troubleshooting.md#async-polling)을 참고해 시간을 늘릴 수 있습니다.

## 8. 다음 단계

이 정도 개념이 잡혔다면 실제로 설치해 봅니다.

- [설치하기 (로컬 빌드 + dev_overrides)](install.md) — Cloud:iA provider가 아직 Registry에 게시되지 않아 직접 빌드해 써야 합니다
- [인증](authentication.md) — endpoint와 자격 증명 설정
- [시작하기](getting-started.md) — 첫 VPC와 인스턴스 만들기

더 깊이 들어가고 싶다면:

- HashiCorp의 공식 IaC 학습 자료: https://learn.hashicorp.com/terraform (OpenTofu도 거의 동일하게 적용)
- OpenTofu 공식 문서: https://opentofu.org/docs/
