# cloudia_image (데이터소스)

이름 또는 ID로 기존 이미지 한 개를 조회합니다. 인스턴스 부팅 이미지 ID를 동적으로 참조하거나, 콘솔에서 업로드한 이미지를 IaC에서 가져올 때 사용합니다. 컬렉션 반복·필터가 필요할 때는 [images.md](images.md)를 사용하세요.

## 예제

```hcl
# 이름으로 조회
data "cloudia_image" "ubuntu" {
  name = "ubuntu-24.04"
}

# ID로 조회
data "cloudia_image" "by_id" {
  lookup_id = "42"
}

resource "cloudia_instance" "web" {
  image_id = data.cloudia_image.ubuntu.id
  # ...
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `lookup_id` | 선택 (ExactlyOneOf) | 조회할 이미지 ID. `name`과 둘 중 하나만 지정. |
| `name` | 선택 (ExactlyOneOf) | 조회할 이미지 이름. |
| `project_id` | 선택 | 프로젝트 ID. 생략 시 provider 설정값 사용. |

## 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 조회된 이미지 ID. |
| `bootable` | Boolean | 부팅 가능 여부. `true`이면 인스턴스 OS 이미지로 사용 가능; `false`이면 데이터 디스크 전용. |
| `default_boot_disk_size_mib` | Number | 이 이미지로 부팅할 때 권장 부팅 디스크 크기 (MiB). |
| `deleted` | Boolean | 소프트 삭제 여부. `true`이면 사용 불가. |
| `description` | String | 이미지 설명. |
| `min_boot_disk_size_mib` | Number | 이 이미지로 부팅할 때 최소 부팅 디스크 크기 (MiB). |
| `os_arch` | String | OS 아키텍처 (예: `x86_64`, `arm64`). |
| `os_name` | String | OS 계열 (예: `ubuntu`, `centos`). |
| `os_variant` | String | OS 변형 식별자. libvirt OS 정보 매핑에 사용. |
| `os_version` | String | OS 버전 (예: `24.04`). |
| `storage_domain_id` | String | 이미지가 저장된 스토리지 도메인 ID. |
| `storage_domain_name` | String | 이미지가 저장된 스토리지 도메인 이름. |
| `system` | Boolean | 시스템 제공 이미지 여부. `true`이면 백엔드 관리 이미지로 사용자가 수정하거나 삭제할 수 없음. |

## 관련 항목

- [images.md](images.md) — 필터로 여러 이미지 조회
- [../resources/image.md](../resources/image.md) — 이미지 리소스 (업로드)
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/image.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
