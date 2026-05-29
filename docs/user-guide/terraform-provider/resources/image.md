# cloudia_image

OS 이미지(qcow2 / img 포맷)를 프로젝트에 업로드·등록하는 리소스입니다. 백엔드는 `virt-inspector`로 업로드된 파일을 검증하며, 부팅 가능한 x86_64 cloud image여야 합니다.

## 예제

```hcl
data "cloudia_storage_domains" "all" {}

resource "cloudia_image" "custom" {
  file_path         = "/path/to/<your-image-name>.qcow2"
  storage_domain_id = data.cloudia_storage_domains.all.items[0].id
}
```

다른 인스턴스에서 등록된 이미지를 참조할 때는 `data "cloudia_image"` 데이터소스를 사용합니다:

```hcl
data "cloudia_image" "ubuntu" {
  name = "ubuntu-24.04"
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `storage_domain_id` | 이미지를 저장할 스토리지 도메인 ID. `cloudia_storage_domains` 데이터소스로 조회 | 필수 | |
| `file_path` | 업로드할 로컬 이미지 파일 경로. `.qcow2` 또는 `.img`(대소문자 무관) | 선택(WriteOnly) | Create 시에만 필요. 이후 HCL에서 생략 가능 |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`, `name`, `bootable`, `type`, `os_name`, `os_version`, `os_arch`, `os_variant`, `size_bytes`, `min_boot_disk_size_mib`, `default_boot_disk_size_mib`, `storage_domain_name`, `storage_domain_type`, `description`, `system`, `deletable`, `deleted`, `origin_snapshot_id`, `created_at`, `updated_at`

## 운영 노트

- **WriteOnly file_path**: `file_path`는 WriteOnly 속성으로 state에 저장되지 않습니다. 최초 `apply`(Create) 시에만 필요하고, 이후 plan/apply에서 HCL에서 생략해도 replacement가 발생하지 않습니다.
- **다른 파일로 교체**: 이미지 내용을 다른 파일로 바꾸려면 destroy + recreate가 필요합니다. in-place 파일 교체는 지원되지 않습니다.
- **파일 포맷 제한**: 업로드 파일은 `.qcow2` 또는 `.img` 확장자여야 합니다. 다른 포맷은 `qemu-img convert -O qcow2 src.vmdk dst.qcow2`로 변환 후 업로드하세요.
- **빈 이미지 거부**: 백엔드가 `virt-inspector`로 검증하므로, 내용이 없거나 부팅 불가능한 이미지는 `CLERR-402004`로 거부됩니다.
- **import 후 file_path**: import 후 state에 `file_path`가 없으므로 HCL에서 `file_path`를 생략해도 됩니다.
- **인스턴스 참조 패턴**: 등록된 이미지를 인스턴스에서 사용할 때는 `data "cloudia_image"`로 이름 조회 후 ID를 넘기는 패턴을 권장합니다.

## Import

```bash
terraform import cloudia_image.custom <project_id>/<image_id>
```

예시:

```bash
terraform import cloudia_image.custom 1/42
```

import 키 형식: `<project_id>/<image_id>`

import 후 `file_path`는 state에 남지 않으므로 HCL에서 생략 가능합니다.

## 관련 항목

- [image_clone.md](image_clone.md) — 이미지를 다른 스토리지 도메인으로 복제
- [volume.md](volume.md) — 블록 볼륨(비부팅 데이터 디스크)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../guides/import.md](../guides/import.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/image.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
