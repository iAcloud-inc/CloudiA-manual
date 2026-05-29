# cloudia_volume

블록 볼륨(비부팅 데이터 디스크)을 생성하는 리소스입니다. 인스턴스에 attach해 추가 디스크로 사용하며, 백엔드 도메인은 `BlockDevice`(비부팅)입니다. 부팅 디스크는 별도 리소스인 `cloudia_image`로 관리됩니다.

## 예제

```hcl
data "cloudia_storage_domains" "all" {}

resource "cloudia_volume" "data" {
  name              = "demo-data"
  description       = "데이터 볼륨 예제"
  size_gib          = 100
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `name` | 볼륨 이름. 최대 80자, 영문자·숫자·`-`·`_` 허용 | 필수 | in-place update 가능 |
| `size_gib` | 볼륨 크기(GiB). 백엔드는 MiB 단위로 저장(`size_gib × 1024`) | 필수 | grow만 in-place, shrink는 destroy + recreate |
| `storage_domain_id` | 볼륨이 위치할 스토리지 도메인 ID. `cloudia_storage_domains` 데이터소스로 조회 | 필수 | 변경 시 **RequiresReplace** |
| `description` | 볼륨 설명. 최대 200자 | 선택 | in-place update 가능 |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`, `size_mib`, `type`, `storage_domain_name`, `storage_domain_type`, `created_at`, `updated_at`

## 운영 노트

- **grow-only**: `size_gib`를 줄이면 Terraform이 destroy + recreate 계획을 수립합니다. shrink는 백엔드에서 `CLERR-401010`으로 거부되므로, 볼륨이 attach된 상태에서 destroy를 시도하면 실패합니다. 먼저 인스턴스에서 볼륨을 detach한 뒤 shrink(destroy + recreate)를 수행하세요.
- **attached 상태에서 destroy 거부**: 볼륨이 인스턴스에 attached된 상태에서 직접 `terraform destroy`를 실행하면 백엔드(`CLERR-401010`)가 삭제를 거부합니다. 인스턴스 리소스에서 볼륨 참조를 먼저 제거하거나 인스턴스를 먼저 삭제하세요.
- **description in-place update**: `description`은 apply 중에 바로 수정됩니다. destroy + recreate 없이 변경할 수 있습니다.
- **storage_domain_id**: `data "cloudia_storage_domains"` 데이터소스를 통해 가용 도메인 목록을 동적으로 조회하고 원하는 타입(`LOCAL`, `CEPH` 등)을 선택하세요.

## Import

```bash
terraform import cloudia_volume.data <project_id>/<volume_id>
```

예시:

```bash
terraform import cloudia_volume.data 1/42
```

import 키 형식: `<project_id>/<volume_id>`

## 관련 항목

- [image.md](image.md) — OS 이미지(부팅 디스크) 업로드
- [nfs_file_system.md](nfs_file_system.md) — NFS 공유 파일시스템
- [virtiofs_file_system.md](virtiofs_file_system.md) — VIRTIOFS host-local 파일시스템
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/volume.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
