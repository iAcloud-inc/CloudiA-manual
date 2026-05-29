# cloudia_virtiofs_file_system

VIRTIOFS host-local 공유 파일시스템을 생성하는 리소스입니다. NFS와 달리 전용 서버 VM을 프로비저닝하지 않고, 호스트 로컬 디렉터리를 인스턴스에 직접 공유하므로 생성·수정·삭제가 동기적으로 즉시 처리됩니다. 같은 물리 호스트에 있는 인스턴스끼리만 공유할 수 있습니다.

## 예제

```hcl
data "cloudia_storage_domains" "all" {}

# LOCAL 타입 스토리지 도메인 필터링 (VIRTIOFS는 LOCAL이 전형적)
locals {
  local_sd = [for sd in data.cloudia_storage_domains.all.items : sd if sd.type == "LOCAL"]
}

resource "cloudia_virtiofs_file_system" "host_local" {
  name              = "host-local-fs"
  storage_domain_id = local.local_sd[0].id
}
```

인스턴스에 VIRTIOFS를 마운트하는 예:

```hcl
# cloudia_instance 리소스에서 file_systems 블록으로 참조
# (cloudia_instance 리소스는 별도 문서를 참고하세요)
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `name` | 파일시스템 이름. 최대 80자, 영문자·숫자·`-`·`_` 허용. 프로젝트 내 중복 불가 | 필수 | in-place update 가능 |
| `storage_domain_id` | 파일시스템이 위치할 스토리지 도메인 ID. `CEPH`는 불가, `LOCAL`이 전형적 | 필수 | 변경 시 **RequiresReplace** |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`, `path`, `type`, `deletable`, `storage_domain_name`, `storage_domain_type`, `created_at`, `updated_at`

## 운영 노트

- **`CEPH` 스토리지 도메인 불가**: `storage_domain_id`에 `CEPH` 타입을 지정하면 plan 단계에서 거부됩니다. `LOCAL`, `GFS2`, `NFS` 타입은 사용할 수 있으며, 호스트 로컬 디렉터리 특성상 `LOCAL`이 가장 전형적입니다. `data "cloudia_storage_domains"`로 조회 후 적절한 타입을 선택하세요.
- **동기 처리**: NFS와 달리 전용 VM을 프로비저닝하지 않으므로 생성·수정·삭제가 모두 동기적으로 즉시 완료됩니다. settle delay가 필요하지 않습니다.
- **호스트 로컬 공유 범위**: VIRTIOFS는 호스트 로컬 디렉터리를 기반으로 하므로 같은 물리 호스트에 위치한 인스턴스끼리만 공유할 수 있습니다. 여러 호스트에 걸친 공유가 필요하면 `cloudia_nfs_file_system`을 사용하세요.
- **마운트 방법**: 인스턴스에 VIRTIOFS를 마운트하려면 `cloudia_instance`의 `file_systems` 블록에 `{ file_system_id = cloudia_virtiofs_file_system.host_local.id, mountpoint = "/mnt/virtiofs" }` 형태로 지정합니다.
- **deletable 플래그**: 인스턴스가 마운트 중이면 백엔드가 `deletable = false`를 반환합니다. destroy 전에 모든 인스턴스에서 마운트를 해제하세요.
- **storage_domain_id RequiresReplace**: `storage_domain_id`를 변경하면 파일시스템이 destroy 후 재생성됩니다.

## Import

```bash
terraform import cloudia_virtiofs_file_system.host_local <project_id>/<file_system_id>
```

예시:

```bash
terraform import cloudia_virtiofs_file_system.host_local 1/42
```

import 키 형식: `<project_id>/<file_system_id>`

## 관련 항목

- [nfs_file_system.md](nfs_file_system.md) — NFS 공유 파일시스템 (멀티 호스트 공유)
- [volume.md](volume.md) — 블록 볼륨(비부팅 데이터 디스크)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/virtiofs_file_system.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
