# cloudia_ssh_key (데이터소스)

프로젝트에 등록된 SSH 키 한 개를 조회합니다. `lookup_id`(ID 직접 지정) 또는 `name`(이름 조회) 중 하나를 지정합니다. 같은 이름을 가진 키가 여러 개인 경우 에러가 발생합니다.

## 예제

```hcl
# 이름으로 조회
data "cloudia_ssh_key" "deploy" {
  name = "deploy"
}

# 인스턴스 cloud_init에 참조
resource "cloudia_instance" "demo" {
  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [data.cloudia_ssh_key.deploy.id]
  }
  # ...
}

output "deploy_key_fingerprint" {
  value = data.cloudia_ssh_key.deploy.fingerprint
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `lookup_id` | 선택 (ExactlyOneOf) | 조회할 SSH 키 ID. `name`과 둘 중 하나만 지정. |
| `name` | 선택 (ExactlyOneOf) | 조회할 SSH 키 이름. 이름 중복이면 에러. |
| `project_id` | 선택 | 프로젝트 ID. 생략 시 provider 설정값 사용. |

## 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 조회된 SSH 키 ID. |
| `public_key` | String | OpenSSH 공개키 문자열. |
| `fingerprint` | String | Cloudia가 계산한 SSH 키 지문. |
| `bind_guest_machine_count` | Number | 현재 이 키가 바인딩된 인스턴스 수. |
| `deletable` | Boolean | 삭제 가능 여부. 이 키를 제거하면 인스턴스에 인증 수단이 없어지는 경우 `false`. |
| `created_at` | String | 생성 시각. |
| `updated_at` | String | 마지막 수정 시각. |

## 관련 항목

- [../resources/ssh_key.md](../resources/ssh_key.md) — SSH 키 리소스 (등록)
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스 (`cloud_init.ssh_key_ids`)

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/ssh_key.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
