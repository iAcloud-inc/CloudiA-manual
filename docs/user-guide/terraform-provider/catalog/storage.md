# 스토리지 (한국어 카탈로그)

블록 볼륨, OS 이미지, 공유 파일시스템 리소스 및 관련 data source.

> 본 카탈로그는 **최소 동작 예제만** 제공합니다. 전체 schema와 자세한 가이드는 영문 docs를 참고하세요.

## 페이지 인덱스

### 리소스
- [`cloudia_volume`](#volume)
- [`cloudia_image`](#image)
- [`cloudia_image_clone`](#image-clone)
- [`cloudia_nfs_file_system`](#nfs-file-system)
- [`cloudia_virtiofs_file_system`](#virtiofs-file-system)

### 데이터소스
- [`cloudia_image` / `cloudia_images`](#ds-image)
- [`cloudia_file_system`](#ds-file-system)
- [`cloudia_storage_domains`](#ds-storage-domains)

---

<a id="volume"></a>
## `cloudia_volume`

블록 볼륨. 인스턴스에 attach해 추가 디스크로 사용.

```hcl
data "cloudia_storage_domains" "all" {}

resource "cloudia_volume" "data" {
  name              = "demo-data"
  size_gib          = 100
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
}
```

> **In-place grow만 지원**, shrink는 plan 단계에서 거부됩니다. 줄이려면 destroy + recreate. `description`도 update 불가 (ADR-0017).

**Import**: `terraform import cloudia_volume.data <project_id>/<volume_id>`

**전체 schema**: [영문 docs/resources/volume.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/volume.md)

---

<a id="image"></a>
## `cloudia_image`

OS 이미지(qcow2) 업로드.

```hcl
resource "cloudia_image" "ubuntu_custom" {
  file_path         = "/path/to/ubuntu-custom.qcow2"
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
}
```

> 백엔드가 `virt-inspector`로 검증하므로 부팅 가능한 x86_64 cloud image여야 합니다 (빈 qcow2는 CLERR-402004로 거부). `file_path`는 RequiresReplace.

**Import**: `terraform import cloudia_image.ubuntu_custom <project_id>/<image_id>` (`file_path`/`storage_domain_id`는 `ImportStateVerifyIgnore`)

**전체 schema**: [영문 docs/resources/image.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/image.md)

---

<a id="image-clone"></a>
## `cloudia_image_clone`

기존 이미지를 다른 스토리지 도메인으로 복제 (LOCAL → CEPH 등).

```hcl
resource "cloudia_image_clone" "ubuntu_on_ceph" {
  source_image_id   = cloudia_image.ubuntu_custom.id
  storage_domain_id = data.cloudia_storage_domains.all.items[1].id   # CEPH 등 별도 SD
}
```

> 양쪽 모두 RequiresReplace. 클론 결과는 새 image ID로 노출되므로 `cloudia_instance.image_id`에는 이 리소스의 `.id`를 넘기세요.

**Import**: `terraform import cloudia_image_clone.ubuntu_on_ceph <project_id>/<image_id>`

**전체 schema**: [영문 docs/resources/image_clone.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/image_clone.md)

---

<a id="nfs-file-system"></a>
## `cloudia_nfs_file_system`

NFS 공유 파일시스템. 여러 인스턴스에서 동시 mount 가능.

```hcl
resource "cloudia_nfs_file_system" "shared" {
  name              = "shared-nfs"
  size_gib          = 200
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
  network_id        = cloudia_vpc.main.id

  vnic = [{
    subnet_id          = cloudia_subnet.public.id
    security_group_ids = [cloudia_security_group.nfs.id]
    # ipv4_address       = "10.20.1.50"   # 선택 (생략 시 자동 할당)
    is_default_nic     = true
  }]
}
```

> `size_gib` grow만 가능, shrink 거부. `vnic`/`storage_domain_id`/`network_id`는 RequiresReplace.

**Import**: `terraform import cloudia_nfs_file_system.shared <project_id>/<file_system_id>`

**전체 schema**: [영문 docs/resources/nfs_file_system.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/nfs_file_system.md)

---

<a id="virtiofs-file-system"></a>
## `cloudia_virtiofs_file_system`

VIRTIOFS host-local 공유 파일시스템. NFS와 달리 host 로컬 디렉터리라 같은 host의 인스턴스끼리만 공유 가능.

```hcl
resource "cloudia_virtiofs_file_system" "host_local" {
  name              = "host-local-fs"
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id   # LOCAL 타입만
}
```

> `storage_domain_id`는 **LOCAL / GFS2 / NFS** 타입만 허용 — CEPH는 plan에서 거부됩니다.

**Import**: `terraform import cloudia_virtiofs_file_system.host_local <project_id>/<file_system_id>`

**전체 schema**: [영문 docs/resources/virtiofs_file_system.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/virtiofs_file_system.md)

---

<a id="ds-image"></a>
## `cloudia_image` / `cloudia_images` (data source)

이미지 조회.

```hcl
# 단일 (이름)
data "cloudia_image" "ubuntu" {
  name = "ubuntu-24.04"
}

# 컬렉션
data "cloudia_images" "all" {}

output "image_names" {
  value = data.cloudia_images.all.items[*].name
}
```

**전체 schema**: [영문 docs/data-sources/image.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/image.md), [images.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/images.md)

---

<a id="ds-file-system"></a>
## `cloudia_file_system` (data source)

NFS와 VIRTIOFS 공통 단일 조회. `kind` 속성으로 어떤 종류인지 알 수 있음.

```hcl
data "cloudia_file_system" "shared" {
  lookup_id = cloudia_nfs_file_system.shared.id
}

output "fs_kind" {
  value = data.cloudia_file_system.shared.kind   # "NFS" 또는 "VIRTIOFS"
}
```

**전체 schema**: [영문 docs/data-sources/file_system.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/file_system.md)

---

<a id="ds-storage-domains"></a>
## `cloudia_storage_domains` (data source, 컬렉션 전용)

사용 가능한 스토리지 도메인 목록. `cloudia_volume.storage_domain_id` 등에 넣을 값을 동적으로 찾을 때 사용.

```hcl
data "cloudia_storage_domains" "all" {}

# LOCAL 타입만 필터 (VIRTIOFS용)
locals {
  local_sd = [for sd in data.cloudia_storage_domains.all.items : sd if sd.type == "LOCAL"]
}

resource "cloudia_virtiofs_file_system" "fs" {
  storage_domain_id = local.local_sd[0].id
  # ...
}
```

**전체 schema**: [영문 docs/data-sources/storage_domains.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/storage_domains.md)
