# cloudia_security_group

VPC 안에 사용자 정의 보안그룹을 생성하고 inbound/outbound 규칙을 관리하는 리소스입니다.

## 예제

HTTP/HTTPS 허용 보안그룹:

```hcl
resource "cloudia_security_group" "web" {
  vpc_id      = cloudia_vpc.main.id
  name        = "web-sg"
  description = "HTTP/HTTPS allow"

  inbound_rules = [
    {
      protocol = "TCP"
      ip_cidr  = "0.0.0.0/0"
      port     = "80"
    },
    {
      protocol = "TCP"
      ip_cidr  = "0.0.0.0/0"
      port     = "443"
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

관리자 대역에서만 SSH 허용:

```hcl
resource "cloudia_security_group" "ssh" {
  vpc_id      = cloudia_vpc.main.id
  name        = "allow-ssh"
  description = "SSH from admin CIDR only"

  inbound_rules = [
    {
      protocol = "TCP"
      ip_cidr  = "<your-admin-cidr>"
      port     = "22"
    },
  ]

  outbound_rules = [
    {
      protocol = "ALL"
      ip_cidr  = "0.0.0.0/0"
      port     = "ALL"
    },
  ]
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `vpc_id` | 상위 VPC(네트워크) ID | 필수 | |
| `name` | 보안그룹 이름. 최대 80자, 영문자·숫자·`-`·`_` 허용 | 필수 | |
| `description` | 보안그룹 설명. 최대 200자 | 필수 | |
| `inbound_rules` | inbound 규칙 집합. 생략 시 inbound 방향을 미관리(unmanaged) 상태로 유지 | 선택 | 빈 set(`[]`)으로 설정하면 모든 inbound 규칙 제거 |
| `outbound_rules` | outbound 규칙 집합. 생략 시 outbound 방향을 미관리 상태로 유지 | 선택 | 빈 set(`[]`)으로 설정하면 모든 outbound 규칙 제거 |
| `allow_intra_group_traffic` | 같은 보안그룹 멤버 간 트래픽 허용 여부 | 선택 | |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

### inbound_rules / outbound_rules 중첩 인자

| 인자 | 설명 | 필수 |
|------|------|------|
| `protocol` | 프로토콜. 예: `ALL`, `TCP`, `UDP` | 필수 |
| `ip_cidr` | 허용할 CIDR. 예: `0.0.0.0/0`, `10.20.0.0/16` | 필수 |
| `port` | 포트 또는 범위. 예: `ALL`, `22`, `80-443` | 필수 |
| `description` | 규칙 설명. 최대 200자 | 선택 |
| `traffic_type` | 규칙 방향. 생략 시 인자 위치에 따라 `inbound`/`outbound` 기본값 적용 | 선택 |

**읽기 전용 출력값**: `id`, `provisioning_source`, `system`, `created_at`, `updated_at`

## 운영 노트

- **SSH에 `0.0.0.0/0` 금지**: 22번 포트 inbound에 `0.0.0.0/0`을 사용하지 마세요. 관리자 IP 대역(`<your-admin-cidr>`)으로 좁혀야 합니다.
- **null = 미관리(tri-state)**: `inbound_rules` 또는 `outbound_rules`를 HCL에서 생략하면 해당 방향의 규칙은 Terraform이 관리하지 않습니다. 빈 set `[]`을 지정하면 모든 규칙을 삭제합니다. 이 두 상태는 다릅니다.
- **import 후 rules 재선언 필요**: `terraform import` 직후에는 `inbound_rules`와 `outbound_rules`가 `null`(미관리)로 설정됩니다. 백엔드에 규칙이 있더라도 Terraform은 무시합니다. **import 후 관리하려는 규칙을 HCL에 반드시 재선언**해야 합니다.
- **rule 정규화**: `ip_cidr`의 whitespace나 `port` 범위 표기(`80-80` 등)가 백엔드에서 정규화될 수 있습니다. plan 시 예상치 못한 diff가 발생하면 백엔드 반환값을 기준으로 HCL을 수정하세요.
- **VPC 이동 불가**: `vpc_id` 변경은 보안그룹을 destroy 후 재생성합니다.

## Import

```bash
terraform import cloudia_security_group.web <project_id>/<vpc_id>/<security_group_id>
```

예시:

```bash
terraform import cloudia_security_group.web 1/42/7
```

import 키 형식: `<project_id>/<vpc_id>/<security_group_id>`

> import 직후 `inbound_rules`, `outbound_rules`는 `null`(미관리) 상태입니다. 관리하려는 규칙을 HCL에 재선언한 뒤 `terraform plan`으로 변경사항을 확인하세요.

## 관련 항목

- [default_security_group.md](default_security_group.md) — VPC 자동 생성 기본 보안그룹
- [vpc.md](vpc.md) — 상위 VPC 리소스
- [subnet.md](subnet.md) — 서브넷 리소스
- [floating_ip.md](floating_ip.md) — 공인 IP 할당
- [../guides/getting-started.md](../guides/getting-started.md)
- [../guides/import.md](../guides/import.md)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 generated reference(provider `docs/resources/security_group.md`, 추후 Registry)를 SSOT로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
