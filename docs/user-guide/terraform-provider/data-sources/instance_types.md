# cloudia_instance_types (데이터소스)

인스턴스 타입 목록을 조회합니다. `gpu_capable`·`capability`·`name`·`lookup_id` 필터를 사용할 수 있습니다. 단일 타입을 이름·ID로 직접 조회하려면 [instance_type.md](instance_type.md)를 사용하세요.

## 예제

```hcl
# GPU 지원 타입만 조회
data "cloudia_instance_types" "gpu_only" {
  gpu_capable = true
}

output "gpu_type_names" {
  value = data.cloudia_instance_types.gpu_only.items[*].name
}

# 이름으로 필터 (완전 일치)
data "cloudia_instance_types" "general" {
  name = "general-purpose"
}
```

> 카탈로그는 환경마다 다릅니다. 사용 가능한 타입 목록은 운영자나 콘솔에서 확인하세요.

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `gpu_capable` | 선택 | GPU 지원 타입만 반환. |
| `capability` | 선택 | Capability 문자열 필터. |
| `name` | 선택 | 이름 완전 일치 필터. |
| `lookup_id` | 선택 | ID 필터. |

## 속성

컬렉션 필드: **`items`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `items` | List(Object) | 필터 후 인스턴스 타입 목록. |
| `items[*].id` | String | 인스턴스 타입 ID. |
| `items[*].name` | String | 인스턴스 타입 이름. |
| `items[*].vcpu_number` | Number | vCPU 수. |
| `items[*].memory_total` | Number | 메모리 (MiB). |
| `items[*].gpu_capable` | Boolean | GPU 지원 여부. |
| `items[*].max_interfaces` | Number | 최대 NIC 수. |
| `items[*].max_ips_per_interface` | Number | NIC당 최대 IP 수. |
| `items[*].capability` | Object | GPU/NPU 하드웨어 능력 정보. |
| `total_count` | Number | 반환된 인스턴스 타입 수. |

## 관련 항목

- [instance_type.md](instance_type.md) — 단일 인스턴스 타입 조회
- [accelerator_gpus.md](accelerator_gpus.md) — GPU vendor/product 카탈로그
- [accelerator_npus.md](accelerator_npus.md) — NPU vendor/product 카탈로그
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/instance_types.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
