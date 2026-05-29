# cloudia_floating_ip

프로젝트의 public IP 풀에서 플로팅 IP를 할당하고, 인스턴스 또는 내부 IP에 bind/unbind하는 리소스입니다.

## 예제

인스턴스에 바인딩하는 경우:

```hcl
resource "cloudia_floating_ip" "web" {
  vpc_id      = cloudia_vpc.main.id
  name        = "web-fip"
  description = "public entrypoint"

  binding = {
    resource_type = "INSTANCE"
    resource_id   = "<your-instance-id>"
    resource_ip   = "10.20.1.10"
  }
}
```

unbound 상태(binding 생략):

```hcl
resource "cloudia_floating_ip" "reserve" {
  vpc_id      = cloudia_vpc.main.id
  name        = "reserve-fip"
  description = "unbound — reserved for future use"
}
```

특정 public IP를 고정 할당하는 경우:

```hcl
resource "cloudia_floating_ip" "fixed" {
  vpc_id      = cloudia_vpc.main.id
  name        = "fixed-fip"
  ip_address  = "<your-public-ip>"
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `vpc_id` | 상위 VPC ID | 필수 | 변경 시 RequiresReplace |
| `name` | 플로팅 IP 이름 | 필수 | |
| `description` | 플로팅 IP 설명 | 선택 | |
| `ip_address` | 할당받을 public IP 주소. 생략 시 백엔드가 자동 할당 | 선택 | 변경 시 기존 IP release + 새 IP 할당 |
| `binding` | 바인딩 대상. 생략 시 unbound 상태 유지 | 선택 | 아래 중첩 인자 참고 |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

### binding 중첩 인자

| 인자 | 설명 | 필수 |
|------|------|------|
| `resource_type` | 바인딩 대상 유형. `INSTANCE` 또는 `IP` | 필수 |
| `resource_id` | 대상 리소스 ID. `INSTANCE` 타입일 때 필수, `IP` 타입일 때 생략 | 선택 |
| `resource_ip` | VPC 내부 IPv4 주소. `INSTANCE`와 `IP` 모두 필수 | 선택 |

**읽기 전용 출력값**: `id`, `public_ip_id`, `linked_resource`, `network_name`, `created_at`, `updated_at`

## 운영 노트

- **binding 생략 = unbound**: `binding` 블록을 생략하면 플로팅 IP가 unbound 상태로 할당됩니다. 나중에 HCL에 `binding`을 추가하면 bind됩니다.
- **ip_address 변경 시 교체**: `ip_address`를 변경하면 백엔드가 기존 public IP를 release하고 새 IP를 할당합니다(`public_ip_id` 값이 변경됩니다). **바인딩된 상태에서 `ip_address` 변경은 허용되지 않습니다** — 먼저 `binding = null`로 unbind 후 변경하세요.
- **project public_ip_quota 소모**: 플로팅 IP 생성 시마다 프로젝트의 `public_ip_quota`가 1씩 소모됩니다. VPC 생성 시에도 vRouter용 IP가 1개 자동 할당됩니다. 할당량 초과 시 API 에러가 발생합니다.
- **vpc_id RequiresReplace**: API는 unbound 플로팅 IP의 VPC 이동을 지원하지만, 이 provider는 `vpc_id` 변경 시 state 안정성을 위해 destroy 후 재생성합니다. VPC를 이동하려면 `terraform destroy` 후 재생성하세요.
- **linked_resource 읽기 전용**: `linked_resource`는 서버가 포맷하는 문자열(`"<instance-name> (ID: <id>): <ip>"`)입니다. 바인딩된 인스턴스의 이름이 바뀌면 이 값도 변경됩니다. HCL에서 직접 관리하지 마세요.

## Import

```bash
terraform import cloudia_floating_ip.web <project_id>/<vpc_id>/<floating_ip_id>
```

예시:

```bash
terraform import cloudia_floating_ip.web 1/42/7
```

import 키 형식: `<project_id>/<vpc_id>/<floating_ip_id>`

## 관련 항목

- [vpc.md](vpc.md) — 상위 VPC 리소스
- [subnet.md](subnet.md) — 서브넷 리소스
- [security_group.md](security_group.md) — 사용자 정의 보안그룹
- [default_security_group.md](default_security_group.md) — VPC 기본 보안그룹
- [../guides/getting-started.md](../guides/getting-started.md)
- [../guides/import.md](../guides/import.md)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/floating_ip.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
