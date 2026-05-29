# cloudia_instance_snapshots (데이터소스)

특정 인스턴스의 스냅샷 목록을 조회합니다. 최신 스냅샷이 맨 앞(`created_at` 내림차순, ID 오름차순)에 위치합니다.

## 예제

```hcl
data "cloudia_instance_snapshots" "demo" {
  instance_id = cloudia_instance.demo.id
}

output "snapshot_count" {
  value = data.cloudia_instance_snapshots.demo.total_count
}

# 가장 최근 스냅샷 ID
output "latest_snapshot_id" {
  value = try(data.cloudia_instance_snapshots.demo.snapshots[0].id, null)
}

# 보호된 스냅샷 이름 목록
output "protected_snapshot_names" {
  value = [
    for s in data.cloudia_instance_snapshots.demo.snapshots :
    s.name if s.is_protected
  ]
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `instance_id` | 필수 | 스냅샷을 조회할 인스턴스 ID. |
| `project_id` | 선택 | 프로젝트 ID. 생략 시 provider 설정값 사용. |

## 속성

컬렉션 필드: **`snapshots`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `snapshots` | List(Object) | 스냅샷 목록. created_at 내림차순 정렬 (최신이 첫 번째). |
| `snapshots[*].id` | String | 스냅샷 ID. |
| `snapshots[*].name` | String | 스냅샷 이름. |
| `snapshots[*].description` | String | 스냅샷 설명. 백엔드 응답에 없으면 null. |
| `snapshots[*].is_protected` | Boolean | 보호 플래그. |
| `snapshots[*].created_at` | String | 생성 시각. |
| `snapshots[*].disk_snapshots` | List(Object) | 디스크별 스냅샷 매핑 목록. |
| `total_count` | Number | 반환된 스냅샷 수. |

> 인스턴스를 삭제(destroy)하기 전에 스냅샷을 먼저 삭제해야 합니다.

## 관련 항목

- [instance.md](instance.md) — 인스턴스 단일 조회
- [../resources/instance_snapshot.md](../resources/instance_snapshot.md) — 스냅샷 리소스 (생성/삭제)
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/instance_snapshots.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
