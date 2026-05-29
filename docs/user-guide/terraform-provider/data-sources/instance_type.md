# cloudia_instance_type (데이터소스)

이름 또는 ID로 인스턴스 타입 한 개를 조회합니다. 조회한 `vcpu_number`·`memory_total` 값을 `cloudia_instance` 리소스에 미러하면 카탈로그 프리셋을 그대로 사용할 수 있습니다. 필터를 걸어 여러 타입을 조회하려면 [instance_types.md](instance_types.md)를 사용하세요.

## 예제

```hcl
data "cloudia_instance_type" "small" {
  name = "s1.small"
}

# 카탈로그 프리셋을 인스턴스에 미러
resource "cloudia_instance" "demo" {
  vcpu_number  = data.cloudia_instance_type.small.vcpu_number
  memory_total = data.cloudia_instance_type.small.memory_total
  # ...
}
```

> 카탈로그는 환경마다 다릅니다. 사용 가능한 타입 목록은 운영자나 콘솔에서 확인하세요.

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `lookup_id` | 선택 | 조회할 인스턴스 타입 ID. |
| `name` | 선택 | 조회할 인스턴스 타입 이름. |

`lookup_id`와 `name` 중 하나를 지정합니다.

## 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 조회된 인스턴스 타입 ID. |
| `vcpu_number` | Number | vCPU 수. |
| `memory_total` | Number | 메모리 (MiB). |
| `gpu_capable` | Boolean | GPU 지원 여부. |
| `max_interfaces` | Number | 최대 NIC 수. |
| `max_ips_per_interface` | Number | NIC당 최대 IP 수. |
| `capability` | Object | GPU/NPU 하드웨어 능력 정보. |
| `capability.gpu_device_info` | Object | GPU passthrough 정보. GPU 미지원 타입은 null. |
| `capability.npu_device_info` | Object | NPU passthrough 정보. NPU 미지원 타입은 null. |

## 관련 항목

- [instance_types.md](instance_types.md) — 필터로 여러 인스턴스 타입 조회
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스 (vcpu_number·memory_total 사용)
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/instance_type.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
