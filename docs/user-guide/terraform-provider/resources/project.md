# cloudia_project

프로젝트(리소스 격리·할당 단위)를 생성하는 리소스입니다. Cloud:iA의 모든 리소스는 프로젝트 단위로 격리되며, 프로젝트 생성과 삭제에는 **admin 권한**이 필요합니다. 반드시 `alias = "admin"` 으로 구성된 provider를 사용하세요([provider 구성 가이드](../guides/configuration.md)).

## 예제

```hcl
provider "cloudia" {
  alias    = "admin"
  endpoint = var.cloudia_endpoint
  auth {
    type     = "password"
    username = var.cloudia_admin_username
    password = var.cloudia_admin_password
  }
}

resource "cloudia_project" "app" {
  provider    = cloudia.admin
  name        = "app-prod"
  description = "운영 환경 프로젝트"

  # quota: -1 = 무제한, 0 = 차단(기본값), 양수 = 상한 (MiB 또는 count)
  vcpu_quota      = 64
  memory_quota    = 131072   # 128 GiB (MiB 단위)
  disk_quota      = 1048576  # 1 TiB (MiB 단위)
  public_ip_quota = 4
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `name` | 프로젝트 이름. 최대 20자, 영문자·숫자·`-`·`_` 허용 | 필수 | |
| `description` | 프로젝트 설명. 최대 200자 | 선택 | |
| `vcpu_quota` | vCPU 할당 상한 (개수). `-1` = 무제한, `0` = 차단(기본값), 양수 = 상한 | 선택 | |
| `memory_quota` | 메모리 할당 상한 (MiB 단위). `-1` = 무제한, `0` = 차단(기본값), 양수 = 상한 | 선택 | |
| `disk_quota` | 디스크(볼륨·이미지·파일시스템 합산) 할당 상한 (MiB 단위). `-1` = 무제한, `0` = 차단(기본값), 양수 = 상한 | 선택 | |
| `public_ip_quota` | 공인 IP 할당 상한 (개수). `-1` = 무제한, `0` = 차단(기본값), 양수 = 상한 | 선택 | |

**읽기 전용 출력값**: `id`, `quota_enabled`

> `quota_enabled` 는 항상 `true`로 반환됩니다. 프로젝트 quota는 항상 활성화 상태로 관리되며, 별도 비활성화 옵션은 제공되지 않습니다.

## 운영 노트

- **admin 권한 필수**: 프로젝트 생성·삭제는 일반 사용자 권한으로 불가합니다. `provider = cloudia.admin` 처럼 admin alias provider를 명시해야 합니다([provider 구성 가이드](../guides/configuration.md)).
- **quota 기본값 0 = 모든 할당 차단**: 새 프로젝트에서 quota 인자를 명시하지 않으면 기본값 `0`이 적용되어 해당 프로젝트에서 아무 리소스도 생성할 수 없습니다. 반드시 `-1`(무제한) 또는 적절한 양수로 설정하세요.
- **VPC 생성과 `public_ip_quota`**: VPC를 생성하면 백엔드가 vRouter용 공인 IP를 자동으로 1개 할당합니다. `public_ip_quota = 0` 상태에서 VPC를 생성하려 하면 API가 `CLERR-312003` 에러를 반환합니다. VPC를 사용하려면 `public_ip_quota >= 1` 이상으로 설정하세요.
- **프로젝트 삭제 전 의존 리소스 제거**: `terraform destroy` 로 프로젝트를 삭제하기 전에 해당 프로젝트 내의 모든 리소스(VPC, 인스턴스, 볼륨 등)를 먼저 제거해야 합니다. 의존 리소스가 남아 있으면 API가 에러를 반환합니다.
- **in-place 업데이트**: `name`, `description`과 각 quota 값(`vcpu_quota` 등)은 프로젝트를 재생성하지 않고 그대로 수정됩니다. 운영 중에도 할당량을 올릴 수 있습니다.

## Import

```bash
terraform import cloudia_project.app <project_id>
```

예시:

```bash
terraform import cloudia_project.app 1
```

import 키 형식: `<project_id>`

Import 후 Terraform 상태와 실제 설정이 일치하는지 확인하는 방법은 [import 가이드](../guides/import.md)를 참고하세요.

## 관련 항목

- [vpc.md](vpc.md) — 프로젝트 내 가상 사설 네트워크
- [../guides/configuration.md](../guides/configuration.md) — admin alias provider 구성
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)
- [cloudia_project (데이터소스)](../data-sources/project.md) — 기존 프로젝트 정보 조회
- [cloudia_projects (데이터소스)](../data-sources/projects.md) — 프로젝트 목록 조회

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/project.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
