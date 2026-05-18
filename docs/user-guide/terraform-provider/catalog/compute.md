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

가상머신 인스턴스. 가장 큰 리소스라 영문 docs를 반드시 같이 보세요.

### 최소 예제

```hcl
data "cloudia_image" "ubuntu" {
  name = "ubuntu-24.04"
}

resource "cloudia_instance" "demo" {
  name         = "demo-vm"
  vcpu_number  = 2
  memory_total = 4096   # MiB

  image_id  = data.cloudia_image.ubuntu.id
  subnet_id = cloudia_subnet.public.id
}
```

### Sizing — 직접 입력

`vcpu_number` + `memory_total` (MiB) 두 값으로 사이즈 결정. 카탈로그 preset을 그대로 쓰려면 `cloudia_instance_type` data source로 미러:

```hcl
data "cloudia_instance_type" "ref" { name = "c5.xlarge" }

resource "cloudia_instance" "from_catalog" {
  vcpu_number  = data.cloudia_instance_type.ref.vcpu_number
  memory_total = data.cloudia_instance_type.ref.memory_total
  # ...
}
```

### Update 분기 (LIVE / STOP / REPLACE) — 핵심 함정

수정한 필드에 따라 동작이 다릅니다.

| 분기 | 어떤 필드 | 동작 |
|---|---|---|
| **LIVE** | `vcpu_number`/`memory_total` **증가**, `data_volume_ids`, `vnic[*].security_group_ids` | 무중단 |
| **STOP** | `vcpu_number`/`memory_total` **감소**, `name`, `cloud_init.*`, `hardware_gpu`/`hardware_npu` 변경 등 | 자동 stop → update → run (다운타임 발생) |
| **REPLACE** | `network_id`, `image_id`, `vnic`, `boot_block_device_size_gib`, `secure_type` 등 | terraform이 destroy + create |

증가 vs 감소가 분기 다른 점 주의 — 4 vCPU → 8 vCPU는 무중단, 8 → 4는 다운타임.

### Import

```bash
terraform import cloudia_instance.demo <project_id>/<instance_id>
```

**전체 schema + GPU/NPU/cloud-init/lifecycle/topology 모든 옵션**: [영문 docs/resources/instance.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/instance.md)

---

<a id="ssh-key"></a>
## `cloudia_ssh_key`

SSH 공개키 등록. 인스턴스에 `ssh_key_ids`로 attach.

```hcl
resource "cloudia_ssh_key" "me" {
  name       = "my-key"
  public_key = file("~/.ssh/id_ed25519.pub")
}
```

> `public_key`는 RequiresReplace. 키를 바꾸려면 새 리소스 만들고 인스턴스 attach만 갈아끼우는 게 일반적.

**Import**: `terraform import cloudia_ssh_key.me <project_id>/<ssh_key_id>`

**전체 schema**: [영문 docs/resources/ssh_key.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/ssh_key.md)

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

  instance_ids      = [cloudia_instance.web1.id, cloudia_instance.web2.id]
  host_machine_ids  = []   # 비워두면 호스트 제약 없음
}
```

**Import**: `terraform import cloudia_affinity_group.ha_pair <project_id>/<affinity_group_id>`

**전체 schema**: [영문 docs/resources/affinity_group.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/affinity_group.md)

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

**전체 schema**: [영문 docs/resources/instance_snapshot.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/instance_snapshot.md)

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

**전체 schema**: [영문 docs/resources/instance_snapshot_restore.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/instance_snapshot_restore.md)

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

**전체 schema**: [영문 docs/data-sources/instance.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/instance.md), [instances.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/instances.md)

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

> 카탈로그는 환경마다 다릅니다. 사내 dev에 등록된 타입 목록은 운영자 또는 콘솔에서 확인.

**전체 schema**: [영문 docs/data-sources/instance_type.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/instance_type.md), [instance_types.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/instance_types.md)

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

**전체 schema**: [영문 docs/data-sources/instance_disks.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/instance_disks.md)

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

**전체 schema**: [영문 docs/data-sources/instance_interface.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/instance_interface.md)

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

**전체 schema**: [영문 docs/data-sources/instance_snapshots.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/instance_snapshots.md)

---

<a id="ds-ssh-key"></a>
## `cloudia_ssh_key` (data source)

기존 SSH 키 조회. `lookup_id` ⊕ `name` (ExactlyOneOf, by-name 중복은 에러).

```hcl
data "cloudia_ssh_key" "existing" {
  name = "my-key"
}

resource "cloudia_instance" "demo" {
  ssh_key_ids = [data.cloudia_ssh_key.existing.id]
  # ...
}
```

**전체 schema**: [영문 docs/data-sources/ssh_key.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/ssh_key.md)

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

**전체 schema**: [영문 docs/data-sources/secure_types.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/secure_types.md)
