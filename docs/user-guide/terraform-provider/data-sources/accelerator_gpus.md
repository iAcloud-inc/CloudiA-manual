# cloudia_accelerator_gpus (데이터소스)

호스트 인벤토리에 등록된 GPU `(vendor_id, product_id)` 고유 쌍 목록과 가용량을 조회합니다. `cloudia_instance.hardware_gpu`의 `vendor_id`·`product_id`를 결정하거나, 용량을 확인하고 싶을 때 사용합니다.

GPU 용량 확인은 `pci_count_avail` 기준을 사용하세요. `card_root_count_avail`은 현재 백엔드에서 null로 반환될 수 있습니다.

## 예제

```hcl
data "cloudia_accelerator_gpus" "all" {}

output "gpu_pairs" {
  value = [
    for g in data.cloudia_accelerator_gpus.all.items :
    "${g.vendor_id}:${g.product_id}"
  ]
}

# 특정 GPU 가용량 확인
locals {
  a100 = one([
    for g in data.cloudia_accelerator_gpus.all.items :
    g if g.vendor_id == "10de" && g.product_id == "20b0"
  ])
}

output "a100_pci_avail" {
  value = local.a100 == null ? 0 : local.a100.pci_count_avail
}
```

## 인자

이 데이터소스는 별도 인자가 없습니다.

## 속성

컬렉션 필드: **`items`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `items` | List(Object) | GPU 고유 쌍 목록 (`vendor_id`, `product_id` ASCII 오름차순). |
| `items[*].vendor_id` | String | PCI 벤더 ID (16진수, 예: `10de`는 NVIDIA). |
| `items[*].vendor_name` | String | 벤더 이름 (없으면 null). |
| `items[*].product_id` | String | PCI 제품 ID (16진수, 벤더 기준). |
| `items[*].product_name` | String | 제품 이름 (없으면 null). |
| `items[*].pci_count_total` | Number | 전체 PCI BDF 수 (모든 호스트 합산). |
| `items[*].pci_count_avail` | Number | 여유 PCI BDF 수 (현재 인스턴스가 사용 중이지 않은 것). |
| `items[*].card_root_count_total` | Number | 카드 루트 총 수. 현재 백엔드에서 null일 수 있음. |
| `items[*].card_root_count_avail` | Number | 여유 카드 루트 수. 현재 백엔드에서 null일 수 있음. |
| `total_count` | Number | 반환된 GPU 고유 쌍 수. |

## 관련 항목

- [accelerator_npus.md](accelerator_npus.md) — NPU 카탈로그 (`card_root_count_avail` 정상 제공)
- [instance_types.md](instance_types.md) — GPU 지원 인스턴스 타입 조회 (`gpu_capable` 필터)
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스 (`hardware_gpu`)

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/accelerator_gpus.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
