# cloudia_storage_domains (데이터소스)

사용 가능한 스토리지 도메인 목록을 조회합니다. `cloudia_volume`, `cloudia_image`, `cloudia_nfs_file_system`, `cloudia_virtiofs_file_system` 등 `storage_domain_id`가 필요한 리소스에서 동적으로 값을 찾을 때 사용합니다. `name` 또는 `type` 필터로 결과를 좁힐 수 있습니다.

## 예제

```hcl
# 전체 스토리지 도메인 목록
data "cloudia_storage_domains" "all" {}

resource "cloudia_volume" "data" {
  name              = "demo-data"
  size_gib          = 100
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
}

# 타입 필터 (VIRTIOFS용 LOCAL 타입만)
data "cloudia_storage_domains" "local_only" {
  type = "LOCAL"
}

locals {
  local_sd = data.cloudia_storage_domains.local_only.items
}

resource "cloudia_virtiofs_file_system" "fs" {
  name              = "host-local-fs"
  storage_domain_id = local.local_sd[0].id
}

output "storage_domain_ids" {
  value = [for sd in data.cloudia_storage_domains.all.items : sd.id]
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `name` | 선택 | 정확히 일치하는 이름 필터. 생략 시 전체 목록 반환. |
| `type` | 선택 | 스토리지 도메인 타입 필터. 허용값: `LOCAL`, `GFS2`, `NFS`, `CEPH`. |

## 속성

컬렉션 필드: **`items`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 데이터소스 식별자 (고정값 `storage-domains`). |
| `items` | List(Object) | 필터 후 스토리지 도메인 목록 (ID 오름차순 정렬). |
| `items[*].id` | String | 스토리지 도메인 ID. |
| `items[*].name` | String | 스토리지 도메인 이름. |
| `items[*].type` | String | 스토리지 도메인 타입 (`LOCAL` / `GFS2` / `NFS` / `CEPH`). |
| `items[*].status` | String | 스토리지 도메인 상태 (`UP` / `CREATING`). |
| `items[*].deletable` | Boolean | 현재 삭제 가능 여부. |
| `items[*].deleted` | Boolean | 소프트 삭제 여부. |
| `items[*].created_at` | String | 생성 시각 (RFC3339). |
| `items[*].updated_at` | String | 마지막 수정 시각 (RFC3339). |
| `total_count` | Number | 필터 후 반환된 스토리지 도메인 수. |

## 관련 항목

- [file_system.md](file_system.md) — 단일 파일시스템 조회
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/storage_domains.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
