# 자주 쓰는 워크플로 (Common Workflows)

> 플레이스홀더 reference: [Reference 표](../README.md#reference-table)
>
> 이 가이드의 예제는 모두 [시작하기](getting-started.md)에서 만든 기본 스택(VPC, subnet, security group, image, SSH key, instance)을 전제로 합니다. 아직 기본 스택을 만들지 않았다면 [시작하기](getting-started.md)를 먼저 완료하세요.

---

## 멀티 NIC 인스턴스

인스턴스에 NIC를 두 개 붙이면 내부 트래픽 분리, 관리 네트워크 격리 등이 가능합니다. `vnic` 목록에 항목을 추가하면 되고, 반드시 하나에만 `is_default_nic = true`를 지정해야 합니다.

```hcl
# 두 번째 서브넷 — 같은 VPC 안에 있어야 합니다.
resource "cloudia_subnet" "private" {
  vpc_id = cloudia_vpc.main.id
  name   = "private-subnet"
  cidr   = "10.250.2.0/24"
  type   = "PRIVATE_SUBNET"
}

resource "cloudia_instance" "dual_nic" {
  name         = "dual-nic-vm"
  network_id   = cloudia_vpc.main.id
  vcpu_number  = 2
  memory_total = 4096   # MiB

  image_id = data.cloudia_image.ubuntu.id

  vnic = [
    {
      subnet_id          = cloudia_subnet.default.id
      security_group_ids = [cloudia_security_group.default.id]
      is_default_nic     = true
    },
    {
      subnet_id          = cloudia_subnet.private.id
      security_group_ids = [cloudia_security_group.default.id]
      is_default_nic     = false
    },
  ]

  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [cloudia_ssh_key.me.id]
  }
}
```

**운영 노트**

- 두 서브넷은 **반드시 같은 VPC** 안에 있어야 합니다. 다른 VPC의 서브넷을 지정하면 backend가 거부합니다.
- `vnic[*].subnet_id`를 변경하면 REPLACE(인스턴스 재생성)가 발생합니다. `tofu plan`으로 미리 확인하세요.
- `is_default_nic = true`인 항목이 정확히 하나여야 합니다. 0개이거나 2개 이상이면 apply 시 에러가 발생합니다.

---

## 데이터 볼륨 attach

`cloudia_volume`을 별도로 만들고 `data_volume_ids`에 나열하면 인스턴스에 추가 블록 디스크가 붙습니다. 볼륨 추가/제거는 **인스턴스를 중지하지 않고** 적용됩니다(LIVE update).

```hcl
data "cloudia_storage_domains" "all" {}

resource "cloudia_volume" "data1" {
  name              = "app-data-01"
  size_gib          = 100
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
}

resource "cloudia_volume" "data2" {
  name              = "app-data-02"
  size_gib          = 50
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
}

resource "cloudia_instance" "app" {
  name         = "app-vm"
  network_id   = cloudia_vpc.main.id
  vcpu_number  = 4
  memory_total = 8192   # MiB

  image_id = data.cloudia_image.ubuntu.id

  data_volume_ids = [
    cloudia_volume.data1.id,
    cloudia_volume.data2.id,
  ]

  vnic = [
    {
      subnet_id          = cloudia_subnet.default.id
      security_group_ids = [cloudia_security_group.default.id]
      is_default_nic     = true
    },
  ]

  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [cloudia_ssh_key.me.id]
  }
}
```

**운영 노트**

- `data_volume_ids` 변경(추가/제거)은 LIVE 분기이므로 인스턴스가 RUNNING 상태에서도 무중단으로 적용됩니다.
- 볼륨의 `size_gib`는 in-place grow(확장)만 가능합니다. 줄이려면 destroy + recreate가 필요합니다.
- 볼륨이 인스턴스에 attached 상태에서 별도로 `terraform destroy`를 시도하면 backend가 거부합니다. 인스턴스를 먼저 detach(또는 destroy)한 뒤 볼륨을 삭제하세요.

---

## 스냅샷 생성과 롤백

`cloudia_instance_snapshot`으로 스냅샷을 찍고, `cloudia_instance_snapshot_restore`로 그 시점으로 되돌립니다.

```hcl
# 스냅샷 생성 — 인스턴스가 RUNNING 상태에서도 생성 가능합니다.
resource "cloudia_instance_snapshot" "before_upgrade" {
  instance_id = cloudia_instance.app.id
  name        = "before-upgrade-2026-05"
  description = "패키지 업그레이드 직전 백업"
}

# 롤백 — 스냅샷 시점으로 복원합니다.
# 복원 대상 인스턴스는 TERMINATED(STOPPED) 상태여야 합니다.
resource "cloudia_instance_snapshot_restore" "rollback" {
  instance_id = cloudia_instance.app.id
  snapshot_id = cloudia_instance_snapshot.before_upgrade.id
}
```

**운영 노트**

- 인스턴스를 `tofu destroy`하려면 스냅샷을 **먼저 삭제**해야 합니다. 스냅샷이 남아 있으면 backend가 인스턴스 삭제를 거부합니다. HCL에서 `cloudia_instance_snapshot`을 먼저 제거하고 apply한 뒤 인스턴스를 destroy하거나, `depends_on`으로 순서를 명시하세요.
- `cloudia_instance_snapshot_restore`는 **action 스타일** 리소스입니다. Create만 의미 있고, state에 기록된 뒤 Update/Read는 no-op입니다.
- 같은 스냅샷으로 여러 번 복원하고 싶다면 `cloudia_instance_snapshot_restore` 리소스를 새로 선언해야 합니다(`snapshot_id`를 바꾸어도 RequiresReplace로 재수행됩니다).
- restore 수행 전에 인스턴스를 STOPPED 상태로 만들어야 합니다. RUNNING 상태에서 restore를 시도하면 backend가 거부합니다.

---

## 플로팅 IP 연결

공인 IP가 필요할 때 `cloudia_floating_ip`를 생성하고 인스턴스의 private IP에 bind합니다. `resource_type = "IP"`로 지정하면 특정 내부 IP 주소에 묶이고, `resource_type = "INSTANCE"`로 지정하면 인스턴스 ID에 직접 묶입니다.

```hcl
locals {
  instance_private_ip = "10.250.1.10"
}

resource "cloudia_instance" "web" {
  name         = "web-vm"
  network_id   = cloudia_vpc.main.id
  vcpu_number  = 2
  memory_total = 4096   # MiB

  image_id = data.cloudia_image.ubuntu.id

  vnic = [
    {
      subnet_id          = cloudia_subnet.default.id
      security_group_ids = [cloudia_security_group.default.id]
      is_default_nic     = true
      ipv4_address       = local.instance_private_ip   # 고정 IP (생략 시 자동 할당)
    },
  ]

  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [cloudia_ssh_key.me.id]
  }
}

resource "cloudia_floating_ip" "web" {
  vpc_id      = cloudia_vpc.main.id
  name        = "web-fip"
  description = "web 서비스 공인 IP"

  depends_on = [cloudia_instance.web]

  binding = {
    resource_type = "IP"
    resource_id   = null
    resource_ip   = local.instance_private_ip
  }
}

output "public_ip" {
  value = cloudia_floating_ip.web.ip_address
}
```

**운영 노트**

- `binding.resource_ip`(대상 VPC 내부 IPv4)는 `"IP"`/`"INSTANCE"` **두 타입 모두 필수**입니다. `resource_id`는 `"INSTANCE"`일 때만 인스턴스 ID로 지정하고, `"IP"`일 때는 반드시 생략(`null`)해야 합니다.
- `binding`을 생략하면 unbound 상태(공인 IP만 예약)로 유지됩니다.
- `ip_address` 속성을 명시해 특정 공인 IP를 고정할 수 있지만, 변경 시 기존 IP가 release되고 새 IP가 할당됩니다.
- 프로젝트의 `public_ip_quota`가 충분해야 합니다. quota 초과 시 apply가 실패합니다.

---

## NFS 공유 볼륨

`cloudia_nfs_file_system`을 만들고 `cloudia_instance.file_systems`에 mount point를 지정하면 여러 인스턴스에서 동시에 접근할 수 있는 공유 스토리지를 구성할 수 있습니다.

```hcl
data "cloudia_storage_domains" "all" {}

resource "cloudia_nfs_file_system" "shared" {
  name              = "shared-nfs"
  size_gib          = 200
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
  network_id        = cloudia_vpc.main.id

  vnic = {
    subnet_id          = cloudia_subnet.default.id
    security_group_ids = [cloudia_security_group.default.id]
  }
}

resource "cloudia_instance" "app1" {
  name         = "app-vm-1"
  network_id   = cloudia_vpc.main.id
  vcpu_number  = 2
  memory_total = 4096   # MiB

  image_id = data.cloudia_image.ubuntu.id

  vnic = [
    {
      subnet_id          = cloudia_subnet.default.id
      security_group_ids = [cloudia_security_group.default.id]
      is_default_nic     = true
    },
  ]

  file_systems = [
    {
      file_system_id = cloudia_nfs_file_system.shared.id
      mountpoint     = "/mnt/shared"
    },
  ]

  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [cloudia_ssh_key.me.id]
  }
}

resource "cloudia_instance" "app2" {
  name         = "app-vm-2"
  network_id   = cloudia_vpc.main.id
  vcpu_number  = 2
  memory_total = 4096   # MiB

  image_id = data.cloudia_image.ubuntu.id

  vnic = [
    {
      subnet_id          = cloudia_subnet.default.id
      security_group_ids = [cloudia_security_group.default.id]
      is_default_nic     = true
    },
  ]

  file_systems = [
    {
      file_system_id = cloudia_nfs_file_system.shared.id
      mountpoint     = "/mnt/shared"
    },
  ]

  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [cloudia_ssh_key.me.id]
  }
}
```

**운영 노트**

- NFS 생성은 비동기입니다. backend가 NFS 서버 VM을 프로비저닝하는 데 시간이 걸리므로, 같은 plan에서 인스턴스를 즉시 mount하면 race가 발생할 수 있습니다. 생성이 실패하면 provider의 `CLOUDIA_NFS_CREATE_SETTLE_SECONDS` 환경 변수로 대기 시간을 늘려 보세요.
- `vnic.subnet_id`, `storage_domain_id`, `network_id`는 **RequiresReplace** 속성입니다. 변경 시 NFS 파일시스템이 재생성됩니다.
- `size_gib`는 grow(확장)만 가능하며, shrink를 시도하면 plan 단계에서 거부됩니다.
- `mountpoint`는 반드시 `/`로 시작하는 절대 경로여야 합니다.

---

## 골든 이미지 만들기

"골든 이미지"란 운영 환경에서 공통으로 쓸 수 있도록 미리 구성된 OS 이미지를 말합니다. Cloud:iA에서의 일반적인 흐름은 다음과 같습니다.

1. **인스턴스 준비** — OS 설치, 패키지 설치, cloud-init 정리 등 기본 환경을 구성합니다.
2. **스냅샷 생성** — `cloudia_instance_snapshot`으로 해당 시점을 스냅샷으로 찍습니다.
3. **이미지 등록** — 스냅샷을 바탕으로 이미지를 만들고 카탈로그에 등록합니다. 이 단계는 현재 콘솔 UI에서 진행합니다.

Terraform으로 스냅샷까지 만드는 방법은 [스냅샷 생성과 롤백](#스냅샷-생성과-롤백) 섹션을 참고하세요. 그 이후 이미지 등록 단계를 포함한 전체 실습 가이드는 여기를 참고하세요.

[ISO/골든 이미지 실습](../../examples-and-labs/16-create-golden-image-from-snapshot.md)

**운영 노트**

- 인스턴스를 스냅샷으로 캡처하기 전에 cloud-init 상태를 초기화하면 이미지에서 생성한 인스턴스에서 cloud-init이 정상 동작합니다. 초기화 방법은 위 실습 가이드를 참고하세요.
- 스냅샷이 남아 있는 동안은 인스턴스를 destroy할 수 없습니다. 골든 이미지 작업이 끝나면 스냅샷을 삭제하거나 인스턴스를 별도 유지하는 정책을 수립하세요.

---

## 다음 단계

- [데이터소스 선택](data-sources.md) — `cloudia_image` vs `cloudia_images` 같은 singular/plural 데이터소스 선택 기준
- [문제 해결](troubleshooting.md) — 자주 만나는 에러와 대응 방법
