# Singular vs Plural 데이터소스 선택하기

> 원본(영문): `terraform-provider-cloudia/docs/guides/data-sources.md`. 한국어 문서와 차이가 있으면 영문 문서를 우선합니다.
>
> 본 문서의 예시는 Cloud:iA dev/test 환경 기준입니다. `<your-...>` 플레이스홀더와 실제 값 매핑은 [가이드 홈의 Reference 표](../README.md#reference-table)를 참고하세요.

Cloud:iA provider는 같은 리소스 타입에 대해 **singular**(단일 조회)와 **plural**(컬렉션 조회) 두 가지 data source를 제공합니다. 다음 두 질문으로 선택하세요.

1. 정확히 **하나**의 항목이 필요한가, 아니면 **여러 개**가 필요한가?
2. 결과를 다른 리소스의 **`id` 참조**로 쓸 것인가, 아니면 **`for_each` / output**에 흘려넣을 것인가?

## 한 줄 요약

| 용도 | 권장 형태 |
|---|---|
| `resource.X.id = data.Y.id` 단일 참조 | **singular** (`cloudia_image`, `cloudia_instance` 등) |
| `for_each = toset(data.cloudia_images.all.items[*].id)` 컬렉션 루프 | **plural** (`cloudia_images`, `cloudia_instances` 등) |
| Output / 대시보드 / 필터 조합 | **plural** |
| Plan 안정성 (여러 매칭은 명확히 실패하길 원함) | **singular** (`ExactlyOneOf` 검증) |

## 페어 인덱스

| Singular | Plural | 비고 |
|---|---|---|
| `cloudia_image` | `cloudia_images` | OS image. project scope |
| `cloudia_instance` | `cloudia_instances` | 인스턴스. plural은 `name_prefix` / `power_state` 필터 지원 |
| `cloudia_instance_type` | `cloudia_instance_types` | 카탈로그. plural은 `gpu_capable` / `capability` 필터 지원 |
| `cloudia_project` | `cloudia_projects` | 프로젝트. admin alias 필요할 수 있음 |

다음 data source는 컬렉션 전용입니다 (singular 짝 없음): `cloudia_instance_disks`, `cloudia_instance_snapshots`, `cloudia_secure_types`, `cloudia_storage_domains`. 단일 항목이 필요하면 HCL `for` / `one()` 함수로 결과를 좁히세요.

> **컬렉션 속성 이름은 data source마다 다릅니다.** 일률적으로 `items`가 아닙니다. 반환되는 목록 속성 이름은 다음과 같습니다.
>
> | data source | 목록 속성 | 개수 속성 |
> |---|---|---|
> | `cloudia_instances` | `instances` | `total_count` |
> | `cloudia_instance_disks` | `disks` | `total_count` |
> | `cloudia_instance_snapshots` | `snapshots` | `total_count` |
> | `cloudia_compute_hosts` | `hosts` | `total_count` |
> | `cloudia_secure_types` | `values` (문자열 목록) | — |
> | `cloudia_images` · `cloudia_instance_types` · `cloudia_storage_domains` · `cloudia_projects` · `cloudia_accelerator_gpus` · `cloudia_accelerator_npus` | `items` | `total_count` |
>
> 개수는 `count`가 아니라 `total_count`입니다.

`cloudia_instance_interface`는 1:1 매핑이 가장 흔한 사용 패턴이라 컬렉션 대신 **selector singular** 형태(`lookup_id` ⊕ `is_default`, `ExactlyOneOf`)로 노출됩니다.

## 예시

### 단일 참조 — singular

다른 리소스의 속성에 `id`를 박을 때 씁니다. 정확히 하나만 매칭되도록 보장하므로 plan 안정성이 좋습니다 (여러 매칭이면 명확히 실패).

```hcl
data "cloudia_image" "ubuntu" {
  name = "<your-image-name>"   # 예: ubuntu-24.04
}

resource "cloudia_instance" "demo" {
  image_id = data.cloudia_image.ubuntu.id
  # ...
}
```

### 컬렉션 루프 — plural

`for_each`로 동적 리소스를 만들 때 씁니다. plural data source는 client-side AND 조합 필터를 지원합니다.

```hcl
data "cloudia_instances" "running" {
  project_id  = var.project_id   # 예: dev/test의 25
  power_state = "RUNNING"
}

output "running_instance_names" {
  value = data.cloudia_instances.running.instances[*].name
}
```

### Singular가 없을 때 — plural을 좁히기

`cloudia_instance_disks`처럼 singular 짝이 없는 data source는 HCL 표현식으로 결과를 좁힙니다.

```hcl
data "cloudia_instance_disks" "demo" {
  instance_id = cloudia_instance.demo.id
}

locals {
  boot_disk = one([for d in data.cloudia_instance_disks.demo.disks : d if d.is_boot])
}
```

## 컬렉션 전용 data source 사용 예

singular 짝이 없는 4종 + selector singular 1종을 어떻게 쓰는지 빠르게.

### `cloudia_instance_disks` — 인스턴스에 붙은 모든 디스크

```hcl
data "cloudia_instance_disks" "demo" {
  instance_id = cloudia_instance.demo.id
}

# 부팅 디스크 1개 뽑기
output "boot_disk_size_gib" {
  value = one([for d in data.cloudia_instance_disks.demo.disks : d.size_gib if d.is_boot])
}

# 추가 데이터 볼륨 개수
output "data_volume_count" {
  value = length([for d in data.cloudia_instance_disks.demo.disks : d if !d.is_boot])
}
```

### `cloudia_instance_interface` — selector singular (1:1)

`lookup_id` 또는 `is_default` 둘 중 하나만 (ExactlyOneOf). 기본 NIC의 IP를 노출하는 가장 흔한 패턴:

```hcl
data "cloudia_instance_interface" "primary" {
  instance_id = cloudia_instance.demo.id
  is_default  = true
}

output "primary_ipv4" {
  value = data.cloudia_instance_interface.primary.ipv4_address
}
```

### `cloudia_instance_snapshots` — 인스턴스 스냅샷 목록

```hcl
data "cloudia_instance_snapshots" "demo" {
  instance_id = cloudia_instance.demo.id
}

# 가장 최근 스냅샷 1개의 ID
locals {
  latest_snapshot_id = element(
    sort([for s in data.cloudia_instance_snapshots.demo.snapshots : s.id]),
    length(data.cloudia_instance_snapshots.demo.snapshots) - 1,
  )
}
```

### `cloudia_secure_types` — 인스턴스 보안 등급 카탈로그

`cloudia_instance.secure_type`에 넣을 값 후보를 조회.

```hcl
data "cloudia_secure_types" "all" {}

output "available_secure_types" {
  value = data.cloudia_secure_types.all.values
}
```

### `cloudia_storage_domains` — 사용 가능한 스토리지 도메인

`cloudia_volume.storage_domain_id`, `cloudia_image.storage_domain_id`에 넣을 값 후보.

```hcl
data "cloudia_storage_domains" "all" {}

# LOCAL 타입만 필터링 (VIRTIOFS는 CEPH만 불가, 보통 LOCAL 사용)
locals {
  local_sd = [for sd in data.cloudia_storage_domains.all.items : sd if sd.type == "LOCAL"]
}
```

### `cloudia_file_system` — 단일 파일시스템 조회 (NFS/VIRTIOFS 공통)

NFS와 VIRTIOFS는 별도 리소스(`cloudia_nfs_file_system`/`cloudia_virtiofs_file_system`)지만 조회는 공통 data source 하나로 통합됩니다.

```hcl
data "cloudia_file_system" "shared" {
  lookup_id = var.shared_fs_id
}

output "fs_kind" {
  value = data.cloudia_file_system.shared.type   # "NFS" 또는 "VIRTIOFS"
}
```

## 자주 하는 실수

- **단일 참조에 plural을 쓰는 경우** — `data.cloudia_images.all.items[0].id`처럼 인덱스로 한 개를 뽑으면, 정렬 순서나 필터가 바뀔 때 plan이 흔들립니다. singular `cloudia_image`를 쓰세요.
- **여러 개를 다루는 작업에 singular를 쓰는 경우** — singular는 `ExactlyOneOf`로 검증하므로, `count` / `for_each`로 여러 번 호출하는 패턴이 어색합니다. plural이 자연스러운 선택입니다.
- **plural에 `count`를 쓰는 경우** — `data.cloudia_instances.X.total_count`는 필터 적용 후 결과 개수를 반환합니다. preflight validation에 유용합니다.

## 함께 보기

- 전체 data source 목록: Terraform Registry sidebar의 Data Sources 섹션
- [시작하기 (Getting Started)](getting-started.md) §5 Image 조회
