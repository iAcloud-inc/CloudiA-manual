# 컴퓨트 (한국어 카탈로그)

가상머신 인스턴스와 그 부속 리소스(SSH 키, 스냅샷, 배치 그룹) 및 관련 data source.

> 본 카탈로그는 **최소 동작 예제만** 제공합니다. 전체 schema와 자세한 가이드는 영문 docs를 참고하세요.

## 페이지 인덱스

### 리소스
- [`cloudia_instance`](#instance)
- [`cloudia_ssh_key`](#ssh-key)
- [`cloudia_affinity_group`](#affinity-group)
- [`cloudia_instance_snapshot`](#instance-snapshot)
- [`cloudia_instance_snapshot_restore`](#instance-snapshot-restore)

### 데이터소스
- [`cloudia_compute_hosts`](#ds-compute-hosts)
- [`cloudia_accelerator_gpus`](#ds-accelerator-gpus)
- [`cloudia_accelerator_npus`](#ds-accelerator-npus)
- [`cloudia_instance` / `cloudia_instances`](#ds-instance)
- [`cloudia_instance_type` / `cloudia_instance_types`](#ds-instance-type)
- [`cloudia_instance_disks`](#ds-instance-disks)
- [`cloudia_instance_interface`](#ds-instance-interface)
- [`cloudia_instance_snapshots`](#ds-instance-snapshots)
- [`cloudia_ssh_key`](#ds-ssh-key)
- [`cloudia_secure_types`](#ds-secure-types)

---

<a id="instance"></a>
## `cloudia_instance`

가상머신 인스턴스. 가장 큰 리소스입니다.

### 최소 예제

```hcl
data "cloudia_image" "ubuntu" {
  name = "<your-image-name>"
}

resource "cloudia_instance" "demo" {
  name         = "demo-vm"
  network_id   = cloudia_vpc.main.id
  vcpu_number  = 2
  memory_total = 4096   # MiB

  image_id = data.cloudia_image.ubuntu.id

  vnic = [
    {
      subnet_id          = cloudia_subnet.public.id
      security_group_ids = [cloudia_security_group.default.id]
      is_default_nic     = true
    },
  ]

  cloud_init = {
    username = "appuser"
    password = "<your-instance-password>"
  }
}
```

`cloud_init.username`은 일반 로그인 사용자명으로 잡으세요. `root`, `admin`, `ubuntu`, `centos` 같은 예약 이름은 backend가 거부합니다.

### Sizing — 직접 입력

`vcpu_number` + `memory_total` (MiB) 두 값으로 사이즈 결정. 카탈로그 preset을 그대로 쓰려면 `cloudia_instance_type` data source로 미러:

```hcl
data "cloudia_instance_type" "ref" { name = "<your-instance-type-name>" }

resource "cloudia_instance" "from_catalog" {
  vcpu_number  = data.cloudia_instance_type.ref.vcpu_number
  memory_total = data.cloudia_instance_type.ref.memory_total
  # ...
}
```

> ⚠️ **Update 동작 주의**: 변경하는 필드에 따라 무중단(LIVE) / 자동 stop-update-run(STOP, 다운타임) / 재생성(REPLACE) 중 하나로 분기됩니다. 운영 환경에서는 **반드시 `tofu plan`으로 어떤 분기인지 확인**한 뒤 apply하세요. 정확한 필드별 매핑(LIVE/STOP/REPLACE 분류, GPU/NPU 설정, cloud-init, boot disk 정책 등) **상세 가이드는 추후 작성 예정**입니다.

### Import

```bash
terraform import cloudia_instance.demo <project_id>/<instance_id>
```

**전체 schema (모든 옵션)**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ssh-key"></a>
## `cloudia_ssh_key`

SSH 공개키 등록. 인스턴스에서는 `cloud_init.ssh_key_ids`로 연결.

```hcl
resource "cloudia_ssh_key" "me" {
  name       = "my-key"
  public_key = file("~/.ssh/id_ed25519.pub")
}
```

> `public_key`는 RequiresReplace. 키를 바꾸려면 새 리소스 만들고 인스턴스 attach만 갈아끼우는 게 일반적.

**Import**: `terraform import cloudia_ssh_key.me <project_id>/<ssh_key_id>`

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="affinity-group"></a>
## `cloudia_affinity_group`

인스턴스/호스트 배치 정책 그룹. "이 인스턴스들은 같은 호스트에" 또는 "흩어서 배치" 같은 정책을 강제.

```hcl
resource "cloudia_affinity_group" "ha_pair" {
  name    = "ha-pair"
  enabled = true

  # 4개 정책 플래그 (true/false 조합)
  guest_positive   = false  # false = 분산 배치 (anti-affinity)
  guest_enforcing  = true   # true = 강제, false = best-effort
  host_positive    = true
  host_enforcing   = false

  instance_ids = [cloudia_instance.web1.id, cloudia_instance.web2.id]
  host_ids     = []   # null = unmanaged, [] = clear, non-empty = replace
}
```

호스트 ID를 직접 하드코딩하지 말고 `cloudia_compute_hosts`에서 읽어 쓰는 패턴이 일반적입니다.

**Import**: `terraform import cloudia_affinity_group.ha_pair <project_id>/<affinity_group_id>`

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="instance-snapshot"></a>
## `cloudia_instance_snapshot`

인스턴스 스냅샷 생성.

```hcl
resource "cloudia_instance_snapshot" "before_upgrade" {
  instance_id = cloudia_instance.demo.id
  name        = "before-upgrade-2026-05"
  description = "upgrade 직전 백업"
}
```

> 인스턴스를 `destroy`하려면 스냅샷을 먼저 지워야 합니다.

**Import**: `terraform import cloudia_instance_snapshot.before_upgrade <project_id>/<instance_id>/<snapshot_id>`

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="instance-snapshot-restore"></a>
## `cloudia_instance_snapshot_restore`

스냅샷 복원. **action 스타일 리소스** — Create만 의미 있고 Update/Read는 no-op, Import 불가.

```hcl
resource "cloudia_instance_snapshot_restore" "rollback" {
  instance_id = cloudia_instance.demo.id
  snapshot_id = cloudia_instance_snapshot.before_upgrade.id
}
```

> `instance_id`/`snapshot_id`를 바꾸면 RequiresReplace로 복원이 다시 수행됨. 같은 스냅샷으로 여러 번 복원하고 싶다면 리소스를 새로 만드세요.

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-compute-hosts"></a>
## `cloudia_compute_hosts` (data source)

cluster-wide compute host 목록. `cloudia_affinity_group.host_ids`를 동적으로 채울 때 사용합니다.

```hcl
data "cloudia_compute_hosts" "up_only" {
  status = "UP"
}

output "host_ids" {
  value = [for h in data.cloudia_compute_hosts.up_only.hosts : h.id]
}
```

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-accelerator-gpus"></a>
## `cloudia_accelerator_gpus` (data source)

GPU `(vendor_id, product_id)` 카탈로그와 가용량. `cloudia_instance.hardware_gpu` 값을 정할 때 사용합니다.

```hcl
data "cloudia_accelerator_gpus" "all" {}

output "gpu_pairs" {
  value = [for g in data.cloudia_accelerator_gpus.all.items : "${g.vendor_id}:${g.product_id}"]
}
```

GPU는 `pci_count_avail` 기준으로 용량을 보는 것이 안전합니다.

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-accelerator-npus"></a>
## `cloudia_accelerator_npus` (data source)

NPU `(vendor_id, product_id)` 카탈로그와 카드 가용량. `cloudia_instance.hardware_npu` 값을 정할 때 사용합니다.

```hcl
data "cloudia_accelerator_npus" "all" {}

output "npu_pairs" {
  value = [for n in data.cloudia_accelerator_npus.all.items : "${n.vendor_id}:${n.product_id}"]
}
```

NPU는 multi-endpoint 카드가 있으므로 `card_root_count_avail` 기준으로 보는 것이 안전합니다.

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-instance"></a>
## `cloudia_instance` / `cloudia_instances` (data source)

기존 인스턴스 조회.

```hcl
# 단일
data "cloudia_instance" "existing" {
  lookup_id = "42"
}

# 컬렉션 + 필터
data "cloudia_instances" "running" {
  name_prefix = "web-"
  power_state = "RUNNING"
}

output "running_count" {
  value = data.cloudia_instances.running.count
}
```

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-instance-type"></a>
## `cloudia_instance_type` / `cloudia_instance_types` (data source)

인스턴스 타입 카탈로그.

```hcl
# 이름으로 단일 조회
data "cloudia_instance_type" "small" {
  name = "s1.small"
}

# GPU/NPU 필터
data "cloudia_instance_types" "gpu_only" {
  gpu_capable = true
}

output "gpu_types" {
  value = data.cloudia_instance_types.gpu_only.items[*].name
}
```

> 카탈로그는 환경마다 다릅니다. dev/test에 등록된 타입 목록은 운영자 또는 콘솔에서 확인.

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-instance-disks"></a>
## `cloudia_instance_disks` (data source, 컬렉션 전용)

인스턴스에 붙은 모든 디스크.

```hcl
data "cloudia_instance_disks" "demo" {
  instance_id = cloudia_instance.demo.id
}

output "boot_disk_size_gib" {
  value = one([for d in data.cloudia_instance_disks.demo.items : d.size_gib if d.is_boot])
}
```

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-instance-interface"></a>
## `cloudia_instance_interface` (data source, selector singular)

인스턴스 NIC 1개. `lookup_id` ⊕ `is_default` (ExactlyOneOf).

```hcl
data "cloudia_instance_interface" "primary" {
  instance_id = cloudia_instance.demo.id
  is_default  = true
}

output "primary_ipv4" {
  value = data.cloudia_instance_interface.primary.ip_address
}
```

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-instance-snapshots"></a>
## `cloudia_instance_snapshots` (data source, 컬렉션 전용)

특정 인스턴스의 스냅샷 목록.

```hcl
data "cloudia_instance_snapshots" "demo" {
  instance_id = cloudia_instance.demo.id
}

output "snapshot_names" {
  value = data.cloudia_instance_snapshots.demo.items[*].name
}
```

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-ssh-key"></a>
## `cloudia_ssh_key` (data source)

기존 SSH 키 조회. `lookup_id` ⊕ `name` (ExactlyOneOf, by-name 중복은 에러).

```hcl
data "cloudia_ssh_key" "existing" {
  name = "my-key"
}

resource "cloudia_instance" "demo" {
  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [data.cloudia_ssh_key.existing.id]
  }
  # ...
}
```

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="ds-secure-types"></a>
## `cloudia_secure_types` (data source, 컬렉션 전용)

`cloudia_instance.secure_type`에 넣을 보안 등급 후보.

```hcl
data "cloudia_secure_types" "all" {}

output "secure_type_names" {
  value = data.cloudia_secure_types.all.items[*].name
}
```

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.
