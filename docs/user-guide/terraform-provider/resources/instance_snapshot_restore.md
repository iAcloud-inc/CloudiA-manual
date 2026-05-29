# cloudia_instance_snapshot_restore

인스턴스를 특정 스냅샷 시점으로 복원하는 **action 스타일** 리소스입니다. Create 시 백엔드 복원 API를 호출하며, Read·Update·Delete는 의도적으로 no-op입니다. 복원은 일회성 이벤트로 백엔드에 별도 상태가 없으므로 **import 불가**합니다.

## 예제

```hcl
resource "cloudia_instance_snapshot_restore" "rollback" {
  instance_id = cloudia_instance.demo.id
  snapshot_id = cloudia_instance_snapshot.before_upgrade.id
}
```

같은 스냅샷으로 복원을 재수행해야 할 때는 `triggers` 맵을 활용합니다:

```hcl
resource "cloudia_instance_snapshot_restore" "rollback" {
  instance_id = cloudia_instance.demo.id
  snapshot_id = cloudia_instance_snapshot.before_upgrade.id

  triggers = {
    intent = "rollback-after-incident-2026-05-29"
  }
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `instance_id` | 복원 대상 인스턴스 ID (`cloudia_instance`) | 필수 | 변경 시 RequiresReplace → 복원 재수행 |
| `snapshot_id` | 복원 기준 스냅샷 ID (`cloudia_instance_snapshot`) | 필수 | 변경 시 RequiresReplace → 복원 재수행 |
| `triggers` | 임의 key/value 맵. 값이 바뀌면 리소스가 교체되어 복원이 재수행됨(`null_resource.triggers`와 동일 컨벤션) | 선택 | 같은 스냅샷 재복원 시 활용 |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`(`<instance_id>/<snapshot_id>/<restored_at>`), `restored_at`(복원 완료 RFC3339 타임스탬프)

## 운영 노트

- **action 스타일 리소스**: Create만 실질적 동작이고 Read/Update/Delete는 no-op입니다. `terraform destroy`는 state 항목만 제거하며 백엔드 상태는 변경되지 않습니다.
- **복원 전 인스턴스 상태**: 백엔드는 대상 인스턴스가 `TERMINATED`(정지) 상태를 요구합니다. apply 전에 인스턴스를 먼저 정지하세요.
- **RequiresReplace**: `instance_id` 또는 `snapshot_id`를 변경하면 기존 리소스가 삭제(no-op)되고 새 리소스로 복원이 재수행됩니다.
- **같은 스냅샷 재복원**: `instance_id`와 `snapshot_id`가 동일한 경우 일반 apply는 no-op입니다. 재복원이 필요하면 `triggers` 맵의 값을 변경하거나 `terraform taint <resource>`를 사용하세요.
- **복원 불가역성**: 복원이 완료되면 인스턴스 디스크는 스냅샷 시점으로 되돌아가며, 그 이후 변경 사항은 사라집니다. 적용 전 반드시 최신 스냅샷을 확보하세요.
- **import 불가**: 복원은 일회성 이벤트로 백엔드에 "마지막 복원" 상태를 저장하는 SoT가 없습니다. 새 환경에서 복원이 필요하면 새 리소스 블록을 작성하세요.

## Import

이 리소스는 **import 불가**합니다. 복원은 일회성 이벤트이며 백엔드에 별도 상태가 없으므로 가져올 정보가 없습니다. 새 환경에서 복원이 필요한 경우 새 리소스 블록을 작성하여 apply하세요.

## 관련 항목

- [instance_snapshot.md](instance_snapshot.md) — 스냅샷 생성·관리
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/instance_snapshot_restore.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
