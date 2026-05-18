# 프로젝트 & 권한 (한국어 카탈로그)

Cloud:iA에서 모든 리소스는 **프로젝트 단위로 격리**됩니다.

> 본 카탈로그는 **최소 동작 예제만** 제공합니다. 전체 schema(모든 인자/속성, 필드 타입, default 값)와 자세한 가이드는 영문 docs를 참고하세요. provider 개발이 진행 중이라 한국어 본은 의도적으로 얇게 유지합니다.

## 페이지 인덱스

- [`cloudia_project` (리소스)](#project)
- [`cloudia_project` (data source, 단일)](#ds-project)
- [`cloudia_projects` (data source, 컬렉션)](#ds-projects)

---

<a id="project"></a>
## `cloudia_project` (리소스)

프로젝트 생성. **admin 권한 필요** — admin alias provider로 호출.

```hcl
resource "cloudia_project" "app" {
  provider     = cloudia.admin
  name         = "app-prod"
  description  = "운영 환경 프로젝트"

  # quota: -1 = 무제한, 0 = 차단(기본값), 양수 = 상한 (MiB 또는 count)
  vcpu_quota      = 64
  memory_quota    = 131072   # 128 GiB
  disk_quota      = 1048576  # 1 TiB
  public_ip_quota = 4
}
```

> ⚠️ **quota 디폴트 0 = 모든 할당 차단**. 새 프로젝트를 만들고 quota를 명시하지 않으면 그 프로젝트에서는 아무 것도 만들 수 없습니다. 특히 `public_ip_quota = 0`이면 VPC 생성도 막힘 (백엔드가 vRouter용 public IP를 자동 할당). 무제한은 `-1`, 사용하지 않을 때도 명시적으로 양수를 적으세요.

**Import**: `terraform import cloudia_project.app <project_id>`

**전체 schema**: [영문 docs/resources/project.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/resources/project.md)

---

<a id="ds-project"></a>
## `cloudia_project` (data source, 단일)

이미 존재하는 프로젝트 1개 조회. `lookup_id` 또는 `name` 중 하나 (ExactlyOneOf).

```hcl
data "cloudia_project" "target" {
  name = "app-prod"
}

resource "cloudia_vpc" "main" {
  project_id = data.cloudia_project.target.id
  name       = "main-vpc"
  cidr       = "10.0.0.0/16"
}
```

**전체 schema**: [영문 docs/data-sources/project.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/project.md)

---

<a id="ds-projects"></a>
## `cloudia_projects` (data source, 컬렉션)

호출자가 볼 수 있는 프로젝트 전체 목록. admin → 전체, 일반 사용자 → 본인 멤버 프로젝트만.

```hcl
data "cloudia_projects" "all" {}

output "project_names" {
  value = data.cloudia_projects.all.items[*].name
}
```

단일 ID 참조용으로 쓰지 마세요 (정렬 순서 변경에 plan이 흔들림) — [Singular vs Plural 가이드](../data-sources.md) 참고.

**전체 schema**: [영문 docs/data-sources/projects.md](https://github.com/iacloud/terraform-provider-cloudia/blob/main/docs/data-sources/projects.md)
