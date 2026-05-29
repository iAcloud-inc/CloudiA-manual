# cloudia_image_clone

기존 이미지를 다른 스토리지 도메인으로 복제하는 리소스입니다. LOCAL → CEPH 등 스토리지 도메인 간 이동에 활용하며, 복제 결과는 독립적인 새 이미지 ID로 노출됩니다. `terraform destroy` 시 복제된 이미지가 백엔드에서 삭제됩니다.

## 예제

```hcl
data "cloudia_storage_domains" "all" {}

resource "cloudia_image" "source" {
  file_path         = "/path/to/<your-image-name>.qcow2"
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
}

# 소스 이미지를 다른 스토리지 도메인(예: CEPH)으로 복제
resource "cloudia_image_clone" "on_ceph" {
  source_image_id   = cloudia_image.source.id
  storage_domain_id = data.cloudia_storage_domains.all.items[1].id   # 대상 SD(CEPH 등)
}
```

인스턴스에서 복제된 이미지를 사용할 때는 `cloudia_image_clone.on_ceph.id`를 인스턴스의 `image_id`에 넘기세요.

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `source_image_id` | 복제 원본 이미지 ID. 같은 프로젝트 내에 존재해야 합니다 | 필수 | 변경 시 **RequiresReplace** |
| `storage_domain_id` | 복제 대상 스토리지 도메인 ID. `cloudia_storage_domains` 데이터소스로 조회 | 필수 | 변경 시 **RequiresReplace** |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`, `name`, `bootable`, `type`, `os_name`, `os_version`, `os_arch`, `os_variant`, `size_bytes`, `min_boot_disk_size_mib`, `default_boot_disk_size_mib`, `storage_domain_name`, `storage_domain_type`, `description`, `system`, `deletable`, `deleted`, `origin_snapshot_id`, `created_at`, `updated_at`

## 운영 노트

- **RequiresReplace**: `source_image_id`와 `storage_domain_id` 모두 변경 시 기존 복제 이미지를 destroy 후 재생성합니다.
- **중복 복제 주의**: 백엔드는 동일 `source_image_id` + `storage_domain_id` 조합의 중복을 방지하지 않습니다. `terraform apply`를 재실행하면 이미 복제본이 있어도 새 이미지가 생성됩니다. 모듈 레벨에서 중복 호출을 방지하세요(예: `for_each` 관리).
- **복제된 이미지 ID**: 복제 결과는 새 이미지 ID(`cloudia_image_clone.<name>.id`)로 노출됩니다. 인스턴스의 `image_id`에 이 값을 사용하세요.
- **import 후 HCL 검증**: import 후 `source_image_id`와 `storage_domain_id`가 원본과 다르면 다음 plan 시 replacement가 발생합니다. import 후 반드시 HCL 값을 원본과 일치시키세요.

## Import

```bash
terraform import cloudia_image_clone.on_ceph <project_id>/<image_id>
```

예시:

```bash
terraform import cloudia_image_clone.on_ceph 1/42
```

import 키 형식: `<project_id>/<image_id>` (복제된 이미지의 ID)

## 관련 항목

- [image.md](image.md) — 원본 OS 이미지 업로드
- [volume.md](volume.md) — 블록 볼륨(비부팅 데이터 디스크)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/image_clone.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
