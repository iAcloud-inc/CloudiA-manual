# 리소스 import

> 본 문서의 예시는 Cloud:iA dev/test 환경 기준입니다. `<your-...>` 플레이스홀더와 실제 값 매핑은 [플레이스홀더 reference](../README.md#reference-table)를 참고하세요.

이미 백엔드에 존재하는 리소스를 Terraform/OpenTofu state에 가져오는 방법을 설명합니다. import 후 drift 감지 방법과 import를 지원하지 않는 리소스도 함께 안내합니다.

## import key 형식 규칙

Cloud:iA provider는 **슬래시(`/`) 구분 import key**를 사용합니다.

- **프로젝트 최상위 리소스** (`cloudia_project`): `<project_id>` (단일 값, 슬래시 없음)
- **project-scoped 리소스**: `<project_id>/<resource_id>`
- **부모 리소스가 있는 중첩 리소스**: `<project_id>/<parent_id>/<resource_id>`

예를 들어 `cloudia_instance_snapshot`은 인스턴스 아래에 속하므로 key가 `<project_id>/<instance_id>/<snapshot_id>` 형식입니다.

일반적인 import 명령어 형식:

```bash
terraform import <리소스_주소> <import_key>
# 또는 OpenTofu를 사용하는 경우
tofu import <리소스_주소> <import_key>
```

`terraform import`와 `tofu import`는 동일하게 동작합니다. 이 문서의 예시는 `terraform import`를 기준으로 작성했으며, `tofu import`로 그대로 바꿔 쓸 수 있습니다.

## 리소스별 import 형식

| 리소스 | import ID 형식 | 비고 |
|---|---|---|
| `cloudia_project` | `<project_id>` | 최상위 리소스. 슬래시 없음 |
| `cloudia_vpc` | `<project_id>/<vpc_id>` | |
| `cloudia_subnet` | `<project_id>/<vpc_id>/<subnet_id>` | 부모는 VPC |
| `cloudia_security_group` | `<project_id>/<vpc_id>/<security_group_id>` | import 후 `inbound_rules`/`outbound_rules`는 null — HCL에 재선언 필요 |
| `cloudia_default_security_group` | `<project_id>/<vpc_id>` | SG ID가 아닌 VPC ID를 사용. 백엔드가 VPC 기준으로 singleton SG를 결정함 |
| `cloudia_floating_ip` | `<project_id>/<vpc_id>/<floating_ip_id>` | 부모는 VPC |
| `cloudia_instance` | `<project_id>/<instance_id>` | |
| `cloudia_ssh_key` | `<project_id>/<ssh_key_id>` | |
| `cloudia_affinity_group` | `<project_id>/<affinity_group_id>` | |
| `cloudia_instance_snapshot` | `<project_id>/<instance_id>/<snapshot_id>` | 부모는 인스턴스 |
| `cloudia_instance_snapshot_restore` | — | **import 불가** (아래 §참고) |
| `cloudia_volume` | `<project_id>/<volume_id>` | import 후 `description`을 state에서 읽어 HCL에 설정 권장 |
| `cloudia_image` | `<project_id>/<image_id>` | `file_path`는 WriteOnly — import 후 HCL에서 생략 가능 |
| `cloudia_image_clone` | `<project_id>/<image_id>` | `source_image_id`/`target_storage_domain_id`는 RequiresReplace — 값이 다르면 replace 발생 |
| `cloudia_nfs_file_system` | `<project_id>/<file_system_id>` | |
| `cloudia_virtiofs_file_system` | `<project_id>/<file_system_id>` | |

### 예시

```bash
# cloudia_project
terraform import cloudia_project.this 1

# cloudia_vpc
terraform import cloudia_vpc.this 1/42

# cloudia_subnet (VPC 아래 중첩)
terraform import cloudia_subnet.this 1/42/7

# cloudia_security_group (VPC 아래 중첩)
terraform import cloudia_security_group.this 1/42/7

# cloudia_default_security_group (VPC ID로 식별)
terraform import cloudia_default_security_group.this 1/42

# cloudia_floating_ip (VPC 아래 중첩)
terraform import cloudia_floating_ip.this 1/42/7

# cloudia_instance
terraform import cloudia_instance.this 1/42

# cloudia_instance_snapshot (인스턴스 아래 중첩)
terraform import cloudia_instance_snapshot.checkpoint 1/42/7

# cloudia_ssh_key
terraform import cloudia_ssh_key.this 1/42

# cloudia_affinity_group
terraform import cloudia_affinity_group.anti_affinity 1/42

# cloudia_volume
terraform import cloudia_volume.this 1/42

# cloudia_image
terraform import cloudia_image.this 1/42

# cloudia_image_clone
terraform import cloudia_image_clone.this 1/42

# cloudia_nfs_file_system
terraform import cloudia_nfs_file_system.share 1/42

# cloudia_virtiofs_file_system
terraform import cloudia_virtiofs_file_system.shared 1/42
```

## import 불가 리소스

> **import 불가**: `cloudia_instance_snapshot_restore`

`cloudia_instance_snapshot_restore`는 **action 스타일** 리소스입니다. Create 시 스냅샷 복원 작업을 한 번 실행하는 것이 전부이며, Update와 Read는 no-op입니다. 백엔드에 지속 상태로 존재하는 오브젝트가 없으므로 import를 지원하지 않습니다.

이 리소스를 import하려고 하면 오류가 발생합니다. 복원 작업을 다시 수행하려면 리소스를 새로 작성해서 apply하세요.

## import 후 확인

import가 완료된 후에는 반드시 plan을 실행해서 drift를 확인하세요.

```bash
tofu plan
```

백엔드가 HCL에 명시하지 않은 기본값을 가지고 있을 때 drift가 발생합니다. `tofu show <리소스_주소>`로 import된 state를 확인하고 HCL과 비교하세요.

일부 리소스는 import 직후 특정 속성이 null 상태로 들어옵니다.

- `cloudia_security_group`, `cloudia_default_security_group`: `inbound_rules`/`outbound_rules`가 null로 import됩니다. Terraform이 관리하길 원하는 규칙은 HCL에 명시적으로 선언해야 합니다.
- `cloudia_default_security_group`: `description`, `allow_intra_group_traffic`도 마찬가지입니다.

import 관련 오류(예: `Resource ID is malformed`) 또는 import 후 예상치 못한 drift는 [문제 해결 §Import](troubleshooting.md#import)를 참고하세요.

각 리소스의 인자·속성·운영 노트는 [리소스 문서](../README.md#리소스)에서 확인할 수 있습니다.
