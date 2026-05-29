# cloudia_instance_interface (데이터소스)

인스턴스의 NIC(네트워크 인터페이스) 한 개를 조회합니다. `lookup_id`(NIC ID 직접 지정) 또는 `is_default`(기본 NIC 선택) 중 정확히 하나를 지정해야 합니다(ExactlyOneOf). 인스턴스의 전체 NIC 목록은 [instance.md](instance.md)의 `network_interfaces` 속성을 사용하세요.

## 예제

```hcl
# 기본 NIC 조회
data "cloudia_instance_interface" "primary" {
  instance_id = cloudia_instance.demo.id
  is_default  = true
}

output "primary_ipv4" {
  value = data.cloudia_instance_interface.primary.ipv4_address
}

output "primary_mac" {
  value = data.cloudia_instance_interface.primary.mac_address
}

# NIC ID로 직접 조회
data "cloudia_instance_interface" "by_id" {
  instance_id = cloudia_instance.demo.id
  lookup_id   = "100"
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `instance_id` | 필수 | NIC를 조회할 인스턴스 ID. |
| `lookup_id` | 선택 (ExactlyOneOf) | 조회할 NIC ID. `is_default`와 둘 중 하나만 지정. |
| `is_default` | 선택 (ExactlyOneOf) | `true` 지정 시 기본 NIC를 조회. `lookup_id`와 둘 중 하나만 지정. 기본 NIC가 여러 개면 에러. |
| `project_id` | 선택 | 프로젝트 ID. 생략 시 provider 설정값 사용. |

## 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 조회된 NIC ID. |
| `ipv4_address` | String | NIC IPv4 주소 (DHCP/자동 할당). |
| `ipv4_gateway` | String | IPv4 게이트웨이. |
| `ipv4_netmask` | String | IPv4 넷마스크. |
| `ipv4_dns` | String | IPv4 DNS 서버. |
| `mac_address` | String | NIC MAC 주소 (백엔드 자동 할당). |
| `interface_name` | String | 게스트 OS 내부에서 보이는 인터페이스 이름. |
| `is_default_nic` | Boolean | 기본 NIC 여부. |
| `subnet_id` | String | NIC가 속한 서브넷 ID. |
| `security_group_ids` | Set(String) | NIC에 연결된 보안그룹 ID 세트. |
| `managed` | Boolean | 시스템 관리 NIC 여부. |

## 관련 항목

- [instance.md](instance.md) — 인스턴스 단일 조회 (network_interfaces 전체 목록 포함)
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/instance_interface.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
