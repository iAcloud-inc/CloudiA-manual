# cloudia_secure_types (데이터소스)

현재 Cloudia 환경에서 인스턴스 생성 시 사용할 수 있는 `secure_type` 후보 목록을 조회합니다. 결과는 호스트 펌웨어·CPU 지원 여부에 따라 달라집니다. `cloudia_instance.secure_type`을 설정하기 전에 이 데이터소스로 환경 가용 여부를 확인할 수 있습니다.

## 예제

```hcl
data "cloudia_secure_types" "available" {}

output "supported_secure_types" {
  value = data.cloudia_secure_types.available.values
}

# SEV 지원 여부 확인
output "supports_sev" {
  value = contains(data.cloudia_secure_types.available.values, "SEV")
}
```

## 인자

이 데이터소스는 별도 인자가 없습니다.

## 속성

컬렉션 필드: **`values`** (Set of String)

| 속성 | 타입 | 설명 |
|---|---|---|
| `values` | Set(String) | 지원되는 secure_type 값 세트 (예: `["NONE", "SEV", "SEV_SNP"]`). |

> `SEV_ES`는 재부팅 불가 제약으로 인해 백엔드 응답에서 제외됩니다. 일반적으로 `NONE`, `SEV`, `SEV_SNP` 중 일부가 반환됩니다.

## 관련 항목

- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스 (`secure_type` 필드)
- [../README.md](../README.md) — Terraform Provider 가이드 목록

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/secure_types.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
