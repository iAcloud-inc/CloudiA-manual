# cloudia_instances (데이터소스)

프로젝트 내 인스턴스 목록을 조회합니다. `name_prefix`·`power_state` 필터를 AND 조합으로 적용할 수 있습니다. 상세 필드(NIC, 데이터 볼륨, 이미지 등)가 필요한 경우에는 [instance.md](instance.md)를 사용하세요.

## 예제

```hcl
# 전체 목록
data "cloudia_instances" "all" {}

output "total_count" {
  value = data.cloudia_instances.all.total_count
}

# 이름 접두사 + 전원 상태 필터
data "cloudia_instances" "running_web" {
  name_prefix = "web-"
  power_state = "RUNNING"
}

output "running_web_ids" {
  value = [for inst in data.cloudia_instances.running_web.instances : inst.id]
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `name_prefix` | 선택 | 인스턴스 이름 접두사 필터. 비어 있으면 적용되지 않음. |
| `power_state` | 선택 | 전원 상태 필터 (`RUNNING` / `STOPPED`). 비어 있으면 적용되지 않음. |
| `project_id` | 선택 | 프로젝트 ID. 생략 시 provider 설정값 사용. |

## 속성

컬렉션 필드: **`instances`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `instances` | List(Object) | 필터 후 인스턴스 요약 목록 (ID 오름차순 정렬). |
| `instances[*].id` | String | 인스턴스 ID. |
| `instances[*].name` | String | 인스턴스 이름. |
| `instances[*].status` | String | 백엔드 관측 상태. |
| `instances[*].power_state` | String | 의도된 전원 상태 (`RUNNING` / `STOPPED`). |
| `instances[*].vcpu_number` | Number | vCPU 수. |
| `instances[*].memory_total` | Number | 메모리 (MiB). |
| `instances[*].ip_addresses` | List(String) | 백엔드에서 보고된 IP 주소 목록. |
| `instances[*].project_id` | String | 소유 프로젝트 ID. |
| `instances[*].secure_type` | String | 보안 모드. |
| `instances[*].created_at` | String | 생성 시각 (RFC3339). |
| `instances[*].updated_at` | String | 마지막 수정 시각 (RFC3339). |
| `total_count` | Number | 필터 후 반환된 인스턴스 수. |

## 관련 항목

- [instance.md](instance.md) — 단일 인스턴스 상세 조회
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/instances.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
