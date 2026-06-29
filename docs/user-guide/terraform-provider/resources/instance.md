# cloudia_instance

가상머신 인스턴스를 생성하는 리소스입니다. 이 provider에서 **가장 큰 리소스**로, 사이징(vCPU·메모리)·네트워크(vNIC)·인증(cloud-init)·디스크(boot/데이터 볼륨)·파일시스템·가속기(GPU/NPU)·보안 모드(secure_type)를 한 리소스에서 모두 다룹니다. 변경하는 필드에 따라 적용 방식(무중단/재시작/재생성)이 달라지므로, 운영 환경에서는 apply 전에 반드시 `plan`으로 동작을 확인하세요.

> 이 페이지는 다른 리소스 문서보다 항목이 많아, 표준 구성(예제·주요 인자·운영 노트) 대신 주제별 섹션(사이징·vNIC·Update 동작 등)으로 구성되어 있습니다.

## 최소 예제

이미지는 `cloudia_image` 데이터소스로 조회하고, 인스턴스는 직접 사이징(`vcpu_number` + `memory_total`)으로 만듭니다. `cloud_init`은 필수 블록입니다.

```hcl
data "cloudia_image" "ubuntu" {
  name = "<your-image-name>"
}

resource "cloudia_instance" "demo" {
  name         = "demo-vm"
  network_id   = cloudia_vpc.main.id
  vcpu_number  = 2
  memory_total = 4096 # MiB

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

`cloud_init.username`은 일반 로그인 사용자명으로 지정하세요(소문자로 시작하는 4~20자, `[a-z0-9_-]`). `root`, `admin`, `ubuntu`, `centos` 같은 예약 이름은 백엔드가 거부합니다.

## 사이징 (Sizing)

사이징은 **직접 입력**이 유일한 경로입니다. `vcpu_number`(vCPU 개수)와 `memory_total`(메모리, MiB) 두 값으로 크기가 결정됩니다.

카탈로그에 등록된 인스턴스 타입을 그대로 쓰고 싶다면 `cloudia_instance_type` 데이터소스의 값을 미러하세요.

```hcl
data "cloudia_instance_type" "ref" {
  name = "<your-instance-type-name>"
}

resource "cloudia_instance" "from_catalog" {
  vcpu_number  = data.cloudia_instance_type.ref.vcpu_number
  memory_total = data.cloudia_instance_type.ref.memory_total
  # ...
}
```

### 핫플러그 여유분 — `max_vcpu` / `max_memory`

`max_vcpu`(vCPU 핫플러그 상한)와 `max_memory`(메모리 핫플러그 상한, MiB)는 인스턴스별 하이퍼바이저 천장값입니다. 카탈로그(인스턴스 타입)에는 노출되지 않으므로 워크로드의 핫플러그 여유분에 맞춰 직접 정합니다. 권장값은 현재 `vcpu_number` / `memory_total`의 1.5~2배입니다. 생략하면 각각 `vcpu_number` / `memory_total` 값으로 자동 채워집니다.

### `hyperthreading_enabled`

기본값은 `true`입니다. `true`(또는 미지정)인 경우 `vcpu_number`는 **반드시 짝수**여야 하며, 홀수를 지정하면 plan 단계에서 거부됩니다. 홀수 vCPU가 필요하면 `hyperthreading_enabled = false`로 설정하세요.

## Update 동작 — LIVE / STOP / REPLACE

인스턴스의 어떤 필드를 변경하느냐에 따라 적용 방식이 세 가지로 분기됩니다.

- **LIVE (무중단)** — 인스턴스를 정지하지 않고 그대로 반영합니다. 다운타임이 없습니다.
- **STOP (다운타임 발생)** — provider가 인스턴스를 자동으로 정지 → 수정 → 다시 시작합니다. 적용 중 일시적인 다운타임이 발생합니다.
- **REPLACE (재생성)** — Terraform이 기존 인스턴스를 삭제하고 새로 만듭니다. 인스턴스 ID·디스크 데이터가 모두 새로 생성됩니다(RequiresReplace).

> ⚠️ **운영 환경 주의**: 같은 변경이라도 분기에 따라 영향이 크게 달라집니다. apply 전에 반드시 `tofu plan`(또는 `terraform plan`)으로 어떤 분기인지 확인하세요. 특히 REPLACE는 기존 인스턴스가 삭제되므로 plan 출력에 `# forces replacement`가 보이면 데이터·IP 보존을 먼저 점검해야 합니다.

| 변경하는 필드 | 분기 | 비고 |
|---|---|---|
| `data_volume_ids` 추가/제거 | **LIVE** | 데이터 볼륨 attach/detach |
| `vnic[*].security_group_ids` 변경 | **LIVE** | NIC 보안그룹 교체 |
| `vcpu_number` 증가 | **LIVE** | 핫플러그(hot-plug) |
| `memory_total` 증가 | **LIVE** | 핫플러그(hot-plug) |
| `vcpu_number` 감소 | **STOP** | 백엔드가 hot-unplug 미지원 |
| `memory_total` 감소 | **STOP** | 백엔드가 hot-unplug 미지원 |
| `max_vcpu` / `max_memory` 변경 | **STOP** | |
| `hyperthreading_enabled` 토글 | **STOP** | vCPU 토폴로지 변경 |
| `name` 변경 | **STOP** | |
| `cloud_init.*` 변경 (username, scripts 등) | **STOP** | 정지 후 재시작 |
| `file_systems` 변경 | **STOP** | |
| `hardware_gpu` / `hardware_npu` 변경(부착/교체/해제) | **STOP** | |
| `power_state` 토글 (RUNNING ↔ STOPPED) | **STOP** | |
| `network_id` 변경 | **REPLACE** | 생성 후 불변 |
| `secure_type` 변경 | **REPLACE** | boot disk 호환성 |
| `vnic` 추가/제거 | **REPLACE** | |
| `vnic[*].subnet_id` 변경 | **REPLACE** | |
| `vnic[*].ipv4_address` 변경 | **REPLACE** | 빈 IPv4 필요 |
| `vnic[*].is_default_nic` 변경 | **REPLACE** | |
| `boot_block_device_size_gib` 변경 | **REPLACE** | |
| `image_id` 변경 | **REPLACE** | |

> STOP 분기와 LIVE 분기가 한 번에 바뀌면 하나의 정지-수정 호출로 합쳐 처리됩니다. `vcpu_number` / `memory_total`은 증가하면 LIVE, 감소하면 STOP으로 방향에 따라 나뉩니다.

## vNIC

`vnic`는 인스턴스의 NIC 목록입니다(인스턴스당 최대 8개). 단일 NIC 또는 다중 NIC 모두 구성할 수 있습니다.

```hcl
resource "cloudia_instance" "multi_nic" {
  # ...
  vnic = [
    {
      subnet_id          = cloudia_subnet.public.id
      security_group_ids = [cloudia_security_group.web.id]
      is_default_nic     = true
      ipv4_address       = "10.20.1.10" # 고정 IP (생략 시 자동 할당)
    },
    {
      subnet_id          = cloudia_subnet.private.id
      security_group_ids = [cloudia_security_group.backend.id]
      is_default_nic     = false
    },
  ]
}
```

- `is_default_nic`는 **정확히 하나의 NIC만** `true`여야 합니다(목록 단위 검증). 아무 NIC도 지정하지 않으면 첫 번째 NIC가 자동으로 기본 NIC가 됩니다.
- `ipv4_address`를 지정하면 고정 IP, 생략하면 Cloud:iA가 자동 할당합니다.
- 두 NIC가 같은 서브넷을 공유하려면 `ipv4_address`가 서로 달라야 합니다(또는 둘 다 자동 할당).
- NIC당 보안그룹은 최대 5개입니다. `security_group_ids` 변경은 LIVE로 무중단 적용되지만, `subnet_id` / `ipv4_address` / `is_default_nic` 변경과 NIC 추가/제거는 REPLACE입니다.

## 인증

`cloud_init`은 필수 블록입니다. `username`은 반드시 지정하고, `password` 또는 `ssh_key_ids` 중 **최소 하나**가 있어야 합니다(둘 다 지정해도 됩니다). 둘 다 없으면 plan 단계에서 거부됩니다.

```hcl
# password만
cloud_init = {
  username = "appuser"
  password = "<your-instance-password>"
}

# ssh_key_ids만
cloud_init = {
  username    = "appuser"
  ssh_key_ids = [cloudia_ssh_key.me.id]
}

# 둘 다
cloud_init = {
  username    = "appuser"
  password    = "<your-instance-password>"
  ssh_key_ids = [cloudia_ssh_key.me.id]
}
```

- `password`는 WriteOnly이므로 state에 저장되지 않습니다. `terraform import` 후에는 다시 입력해야 합니다.
- `ssh_key_ids`는 최대 3개까지 주입할 수 있습니다. 키 등록은 [`ssh_key.md`](ssh_key.md)를 참고하세요.

## cloud-init 스크립트

`cloud_init.scripts`로 게스트 안에서 cloud-init이 실행할 사용자 스크립트를 등록할 수 있습니다. 각 스크립트의 `phase`로 실행 시점을 정합니다.

| `phase` | 실행 시점 |
|---|---|
| `PER_ONCE` | 인스턴스 수명 동안 단 한 번 실행 |
| `PER_INSTANCE` | cloud-init 설정이 바뀔 때 실행 |
| `PER_BOOT` | 부팅할 때마다 실행 |

```hcl
cloud_init = {
  username = "appuser"
  password = "<your-instance-password>"

  scripts = [
    {
      content = "#!/bin/sh\necho \"hello from cloud-init\" > /tmp/init.log\n"
      phase   = "PER_INSTANCE"
    },
  ]
}
```

- `scripts` 변경은 STOP 분기로 처리되어 인스턴스가 자동으로 재시작됩니다. 다운타임을 피하려면 `power_state = "STOPPED"`로 먼저 정지한 뒤 적용하세요.
- `scripts` 키 전체를 생략하면 백엔드의 모든 사용자 스크립트가 제거됩니다. 빈 배열 `scripts = []`는 의도가 모호하여 거부되므로, 전부 제거하려면 키 자체를 생략하세요.
- `script_order`는 모든 항목에 지정하거나 모두 생략해야 합니다(일부만 지정하면 plan 단계에서 거부). 생략하면 목록 순서대로 자동 부여됩니다.

## secure_type

`secure_type`은 기밀 VM 모드입니다(`NONE` | `SEV` | `SEV_ES` | `SEV_SNP`, 기본값 `NONE`). 환경에서 사용할 수 있는 후보는 `cloudia_secure_types` 데이터소스로 조회합니다.

```hcl
data "cloudia_secure_types" "all" {}

output "secure_type_names" {
  value = data.cloudia_secure_types.all.items[*].name
}
```

- `secure_type` 변경은 boot disk 호환성 때문에 **REPLACE**입니다. 예를 들어 `NONE` → `SEV` 전환은 인스턴스 재생성으로 이어지며, 인스턴스가 배치된 호스트가 SEV를 지원하지 않으면 apply가 실패합니다.
- `secure_type = "SEV_ES"`인 경우 백엔드가 `max_vcpu`를 `vcpu_number`와 같게 강제합니다.

## GPU / NPU

가속기는 `hardware_gpu`(GPU) 또는 `hardware_npu`(NPU)로 부착합니다. 인스턴스 하나당 가속기는 **최대 하나**이며, `hardware_gpu`와 `hardware_npu`를 **동시에 지정하면 plan 단계에서 거부**됩니다.

사용 가능한 `(vendor_id, product_id)` 쌍은 `cloudia_accelerator_gpus` / `cloudia_accelerator_npus` 데이터소스로 조회합니다. 호스트가 물리적으로 해당 장치를 가지고 있어야 부착됩니다.

```hcl
resource "cloudia_instance" "with_npu" {
  name         = "instance-with-npu"
  network_id   = cloudia_vpc.main.id
  image_id     = data.cloudia_image.ubuntu.id
  vcpu_number  = data.cloudia_instance_type.small.vcpu_number
  memory_total = data.cloudia_instance_type.small.memory_total

  vnic = [
    {
      subnet_id          = cloudia_subnet.public.id
      security_group_ids = [cloudia_security_group.default.id]
      is_default_nic     = true
    },
  ]

  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [cloudia_ssh_key.me.id]
  }

  # GPU를 부착하려면 hardware_gpu를 대신 사용하세요(둘 중 하나만).
  hardware_npu = {
    vendor_id  = "1eff"
    product_id = "1250"
    unit_count = 1
  }
}
```

- `unit_count`는 1 이상이며 기본값은 1입니다. 가속기 종류에 따라 의미가 다릅니다. GPU는 1 unit = PCI 장치 1개, NPU는 1 unit = 카드 루트(card-root) 1개(카드 하나에 여러 PCI가 묶일 수 있음)입니다.
- 용량은 GPU/NPU 공통 `pci_count_avail`, NPU 전용 `card_root_count_avail` 값으로 미리 확인하세요.
- 가속기 부착/교체/해제는 모두 **STOP** 분기로 처리됩니다(부착 후 인스턴스가 정지 → 수정 → 재시작). 블록을 생략하면 가속기가 분리됩니다.

## plan 단계에서 자주 만나는 거부

apply 전 `plan` 단계에서 걸러지는 대표적인 거부 상황입니다.

| 거부 메시지(또는 상황) | 원인 |
|---|---|
| `vcpu_number must be even when hyperthreading_enabled = true` | `hyperthreading_enabled = true`(또는 기본값)인데 `vcpu_number`가 홀수 |
| `hardware_gpu and hardware_npu cannot both be set` | `hardware_gpu`와 `hardware_npu`를 동시에 지정 |
| `cloud_init requires password or ssh_key_ids` | `cloud_init`에 `password`·`ssh_key_ids`가 모두 없음 |
| `mountpoint must be an absolute path` | `file_systems[*].mountpoint`가 절대경로(`/`로 시작)가 아님 |
| `username` 거부 (예약 이름) | `cloud_init.username`이 `root`/`admin`/`ubuntu`/`centos` 등 예약 이름 |
| `scripts = []` 거부 | 빈 배열 대신 `scripts` 키 전체를 생략해야 함 |

## Import

```bash
terraform import cloudia_instance.demo <project_id>/<instance_id>
```

예시:

```bash
terraform import cloudia_instance.demo 1/42
```

import 키 형식: `<project_id>/<instance_id>`

> `cloud_init.password`는 WriteOnly라 state에 저장되지 않으므로, import 후 설정에 다시 입력해야 합니다.

## 관련 항목

- [ssh_key.md](ssh_key.md) — 인스턴스에 주입할 SSH 공개키
- [volume.md](volume.md) — `data_volume_ids`로 붙이는 데이터 볼륨
- [security_group.md](security_group.md) — vNIC에 연결하는 보안그룹
- [subnet.md](subnet.md) — vNIC가 속할 서브넷
- [instance_snapshot.md](instance_snapshot.md) — 인스턴스 스냅샷
- [affinity_group.md](affinity_group.md) — 인스턴스 배치 정책 그룹
- [nfs_file_system.md](nfs_file_system.md) — `file_systems`로 마운트하는 NFS 파일시스템
- [virtiofs_file_system.md](virtiofs_file_system.md) — `file_systems`로 마운트하는 VIRTIOFS 파일시스템
- 데이터소스: `cloudia_instance_type`, `cloudia_secure_types`, `cloudia_accelerator_gpus`, `cloudia_accelerator_npus` (조회 전용)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../guides/getting-started.md](../guides/getting-started.md)
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)
- [cloudia_instance (데이터소스)](../data-sources/instance.md) — 기존 인스턴스 정보 조회
- [cloudia_instances (데이터소스)](../data-sources/instances.md) — 인스턴스 목록 조회
- [cloudia_instance_type (데이터소스)](../data-sources/instance_type.md) — 인스턴스 타입 카탈로그 조회
- [cloudia_instance_disks (데이터소스)](../data-sources/instance_disks.md) — 인스턴스에 연결된 디스크 목록 조회
- [cloudia_instance_interface (데이터소스)](../data-sources/instance_interface.md) — 인스턴스 네트워크 인터페이스 조회
- [cloudia_secure_types (데이터소스)](../data-sources/secure_types.md) — 사용 가능한 보안 모드 목록 조회

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/instance.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
