# cloudia_affinity_group

인스턴스 및 호스트의 배치 정책 그룹을 관리하는 리소스입니다. "이 인스턴스들은 같은 호스트에 모아서(affinity)" 또는 "서로 다른 호스트에 분산(anti-affinity)"하는 정책을 hard(강제) 또는 soft(best-effort)로 지정합니다.

## 예제

```hcl
# 두 인스턴스를 서로 다른 호스트에 배치 (anti-affinity, hard)
resource "cloudia_affinity_group" "ha_pair" {
  name        = "ha-pair"
  description = "웹 서버 HA 쌍 — 다른 호스트에 분산 배치"
  enabled     = true

  guest_positive  = false  # false = 분산 (anti-affinity)
  guest_enforcing = true   # true = 강제 (hard rule)

  host_positive  = true    # true = 집중 (특정 호스트 그룹 내에서)
  host_enforcing = false   # false = best-effort (soft rule)

  instance_ids = [
    cloudia_instance.web1.id,
    cloudia_instance.web2.id,
  ]

  host_ids = []  # null = unmanaged, [] = clear, non-empty = replace
}
```

`cloudia_compute_hosts` 데이터소스를 이용해 호스트 ID를 동적으로 채우는 패턴:

```hcl
data "cloudia_compute_hosts" "fleet" {
  status = "UP"
}

locals {
  pinned_host_ids = slice(
    [for h in data.cloudia_compute_hosts.fleet.hosts : h.id],
    0,
    min(2, length(data.cloudia_compute_hosts.fleet.hosts))
  )
}

resource "cloudia_affinity_group" "ha_pair" {
  name     = "ha-pair"
  enabled  = true

  guest_positive  = false
  guest_enforcing = true

  host_positive  = true
  host_enforcing = false

  instance_ids = [cloudia_instance.web1.id, cloudia_instance.web2.id]
  host_ids     = local.pinned_host_ids
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `name` | 그룹 이름. 최대 80자, 영문자·숫자·`-`·`_` 허용 | 필수 | |
| `enabled` | 정책 활성화 여부. `false`이면 설정 유지, 스케줄링 강제는 중단 | 필수 | |
| `description` | 그룹 설명. 최대 200자 | 선택 | |
| `guest_positive` | 게스트(인스턴스) 배치 방향. `true`=집중(affinity), `false`=분산(anti-affinity). null이면 게스트 정책 비활성화 | 선택 | |
| `guest_enforcing` | 게스트 정책 강도. `true`=강제(hard), `false`=best-effort(soft). `guest_positive` 설정 시 필수 | 선택 | `guest_positive` 설정 시 필수 |
| `host_positive` | 호스트 배치 방향. `true`=집중, `false`=분산. null이면 호스트 정책 비활성화 | 선택 | |
| `host_enforcing` | 호스트 정책 강도. `true`=강제, `false`=best-effort. `host_positive` 설정 시 필수 | 선택 | `host_positive` 설정 시 필수 |
| `instance_ids` | 게스트 멤버 인스턴스 ID 목록. null=unmanaged, `[]`=전체 해제, non-empty=교체 | 선택 | |
| `host_ids` | 호스트 멤버 ID 목록. null=unmanaged, `[]`=전체 해제, non-empty=교체 | 선택 | `cloudia_compute_hosts` 데이터소스 활용 권장 |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**4개 정책 플래그 요약**:

| 플래그 | `true` 의미 | `false` 의미 |
|--------|-------------|--------------|
| `guest_positive` | 인스턴스 집중 배치 (affinity) | 인스턴스 분산 배치 (anti-affinity) |
| `guest_enforcing` | 강제 (hard rule) — 충족 불가 시 배치 거부 | best-effort (soft rule) |
| `host_positive` | 호스트 집중 배치 (affinity) | 호스트 분산 배치 (anti-affinity) |
| `host_enforcing` | 강제 (hard rule) | best-effort (soft rule) |

**읽기 전용 출력값**: `id`, `created_at`, `updated_at`

## 운영 노트

- **positive without enforcing**: `guest_positive`를 설정하면서 `guest_enforcing`을 생략(null)하면 plan이 거부될 수 있습니다. 두 플래그는 항상 쌍으로 설정하세요. 동일 규칙이 `host_positive` / `host_enforcing`에도 적용됩니다.
- **tri-state 멤버십**: `instance_ids`와 `host_ids`는 null(관리 안 함) / `[]`(전체 해제) / non-empty(전체 교체) 세 가지 상태를 구분합니다. Terraform state에서 명시적으로 `[]`를 넣어야 전체 해제가 됩니다.
- **cross-group conflict**: 동일 인스턴스가 서로 충돌하는 정책의 그룹에 중복 등록되면 백엔드가 conflict를 감지합니다. 인스턴스를 여러 그룹에 등록할 때는 정책 방향이 충돌하지 않는지 확인하세요.
- **host_ids 동적 관리**: 호스트 ID를 하드코딩하지 말고 `cloudia_compute_hosts` 데이터소스로 조회하여 채우는 패턴을 권장합니다.
- **enabled = false**: 그룹을 비활성화해도 멤버십은 유지됩니다. 스케줄링 강제만 중단됩니다.

## Import

```bash
terraform import cloudia_affinity_group.ha_pair <project_id>/<affinity_group_id>
```

예시:

```bash
terraform import cloudia_affinity_group.ha_pair 1/42
```

import 키 형식: `<project_id>/<affinity_group_id>`

## 관련 항목

- [../guides/import.md](../guides/import.md)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../README.md](../README.md)
- `cloudia_compute_hosts` 데이터소스 — 호스트 ID 동적 조회에 사용
- [cloudia_compute_hosts (데이터소스)](../data-sources/compute_hosts.md) — 배치 가능한 컴퓨트 호스트 목록 조회

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/affinity_group.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
