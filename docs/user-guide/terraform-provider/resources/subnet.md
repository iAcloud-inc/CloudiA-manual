# cloudia_subnet

VPC 안에 IP 블록(서브넷)을 생성하는 리소스입니다. 서브넷 유형(`PUBLIC_SUBNET` / `PRIVATE_SUBNET`)으로 인터넷 접근 여부를 구분합니다.

## 예제

```hcl
resource "cloudia_subnet" "public" {
  vpc_id = cloudia_vpc.main.id
  name   = "public-subnet"
  cidr   = "10.20.1.0/24"
  type   = "PUBLIC_SUBNET"   # 또는 "PRIVATE_SUBNET"
}
```

DNS를 명시적으로 지정하는 경우:

```hcl
resource "cloudia_subnet" "private" {
  vpc_id      = cloudia_vpc.main.id
  name        = "private-subnet"
  cidr        = "10.20.2.0/24"
  type        = "PRIVATE_SUBNET"
  dns         = "10.20.0.2"
  description = "private subnet"
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `vpc_id` | 상위 VPC(네트워크) ID | 필수 | |
| `name` | 서브넷 이름. 최대 80자, 영문자·숫자·`-`·`_` 허용 | 필수 | |
| `cidr` | 서브넷 CIDR. 예: `10.20.1.0/24` | 필수 | 변경 시 **RequiresReplace** |
| `type` | 서브넷 유형. `PUBLIC_SUBNET` 또는 `PRIVATE_SUBNET` | 필수 | |
| `dns` | 서브넷에 지정할 DNS 서버 IP | 선택 | 백엔드가 자동 보정하지 않음 — 비워두면 주의 필요 |
| `description` | 서브넷 설명. 최대 200자 | 선택 | |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`, `gateway_ip`, `dns_server`, `created_at`, `updated_at`

## 운영 노트

- **cidr RequiresReplace**: `cidr` 값을 변경하면 서브넷을 destroy 후 재생성합니다. 서브넷에 인스턴스가 붙어 있으면 먼저 인스턴스를 제거해야 합니다.
- **dns 필드 동작**: `dns`를 비워두면 백엔드가 자동으로 채워주지 않습니다. 다음 refresh 시 백엔드에 저장된 값이 반영되므로, `dns_server`(읽기 전용)와 `dns`(입력) 두 필드가 별개로 동작합니다. 정확한 DNS 제어가 필요하면 `dns`를 명시적으로 지정하세요.
- **서브넷 유형 변경**: `type`(PUBLIC/PRIVATE) 변경도 RequiresReplace를 유발할 수 있습니다. 변경 전 plan 출력을 확인하세요.
- **VPC 먼저**: 서브넷은 반드시 VPC가 존재해야 생성할 수 있습니다. `cloudia_vpc.main.id` 참조를 통해 의존 순서를 자동으로 설정하세요.

## Import

```bash
terraform import cloudia_subnet.public <project_id>/<vpc_id>/<subnet_id>
```

예시:

```bash
terraform import cloudia_subnet.public 1/42/7
```

import 키 형식: `<project_id>/<vpc_id>/<subnet_id>`

## 관련 항목

- [vpc.md](vpc.md) — 상위 VPC 리소스
- [security_group.md](security_group.md) — 사용자 정의 보안그룹
- [default_security_group.md](default_security_group.md) — VPC 자동 생성 기본 보안그룹
- [floating_ip.md](floating_ip.md) — 공인 IP 할당
- [../guides/getting-started.md](../guides/getting-started.md)
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/subnet.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
