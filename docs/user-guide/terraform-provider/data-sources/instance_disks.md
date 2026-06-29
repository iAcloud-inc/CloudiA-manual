# cloudia_instance_disks (데이터소스)

인스턴스에 부착된 디스크 목록(부팅 디스크 + 데이터 디스크)을 조회합니다. `is_boot` 필드로 부팅 디스크를 구별할 수 있습니다. 정렬 순서: 부팅 디스크 우선, 이후 부팅 순서(boot_order) 오름차순, ID 오름차순.

## 예제

```hcl
data "cloudia_instance_disks" "demo" {
  instance_id = cloudia_instance.demo.id
}

# 부팅 디스크 크기 (GiB)
output "boot_disk_size_gib" {
  value = one([
    for d in data.cloudia_instance_disks.demo.disks :
    d.size_gib if d.is_boot
  ])
}

# 데이터 디스크 ID 목록
output "data_disk_ids" {
  value = [
    for d in data.cloudia_instance_disks.demo.disks :
    d.block_device_id if !d.is_boot
  ]
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `instance_id` | 필수 | 디스크를 조회할 인스턴스 ID. |
| `project_id` | 선택 | 프로젝트 ID. 생략 시 provider 설정값 사용. |

## 속성

컬렉션 필드: **`disks`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `disks` | List(Object) | 부착된 디스크 목록. 부팅 디스크가 항상 첫 번째. |
| `disks[*].id` | String | 디스크 GuestHardware ID. |
| `disks[*].is_boot` | Boolean | 부팅 디스크 여부. |
| `disks[*].size_gib` | Number | 디스크 크기 (GiB). |
| `disks[*].size_mib` | Number | 디스크 크기 (MiB, 백엔드 원본값). |
| `disks[*].block_device_id` | String | 블록 디바이스 (볼륨) ID. 없으면 null. |
| `disks[*].boot_order` | Number | BIOS/UEFI 부팅 우선순위. 0이면 데이터 디스크. |
| `disks[*].disk_index` | Number | 응답 내 위치 인덱스 (0부터 시작). |
| `total_count` | Number | 반환된 디스크 수. |

## 관련 항목

- [instance.md](instance.md) — 인스턴스 단일 조회 (`data_volume_ids` 포함)
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스
- [../resources/instance_snapshot.md](../resources/instance_snapshot.md) — 인스턴스 스냅샷

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/instance_disks.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
