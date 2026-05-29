# cloudia_vpc

VPC(가상 사설 네트워크)를 생성하는 리소스입니다. 모든 네트워크 리소스의 최상위 격리 단위이며, 생성 시 백엔드가 default security group과 vRouter용 public IP를 자동으로 할당합니다.

## 예제

```hcl
resource "cloudia_vpc" "main" {
  name        = "main-vpc"
  cidr        = "10.20.0.0/16"
  description = "main vpc"
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `name` | VPC 이름. 최대 60자, 영문자·숫자·`-`·`_` 허용 | 필수 | |
| `cidr` | VPC의 IP 대역. 예: `10.20.0.0/16` | 필수 | 백엔드가 정규화(canonical)하여 저장 |
| `description` | VPC 설명. 최대 200자 | 선택 | |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`, `default_security_group_id`, `dns_server_ip`, `vlan`, `created_at`, `updated_at`

## 운영 노트

- **CIDR canonical drift**: 입력한 CIDR(`10.20.0.1/16` 등)을 백엔드가 정규화(`10.20.0.0/16`)하여 저장합니다. 다음 `plan` 시 diff가 발생하지 않도록 처음부터 정규화된 CIDR를 입력하세요.
- **자동 리소스 생성**: VPC 생성 시 백엔드가 default security group 1개와 vRouter용 public IP 1개를 자동으로 할당합니다. 따라서 프로젝트의 `public_ip_quota >= 1` 이 충족되어야 합니다.
- **destroy 시 동작**: `terraform destroy` 로 VPC를 삭제하면 연결된 서브넷, 보안그룹, 플로팅 IP를 먼저 제거해야 합니다. 의존 리소스가 남아 있으면 API가 에러를 반환합니다.
- **동시 생성 race**: 동일 프로젝트에서 여러 VPC를 동시에 생성할 때 race condition이 발생할 수 있습니다. `depends_on` 또는 순차 apply를 권장합니다.

## Import

```bash
terraform import cloudia_vpc.main <project_id>/<vpc_id>
```

예시:

```bash
terraform import cloudia_vpc.main 1/42
```

import 키 형식: `<project_id>/<vpc_id>`

## 관련 항목

- [subnet.md](subnet.md) — VPC 안의 서브넷
- [security_group.md](security_group.md) — 사용자 정의 보안그룹
- [default_security_group.md](default_security_group.md) — VPC 자동 생성 기본 보안그룹
- [floating_ip.md](floating_ip.md) — 공인 IP 할당
- [../guides/getting-started.md](../guides/getting-started.md)
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/vpc.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
