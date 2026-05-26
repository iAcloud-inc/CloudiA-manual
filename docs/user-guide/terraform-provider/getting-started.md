# 시작하기 (Getting Started)

> 영문 SSOT: `terraform-provider-cloudia/docs/guides/getting-started.md`. 본 한국어 본은 그 sibling이며, 차이가 있을 경우 영문판이 우선합니다.
>
> 본 문서의 예시는 Cloud:iA dev/test 환경 기준입니다. `<your-...>` 플레이스홀더와 실제 값 매핑은 [가이드 홈의 Reference 표](README.md#reference-table)를 참고하세요.

이 가이드는 Cloud:iA 환경에서 첫 번째 인스턴스를 띄우기까지의 최소 흐름을 안내합니다. [인증](authentication.md) 설정이 이미 끝났다고 가정합니다.

전체 흐름: **provider configure → VPC → subnet → security group → image lookup → ssh key → instance**.

## 0. 사전 준비

- **provider 설치 완료** — [설치하기](install.md)를 먼저 끝내고 오세요. (Registry 미배포 상태라 로컬 빌드 + `dev_overrides`가 필요합니다.)
- OpenTofu CLI (또는 Terraform CLI) 설치 완료
- 프로젝트 한 개 이상을 보유한 Cloud:iA 계정 (이 가이드는 admin alias 없이 단일 provider로 진행)
- 인증 환경 변수 export 완료 — [인증 §Cloud:iA dev/test 환경용 .env 예시](authentication.md#dev-env-example) 또는 [설치 §6](install.md#env-file)의 `.env`를 `source` 했다고 가정합니다

새 작업 디렉터리를 만들고 `main.tf` 파일을 생성합니다. 첫 블록은 "이 디렉터리는 cloudia provider를 쓴다" 라고 OpenTofu에 알리는 선언입니다.

```bash
mkdir ~/cloudia-tutorial && cd ~/cloudia-tutorial
```

```hcl
# main.tf
terraform {
  required_providers {
    cloudia = {
      source = "iacloud/cloudia"
    }
  }
}
```

> dev_overrides가 활성화된 상태에서는 `tofu init`을 건너뛰고 바로 `tofu plan`을 실행하면 됩니다. 자세한 이유는 [설치 §4](install.md#dev-overrides) 참고.

## 1. Provider 설정

연결 정보는 variable로 빼고, 값은 환경 변수(`TF_VAR_*`)나 `terraform.tfvars`로 주입합니다.

```hcl
variable "cloudia_endpoint" {
  type        = string
  description = "Cloud:iA API endpoint. dev/test 예시: <your-cloudia-endpoint>"
}

variable "cloudia_api_base_path" {
  type    = string
  default = ""   # dev/test는 "/cloudia"
}

variable "cloudia_tls_insecure" {
  type        = bool
  default     = false
  description = "TLS 검증 skip. dev only."
}

variable "project_id" {
  type        = string
  description = "Target project ID (예: dev/test의 25)"
}

provider "cloudia" {
  endpoint      = var.cloudia_endpoint
  api_base_path = var.cloudia_api_base_path
  tls_insecure  = var.cloudia_tls_insecure
  project_id    = var.project_id

  auth {
    type = "password"
    # username/password/client_id/client_secret은 CLOUDIA_AUTH_* 환경변수에서 주입
  }
}
```

Cloud:iA dev/test 환경용 `terraform.tfvars` 예시 (이 파일은 git에 커밋하지 말 것):

```hcl
cloudia_endpoint      = "<your-cloudia-endpoint>"
cloudia_api_base_path = "/cloudia"
cloudia_tls_insecure  = true   # dev only
project_id            = "<your-project-id>"   # dev/test 예시: 25
```

## 2. VPC 생성

`main.tf`에 다음 블록을 **추가**합니다 (앞의 provider 블록 아래에).

```hcl
variable "vpc_cidr" {
  type    = string
  default = "10.250.0.0/16"   # 본인 네트워크 설계에 맞게 조정
}

resource "cloudia_vpc" "main" {
  name = "tutorial-vpc"
  cidr = var.vpc_cidr
}
```

이제 plan으로 미리보기를 해봅니다.

```bash
tofu plan
```

다음과 같이 "VPC 1개를 새로 만들겠다" 는 요약이 나옵니다.

```
Terraform will perform the following actions:

  # cloudia_vpc.main will be created
  + resource "cloudia_vpc" "main" {
      + cidr = "10.250.0.0/16"
      + id   = (known after apply)
      + name = "tutorial-vpc"
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

> 📖 **plan 출력 읽는 법**
> - `+` 는 새로 생성, `-` 는 삭제, `~` 는 변경, `+/-` 는 재생성을 뜻합니다.
> - `(known after apply)` 는 "지금은 모르지만 apply 후에 결정되는 값" 이라는 뜻입니다 (백엔드가 ID를 발급하는 경우).
> - 맨 아래 `Plan: X to add, Y to change, Z to destroy.` 가 한 줄 요약입니다.

내용이 맞으면 `apply`로 실제 생성합니다.

```bash
tofu apply
```

`Do you want to perform these actions?` 프롬프트에 `yes`를 입력하면 진행됩니다. 백엔드가 비동기로 작업하므로 1~2분이 걸릴 수 있습니다 ([개념 §7 비동기 작업과 polling](concepts.md#async-polling) 참고).

`apply` 이후 `cloudia_vpc.main.id`를 다음 단계에서 참조합니다.

> 🚨 **중간에 멈춘 경우**: 만약 apply 중 Ctrl+C로 중단했다면, 백엔드에는 이미 일부 리소스가 만들어졌을 수 있습니다. `tofu plan`을 다시 돌려 현재 state와 백엔드 상태를 확인하세요. 필요시 [문제 해결](troubleshooting.md)을 참고합니다.

## 3. Subnet 생성

```hcl
variable "subnet_cidr" {
  type    = string
  default = "10.250.1.0/24"   # vpc_cidr 안의 주소 블록
}

resource "cloudia_subnet" "default" {
  vpc_id = cloudia_vpc.main.id
  name   = "tutorial-subnet"
  cidr   = var.subnet_cidr
}
```

## 4. Security Group 생성

SSH (22) inbound + 모든 outbound 허용.

```hcl
resource "cloudia_security_group" "default" {
  vpc_id      = cloudia_vpc.main.id
  name        = "tutorial-sg"
  description = "Allow SSH inbound"

  ingress {
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["<your-admin-cidr>"]   # 예: ["10.0.0.0/8"]. 0.0.0.0/0은 금지
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

> 운영 환경에서는 inbound CIDR을 특정 IP allowlist로 제한하세요. dev/test에서도 0.0.0.0/0을 그대로 두지 말고 관리자 대역(`<your-admin-cidr>`)으로 좁히세요.

## 5. Image 조회

OS 이미지는 data source로 조회합니다. 이름 기반 조회가 일반적입니다.

```hcl
data "cloudia_image" "ubuntu" {
  name = "<your-image-name>"   # 예: ubuntu-24.04 (dev/test에 등록된 이미지 이름은 운영자에게 확인)
}
```

여러 후보가 필요하면 컬렉션 data source인 `cloudia_images`를 쓰세요. 둘 사이의 일반 선택 기준은 [Singular vs Plural 데이터소스](data-sources.md)에서 다룹니다.

## 6. SSH 키 등록

인스턴스에 SSH로 접속할 때 쓸 공개키를 등록합니다. 아직 SSH 키가 없다면 먼저 만드세요.

```bash
# 새 SSH 키가 필요하면 (이미 있다면 skip)
ssh-keygen -t ed25519 -C "your_email@example.com"
# 기본 위치: ~/.ssh/id_ed25519 (private), ~/.ssh/id_ed25519.pub (public)
```

```hcl
resource "cloudia_ssh_key" "me" {
  name       = "tutorial-key"
  public_key = file("~/.ssh/id_ed25519.pub")   # 공개키 파일 경로
}
```

> `file(...)`은 파일 내용을 읽어 문자열로 만드는 HCL 내장 함수입니다. 공개키(`.pub`)만 올리고 **개인키는 절대 올리지 마세요**.

## 7. 인스턴스 생성

`instance_type` 값은 카탈로그(`cloudia_instance_types`)로 조회하거나, ID를 알면 직접 넘길 수 있습니다.

```hcl
data "cloudia_instance_type" "small" {
  name = "<your-instance-type-name>"   # 예: s1.small. 카탈로그는 환경마다 다름
}

resource "cloudia_instance" "demo" {
  name         = "tutorial-instance"
  network_id   = cloudia_vpc.main.id
  vcpu_number  = data.cloudia_instance_type.small.vcpu_number
  memory_total = data.cloudia_instance_type.small.memory_total

  image_id = data.cloudia_image.ubuntu.id

  vnic = [
    {
      subnet_id          = cloudia_subnet.default.id
      security_group_ids = [cloudia_security_group.default.id]
      is_default_nic     = true
    },
  ]

  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [cloudia_ssh_key.me.id]
  }
}
```

```bash
tofu apply
```

생성은 비동기입니다 — provider가 백엔드 `requestId`를 polling합니다. `CLOUDIA_POLL_TIMEOUT_SECONDS` (기본 600초) 안에 완료되지 않으면 timeout 에러가 발생합니다 ([인증 §선택 환경 변수](authentication.md#optional-env-vars) 참고).

`cloud_init` 블록은 필수입니다. SSH 키 대신 초기 비밀번호를 줄 때는 `cloud_init = { username = "appuser", password = "<your-password>" }`처럼 적으면 됩니다.

`cloud_init.username`은 4-20자, 소문자로 시작, `[a-z0-9_-]`만 허용됩니다. `root`, `admin`, `ubuntu`, `centos` 같은 예약 이름은 backend가 거부하므로 예시처럼 일반 사용자명을 쓰세요.

## 8. 결과 확인

인스턴스에 연결된 disk와 NIC:

```hcl
data "cloudia_instance_disks" "demo" {
  instance_id = cloudia_instance.demo.id
}

data "cloudia_instance_interface" "demo_default" {
  instance_id = cloudia_instance.demo.id
  is_default  = true
}

output "primary_ip" {
  value = data.cloudia_instance_interface.demo_default.ip_address
}
```

## 9. 정리

튜토리얼 리소스를 모두 삭제하려면:

```bash
tofu destroy
```

`Plan: 0 to add, 0 to change, X to destroy.` 와 함께 무엇이 삭제될지 보여줍니다. `yes`를 입력하면 실제 삭제가 진행됩니다.

참고 사항:

- 인스턴스에 스냅샷이 있으면 스냅샷을 먼저 삭제해야 합니다. 스냅샷은 별도 리소스(`cloudia_instance_snapshot`)입니다.
- 다른 리소스가 참조 중인 `vpc`/`subnet`/`security_group`은 그 참조가 해제될 때까지 `destroy`가 막힙니다.
- `tofu destroy` 실행 시 **현재 디렉터리의 state에 기록된 리소스만** 삭제됩니다 — 콘솔에서 만든 다른 자원에는 영향이 없습니다.

## 그다음에 더 알아볼 것

- [Singular vs Plural 데이터소스](data-sources.md) — `data.cloudia_image` vs `data.cloudia_images` 같은 단일/컬렉션 선택 기준
- [문제 해결](troubleshooting.md) — 자주 만나는 에러와 대응
- HashiCorp 공식 튜토리얼: https://learn.hashicorp.com/terraform (variable, output, module 같은 다음 단계 개념)
- 더 큰 구성을 만들 때는 **modules**로 재사용 가능한 단위로 나누고, **remote backend**(S3 등)로 state를 팀과 공유하는 것이 일반적입니다 — 본 매뉴얼 범위 밖이므로 위 공식 자료를 참고하세요.

## 비고

OIDC 인증이 도입되면 [인증](authentication.md) §0 사전 준비와 이 가이드의 사전 준비 항목이 함께 업데이트됩니다 (ADR-0006).
