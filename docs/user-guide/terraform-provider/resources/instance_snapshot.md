# cloudia_instance_snapshot

인스턴스 스냅샷을 생성·관리하는 리소스입니다. 생성·삭제 요청은 백엔드가 비동기(`202 + requestId`)로 처리하며 provider가 완료를 폴링합니다. 스냅샷 복원은 별도 리소스인 [instance_snapshot_restore.md](instance_snapshot_restore.md)를 사용합니다.

## 예제

모든 디스크 스냅샷 (기본):

```hcl
resource "cloudia_instance_snapshot" "before_upgrade" {
  instance_id = cloudia_instance.demo.id
  name        = "before-upgrade-2026-05"
  description = "업그레이드 직전 백업"
}
```

특정 디스크만 스냅샷:

```hcl
data "cloudia_instance_disks" "demo" {
  instance_id = cloudia_instance.demo.id
}

resource "cloudia_instance_snapshot" "boot_only" {
  instance_id    = cloudia_instance.demo.id
  name           = "boot-only-2026-05"
  guest_disk_ids = [
    for d in data.cloudia_instance_disks.demo.disks : d.id if d.is_boot
  ]
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `instance_id` | 스냅샷을 생성할 인스턴스 ID (`cloudia_instance`) | 필수 | 변경 시 새 스냅샷 생성(RequiresReplace) |
| `name` | 스냅샷 이름. 최대 80자, 영문자·숫자·`-`·`_` 허용 | 필수 | in-place 업데이트 가능 |
| `description` | 스냅샷 설명. 최대 200자 | 선택 | in-place 업데이트 가능 |
| `guest_disk_ids` | 포함할 디스크 ID 목록. 생략 또는 빈 배열이면 모든 디스크 스냅샷 | 선택 | 변경 시 새 스냅샷 생성(RequiresReplace) |
| `is_protected` | 보호 플래그. `true`이면 백엔드 정책이 실수 삭제를 방지 | 선택 | |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`, `created_at`, `disk_snapshots`(per-disk 매핑 목록)

## 운영 노트

- **선행 조건**: 인스턴스가 `UP` 또는 `TERMINATED` 상태여야 스냅샷을 생성할 수 있습니다. 다른 상태에서 apply하면 백엔드가 에러를 반환합니다.
- **destroy 순서**: 인스턴스를 `terraform destroy`하려면 해당 인스턴스의 스냅샷을 먼저 삭제해야 합니다. 스냅샷이 남아 있으면 API가 인스턴스 삭제를 거부합니다.
- **비동기 처리**: 스냅샷 생성·삭제 API는 `202`를 반환하고 provider가 완료를 폴링합니다. 디스크 크기에 따라 수 분이 소요될 수 있습니다.
- **in-place 업데이트**: `name`과 `description`은 인스턴스·스냅샷을 재생성하지 않고 PUT으로 업데이트됩니다. `instance_id`나 `guest_disk_ids`를 변경하면 기존 스냅샷이 삭제되고 새로 생성됩니다.
- **복원**: 스냅샷을 인스턴스에 복원하려면 [instance_snapshot_restore.md](instance_snapshot_restore.md) 리소스를 사용하세요.

## Import

```bash
terraform import cloudia_instance_snapshot.before_upgrade <project_id>/<instance_id>/<snapshot_id>
```

예시:

```bash
terraform import cloudia_instance_snapshot.before_upgrade 1/42/7
```

import 키 형식: `<project_id>/<instance_id>/<snapshot_id>` (3-part, 인스턴스 스코프)

## 관련 항목

- [instance_snapshot_restore.md](instance_snapshot_restore.md) — 스냅샷 복원
- [../guides/import.md](../guides/import.md)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../README.md](../README.md)
- [cloudia_instance_snapshots (데이터소스)](../data-sources/instance_snapshots.md) — 인스턴스 스냅샷 목록 조회

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/instance_snapshot.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
