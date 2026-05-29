# cloudia_compute_hosts (데이터소스)

클러스터 전체 컴퓨트 호스트 목록을 조회합니다. 주로 `cloudia_affinity_group.host_ids`를 동적으로 채울 때 사용합니다. 호스트 ID를 하드코딩하는 대신 이 데이터소스로 읽어 사용하세요. `status`·`host_name_prefix` 필터를 AND 조합으로 적용할 수 있습니다.

## 예제

```hcl
# 상태가 UP인 호스트만 조회
data "cloudia_compute_hosts" "up_only" {
  status = "UP"
}

output "up_host_ids" {
  value = [for h in data.cloudia_compute_hosts.up_only.hosts : h.id]
}

# affinity_group에 동적으로 연결
resource "cloudia_affinity_group" "ha_pair" {
  name           = "ha-pair"
  enabled        = true
  guest_positive = false
  guest_enforcing = true
  host_positive  = true
  host_enforcing = false

  instance_ids = [cloudia_instance.web1.id, cloudia_instance.web2.id]
  host_ids     = [for h in data.cloudia_compute_hosts.up_only.hosts : h.id]
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `status` | 선택 | 상태 필터 (`UP` / `DOWN` / `MAINTENANCE_MODE`). 비어 있으면 적용되지 않음. |
| `host_name_prefix` | 선택 | 호스트 이름 접두사 필터. 비어 있으면 적용되지 않음. |

## 속성

컬렉션 필드: **`hosts`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `hosts` | List(Object) | 컴퓨트 호스트 목록 (ID 오름차순 정렬). |
| `hosts[*].id` | String | 호스트 ID (`hostMachineId`). `cloudia_affinity_group.host_ids` 입력에 사용. |
| `hosts[*].host_name` | String | 호스트 이름. |
| `hosts[*].status` | String | 백엔드 상태 (`UP` / `DOWN` / `MAINTENANCE_MODE`). |
| `hosts[*].instance_count` | Number | 현재 스케줄된 인스턴스 수. |
| `hosts[*].cpu_overcommit_ratio` | Number | CPU 오버커밋 비율. |
| `hosts[*].memory_overcommit_ratio` | Number | 메모리 오버커밋 비율. |
| `hosts[*].created_at` | String | 생성 시각 (RFC3339). |
| `hosts[*].updated_at` | String | 마지막 수정 시각 (RFC3339). |
| `total_count` | Number | 필터 후 반환된 호스트 수. |

## 관련 항목

- [../resources/affinity_group.md](../resources/affinity_group.md) — 배치 그룹 리소스 (`host_ids`)
- [accelerator_gpus.md](accelerator_gpus.md) — GPU 카탈로그
- [accelerator_npus.md](accelerator_npus.md) — NPU 카탈로그

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/compute_hosts.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
