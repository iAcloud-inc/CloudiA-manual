# cloudia_project (데이터소스)

`lookup_id` 또는 `name`으로 기존 프로젝트 한 개를 조회합니다. 두 인자를 모두 생략하면 provider에 설정된 `project_id`를 기준으로 조회합니다. 프로젝트 목록 전체가 필요할 때는 [projects.md](projects.md)를 사용하세요.

## 예제

```hcl
# 이름으로 조회
data "cloudia_project" "target" {
  name = "app-prod"
}

resource "cloudia_vpc" "main" {
  project_id = data.cloudia_project.target.id
  name       = "main-vpc"
  cidr       = "10.0.0.0/16"
}

# ID로 조회
data "cloudia_project" "by_id" {
  lookup_id = "5"
}

output "project_vcpu_quota" {
  value = data.cloudia_project.by_id.vcpu_quota
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `lookup_id` | 선택 | 조회할 프로젝트 ID. `name`과 동시에 지정 불가. |
| `name` | 선택 | 조회할 프로젝트 이름. `lookup_id`와 동시에 지정 불가. |

## 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 조회된 프로젝트 ID. |
| `description` | String | 프로젝트 설명. |
| `disk_quota` | Number | 디스크 quota (MiB). |
| `memory_quota` | Number | 메모리 quota (MiB). |
| `public_ip_quota` | Number | 공인 IP quota. |
| `quota_enabled` | Boolean | 프로젝트 quota 활성화 여부. |
| `vcpu_quota` | Number | vCPU quota. |

## 관련 항목

- [projects.md](projects.md) — 프로젝트 목록 조회
- [../resources/project.md](../resources/project.md) — 프로젝트 리소스 (생성)
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/project.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
