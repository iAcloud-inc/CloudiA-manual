# cloudia_images (데이터소스)

프로젝트 내 이미지 목록을 조회합니다. `name` 필터로 특정 이름의 이미지만 좁힐 수 있습니다. 특정 이미지 한 개를 ID나 이름으로 정확히 참조할 때는 [image.md](image.md)를 사용하세요.

## 예제

```hcl
# 전체 이미지 목록
data "cloudia_images" "all" {}

output "image_names" {
  value = data.cloudia_images.all.items[*].name
}

# 이름으로 필터
data "cloudia_images" "ubuntu" {
  name = "ubuntu-24.04"
}

output "ubuntu_image_id" {
  value = data.cloudia_images.ubuntu.items[0].id
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `name` | 선택 | 정확히 일치하는 이름 필터. 생략 시 전체 목록 반환. |
| `project_id` | 선택 | 프로젝트 ID. 생략 시 provider 설정값 사용. |

## 속성

컬렉션 필드: **`items`** / 카운트 필드: **`total_count`**

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 데이터소스 식별자 (고정값 `images`). |
| `items` | List(Object) | 필터 후 이미지 요약 목록. |
| `items[*].id` | String | 이미지 ID. |
| `items[*].name` | String | 이미지 이름. |
| `items[*].bootable` | Boolean | 부팅 가능 여부. |
| `items[*].deleted` | Boolean | 소프트 삭제 상태. |
| `items[*].description` | String | 이미지 설명. |
| `items[*].os_variant` | String | OS 변형 식별자. |
| `items[*].storage_domain_id` | String | 이미지가 저장된 스토리지 도메인 ID. |
| `items[*].storage_domain_name` | String | 이미지가 저장된 스토리지 도메인 이름. |
| `items[*].system` | Boolean | 시스템 제공 이미지 여부. |
| `total_count` | Number | 필터 후 반환된 이미지 수. |

## 관련 항목

- [image.md](image.md) — 단일 이미지 상세 조회
- [../resources/image.md](../resources/image.md) — 이미지 리소스 (업로드)
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/images.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
