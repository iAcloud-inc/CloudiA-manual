# cloudia_accelerator_npus (데이터소스)

호스트 인벤토리에 등록된 NPU `(vendor_id, product_id)` 고유 쌍 목록과 카드 가용량을 조회합니다. `cloudia_instance.hardware_npu`의 `vendor_id`·`product_id`를 결정하거나, 용량을 확인하고 싶을 때 사용합니다.

NPU는 카드 하나에 여러 PCI가 묶이는 multi-endpoint 구조입니다. `card_root_count_avail`(여유 카드 루트 수)이 용량 확인의 기준입니다. `pci_count_avail`은 개별 PCI BDF 수로, NPU 할당 단위(`unit_count` = 카드 루트)와 다릅니다.

## 예제

```hcl
data "cloudia_accelerator_npus" "all" {}

output "npu_pairs" {
  value = [
    for n in data.cloudia_accelerator_npus.all.items :
    "${n.vendor_id}:${n.product_id}"
  ]
}

# 특정 NPU 카드 가용량 확인
locals {
  atom = one([
    for n in data.cloudia_accelerator_npus.all.items :
    n if n.vendor_id == "1eff" && n.product_id == "rbln-ca22"
  ])
}

output "atom_cards_avail" {
  value = local.atom == null ? 0 : local.atom.card_root_count_avail
}
```

## 인자

이 데이터소스는 별도 인자가 없습니다.

## 속성

컬렉션 필드: **`items`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `items` | List(Object) | NPU 고유 쌍 목록 (`vendor_id`, `product_id` ASCII 오름차순). |
| `items[*].vendor_id` | String | PCI 벤더 ID (16진수). |
| `items[*].vendor_name` | String | 벤더 이름 (없으면 null). |
| `items[*].product_id` | String | PCI 제품 ID (16진수, 벤더 기준). |
| `items[*].product_name` | String | 제품 이름 (없으면 null). |
| `items[*].card_root_count_total` | Number | 전체 카드 루트 수 (모든 호스트 합산). |
| `items[*].card_root_count_avail` | Number | 여유 카드 루트 수. NPU 용량 확인의 기준 필드. |
| `items[*].pci_count_total` | Number | 전체 PCI BDF 수 (모든 호스트 합산). |
| `items[*].pci_count_avail` | Number | 여유 PCI BDF 수. |
| `total_count` | Number | 반환된 NPU 고유 쌍 수. |

## 관련 항목

- [accelerator_gpus.md](accelerator_gpus.md) — GPU 카탈로그 (GPU는 `pci_count_avail` 기준)
- [instance_types.md](instance_types.md) — GPU/NPU 지원 인스턴스 타입 조회
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스 (`hardware_npu`)

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/accelerator_npus.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
