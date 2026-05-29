# cloudia_projects (데이터소스)

호출자가 볼 수 있는 프로젝트 전체 목록을 조회합니다. admin 권한으로 호출하면 전체 프로젝트가, 일반 사용자로 호출하면 본인이 멤버인 프로젝트만 반환됩니다. 특정 프로젝트 한 개를 ID나 이름으로 참조할 때는 [project.md](project.md)를 사용하세요.

## 예제

```hcl
# 전체 프로젝트 목록 (생성일 내림차순)
data "cloudia_projects" "all" {
  sort = ["createdAt,DESC"]
}

output "project_count" {
  value = data.cloudia_projects.all.total_count
}

output "first_project_name" {
  value = try(data.cloudia_projects.all.items[0].name, null)
}
```

> 단일 ID 참조 용도로 `items[0]`을 직접 사용하지 마세요. 목록 정렬 순서가 바뀌면 plan이 흔들립니다. 특정 프로젝트를 참조할 때는 [project.md](project.md)를 사용하세요.

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `sort` | 선택 | 정렬 키 목록. 예: `["createdAt,DESC"]`. |

## 속성

컬렉션 필드: **`items`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 데이터소스 쿼리 식별자. |
| `items` | List(Object) | 반환된 프로젝트 목록. |
| `items[*].id` | String | 프로젝트 ID. |
| `items[*].name` | String | 프로젝트 이름. |
| `items[*].description` | String | 프로젝트 설명. |
| `total_count` | Number | 반환된 프로젝트 수. |

## 관련 항목

- [project.md](project.md) — 단일 프로젝트 조회
- [../resources/project.md](../resources/project.md) — 프로젝트 리소스 (생성)
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/projects.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
