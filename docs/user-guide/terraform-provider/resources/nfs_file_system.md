# cloudia_nfs_file_system

NFS 공유 파일시스템을 생성하는 리소스입니다. 백엔드가 전용 NFS 서버 VM을 비동기로 프로비저닝하며, 여러 인스턴스에서 동시에 마운트(multi-attach)할 수 있습니다. NIC는 단일 구성입니다.

## 예제

```hcl
data "cloudia_storage_domains" "all" {}

resource "cloudia_nfs_file_system" "shared" {
  name              = "shared-nfs"
  size_gib          = 200
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
  network_id        = cloudia_vpc.main.id

  vnic = {
    subnet_id          = cloudia_subnet.public.id
    security_group_ids = [cloudia_security_group.nfs.id]
    # ipv4_address     = "10.20.1.50"   # 선택 — 생략 시 서브넷에서 자동 할당
  }
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `name` | 파일시스템 이름. 최대 80자, 영문자·숫자·`-`·`_` 허용. 프로젝트 내 중복 불가 | 필수 | in-place update 가능 |
| `size_gib` | 파일시스템 크기(GiB). 백엔드는 MiB 단위로 저장(`size_gib × 1024`) | 필수 | grow만 in-place, shrink는 plan 단계에서 거부 |
| `storage_domain_id` | NFS 데이터가 저장될 스토리지 도메인 ID | 필수 | 변경 시 **RequiresReplace** |
| `network_id` | NFS 서버 VM이 위치할 VPC(네트워크) ID | 필수 | 변경 시 **RequiresReplace** |
| `vnic` | NFS 서버 VM의 NIC 설정 (단일 객체) | 필수 | 변경 시 **RequiresReplace** |
| `vnic.subnet_id` | NIC가 연결될 서브넷 ID | 필수(vnic 내) | 변경 시 **RequiresReplace** |
| `vnic.security_group_ids` | NIC에 적용할 보안그룹 ID 집합(Set). 하나 이상 필수 | 필수(vnic 내) | 변경 시 **RequiresReplace** |
| `vnic.ipv4_address` | NIC에 지정할 정적 IPv4 주소. 생략 시 서브넷에서 자동 할당 | 선택(vnic 내) | 변경 시 **RequiresReplace** |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`, `path`, `type`, `size_mib`, `instance_count`, `deletable`, `storage_domain_name`, `storage_domain_type`, `created_at`, `updated_at`

## 운영 노트

- **grow-only**: `size_gib`를 줄이면 plan 단계에서 데이터 보호 정책으로 거부됩니다(`FS_UPDATE_FAILED`). 더 작은 NFS가 필요하면 destroy 후 재생성하세요.
- **RequiresReplace 인자**: `vnic`(전체 블록), `storage_domain_id`, `network_id`는 변경 시 파일시스템 전체를 destroy 후 재생성합니다. 변경 전에 마운트된 인스턴스를 먼저 분리하세요.
- **비동기 생성 및 settle delay**: NFS 서버 VM 생성·업데이트·삭제는 모두 `202 + requestId` 비동기 API로 처리되며, provider가 완료까지 polling합니다. 완료 후 provider는 추가로 약 30초(`nfs_create_settle_seconds`, 기본값) 대기하여 NFS 서버 내 `cloud-init` runcmd가 완료되길 기다립니다. 같은 plan에서 바로 인스턴스를 마운트하면 race가 발생할 수 있으니 `CLOUDIA_NFS_CREATE_SETTLE_SECONDS` 환경변수 또는 provider의 `nfs_create_settle_seconds` 설정으로 대기 시간을 늘리세요.
- **단일 NIC**: 백엔드 정책상 NFS는 단일 NIC만 허용합니다. `vnic`은 리스트가 아닌 단일 중첩 객체입니다.
- **마운트 방법**: 인스턴스에 NFS를 마운트하려면 `cloudia_instance`의 `file_systems` 블록에 `{ file_system_id = cloudia_nfs_file_system.shared.id, mountpoint = "/mnt/nfs" }` 형태로 지정합니다.
- **deletable 플래그**: 인스턴스가 마운트 중이면 백엔드가 `deletable = false`를 반환합니다. 이 상태에서 destroy를 시도하면 실패합니다. 먼저 모든 인스턴스에서 마운트를 해제하세요.

## Import

```bash
terraform import cloudia_nfs_file_system.shared <project_id>/<file_system_id>
```

예시:

```bash
terraform import cloudia_nfs_file_system.shared 1/42
```

import 키 형식: `<project_id>/<file_system_id>`

## 관련 항목

- [virtiofs_file_system.md](virtiofs_file_system.md) — VIRTIOFS host-local 파일시스템
- [volume.md](volume.md) — 블록 볼륨(비부팅 데이터 디스크)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/nfs_file_system.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
