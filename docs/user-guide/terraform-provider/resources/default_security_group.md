# cloudia_default_security_group

VPC 생성 시 백엔드가 자동으로 만드는 기본 보안그룹(singleton)을 Terraform 관리 대상으로 adopt(어댑트)하는 리소스입니다. 새로 생성하는 것이 아니라 이미 존재하는 기본 SG를 가져와 관리합니다.

## 예제

기본 SG를 adopt하고 관리자 대역에서 SSH만 허용:

```hcl
resource "cloudia_default_security_group" "main_default" {
  vpc_id      = cloudia_vpc.main.id
  description = "기본 SG — 관리자 대역에서만 SSH 허용"

  inbound_rules = [
    {
      protocol    = "TCP"
      ip_cidr     = "10.0.0.0/8"
      port        = "22"
      description = "ssh from internal cidr"
    },
  ]

  outbound_rules = [
    {
      protocol    = "ALL"
      ip_cidr     = "0.0.0.0/0"
      port        = "ALL"
      description = "default outbound allow"
    },
  ]
}
```

규칙을 Terraform이 관리하지 않고 메타데이터만 관리하는 경우(forget 패턴):

```hcl
resource "cloudia_default_security_group" "main_default" {
  vpc_id = cloudia_vpc.main.id
  # inbound_rules, outbound_rules 생략 → 백엔드 소유(미관리)
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `vpc_id` | 상위 VPC ID. 이 리소스의 식별자이며 in-place 변경 불가 | 필수 | 변경 시 RequiresReplace |
| `description` | 기본 SG에 설정할 설명. 최대 200자 | 선택 | 생략 시 백엔드 값 유지(미관리) |
| `inbound_rules` | inbound 규칙 집합. 생략 시 inbound 방향을 미관리 상태로 유지 | 선택 | 빈 set(`[]`)으로 설정하면 모든 inbound 규칙 제거 |
| `outbound_rules` | outbound 규칙 집합. 생략 시 outbound 방향을 미관리 상태로 유지 | 선택 | 빈 set(`[]`)으로 설정하면 모든 outbound 규칙 제거 |
| `allow_intra_group_traffic` | 같은 SG 멤버 간 트래픽 허용 여부 | 선택 | 생략 시 백엔드 값 유지(미관리) |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

### inbound_rules / outbound_rules 중첩 인자

| 인자 | 설명 | 필수 |
|------|------|------|
| `protocol` | 프로토콜. 예: `ALL`, `TCP`, `UDP` | 필수 |
| `ip_cidr` | 허용할 CIDR. 예: `0.0.0.0/0`, `10.20.0.0/16` | 필수 |
| `port` | 포트 또는 범위. 예: `ALL`, `22`, `80-443` | 필수 |
| `description` | 규칙 설명. 최대 200자 | 선택 |
| `traffic_type` | 규칙 방향. 생략 시 위치에 따라 기본값 적용 | 선택 |

**읽기 전용 출력값**: `id`, `name`(백엔드 고정), `provisioning_source`, `system`, `created_at`, `updated_at`

## 운영 노트

- **adopt/forget 모델**: 이 리소스는 백엔드 singleton을 "adopt"합니다. `terraform destroy`를 실행해도 실제 백엔드의 기본 SG는 삭제되지 않고, Terraform state에서만 제거됩니다. 기본 SG는 VPC 삭제 시 백엔드가 자동으로 제거합니다.
- **null = 미관리(tri-state)**: `description`, `allow_intra_group_traffic`, `inbound_rules`, `outbound_rules`를 HCL에서 생략하면 해당 속성은 Terraform이 관리하지 않습니다(`null` 상태). 이는 빈 값과 다릅니다. `outbound_rules = null` 일 때 outbound 방향은 백엔드 소유로 유지됩니다.
- **name은 백엔드 고정**: `name` 인자는 존재하지 않습니다. 이름은 백엔드가 `<vpc-name>-default-sg` 형식으로 자동 부여하며, 읽기 전용 `name` 속성으로만 조회할 수 있습니다.
- **import 후 재선언 필요**: import 직후 `description`, `inbound_rules`, `outbound_rules`, `allow_intra_group_traffic` 모두 `null`(미관리)로 설정됩니다. 관리하려는 속성을 HCL에 재선언한 뒤 `terraform plan`으로 확인하세요.
- **import 키는 VPC ID**: 기본 SG의 ID가 아닌 **VPC ID**를 import 키로 사용합니다. 백엔드가 VPC ID로 singleton SG를 자동으로 조회합니다.
- **일반 `cloudia_security_group`과의 차이**: VPC당 1개만 존재하며, name이 백엔드 고정이고, destroy 시 백엔드 SG가 실제로 삭제되지 않습니다.

## Import

```bash
terraform import cloudia_default_security_group.main_default <project_id>/<vpc_id>
```

예시:

```bash
terraform import cloudia_default_security_group.main_default 1/42
```

import 키 형식: `<project_id>/<vpc_id>` (SG ID가 아닌 **VPC ID** 사용)

> import 직후 `description`, `inbound_rules`, `outbound_rules`, `allow_intra_group_traffic`은 모두 `null`(미관리) 상태입니다. 관리하려는 속성을 HCL에 재선언한 뒤 `terraform plan`으로 변경사항을 확인하세요.

## 관련 항목

- [vpc.md](vpc.md) — 상위 VPC 리소스 (기본 SG의 생명주기와 연동)
- [security_group.md](security_group.md) — 사용자 정의 보안그룹
- [subnet.md](subnet.md) — 서브넷 리소스
- [floating_ip.md](floating_ip.md) — 공인 IP 할당
- [../guides/getting-started.md](../guides/getting-started.md)
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/default_security_group.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
