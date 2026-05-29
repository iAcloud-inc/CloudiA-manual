# cloudia_ssh_key

프로젝트에 SSH 공개키를 등록하는 리소스입니다. 등록된 키는 인스턴스 생성 시 `cloud_init.ssh_key_ids`로 연결하여 사용합니다.

## 예제

```hcl
resource "cloudia_ssh_key" "me" {
  name       = "my-key"
  public_key = file("~/.ssh/id_ed25519.pub")
}
```

인스턴스에 연결하는 예제:

```hcl
resource "cloudia_instance" "web" {
  # ...
  cloud_init = {
    username    = "appuser"
    ssh_key_ids = [cloudia_ssh_key.me.id]
  }
}
```

## 주요 인자

| 인자 | 설명 | 필수 | 비고 |
|------|------|------|------|
| `name` | SSH 키 이름. 최대 80자, 영문자·숫자·`-`·`_` 허용 | 필수 | |
| `public_key` | OpenSSH 공개키 문자열(예: `ssh-rsa AAAA... user@host`) | 필수 | **RequiresReplace** — 변경 시 새 리소스 생성 |
| `project_id` | 상위 프로젝트 ID. 생략 시 provider 기본값 사용 | 선택 | |

**읽기 전용 출력값**: `id`, `fingerprint`, `bind_guest_machine_count`, `deletable`, `created_at`, `updated_at`

## 운영 노트

- **RequiresReplace**: `public_key`를 변경하면 기존 리소스가 삭제되고 새 리소스가 생성됩니다. 인스턴스에 키가 연결된 상태에서 교체할 때는 ① 새 SSH 키 리소스 추가 → ② 인스턴스 `cloud_init.ssh_key_ids` 교체 → ③ 기존 키 리소스 삭제 순서로 진행하는 것을 권장합니다.
- **deletable 플래그**: 인스턴스에 이 키가 유일한 인증 수단(비밀번호 미설정, 다른 SSH 키 없음)으로 등록된 경우 백엔드가 `deletable = false`를 반환하고, 해당 상태에서 `public_key` 교체(destroy+create)는 plan 단계에서 차단됩니다.
- **幂等성**: 이미 등록된 `public_key`를 다시 선언하면 기존 행을 채택(adopt)하며 중복 생성하지 않습니다. 동시 apply나 재실행에서도 안전합니다.
- **import 후 드리프트**: import 이후 state에는 백엔드가 반환한 `public_key` 값이 저장됩니다. HCL 값이 백엔드 반환값과 정확히 일치하지 않으면 다음 plan에서 RequiresReplace diff가 발생할 수 있으므로 주의하세요.

## Import

```bash
terraform import cloudia_ssh_key.me <project_id>/<ssh_key_id>
```

예시:

```bash
terraform import cloudia_ssh_key.me 1/42
```

import 키 형식: `<project_id>/<ssh_key_id>`

## 관련 항목

- [../guides/import.md](../guides/import.md)
- [../guides/common-workflows.md](../guides/common-workflows.md)
- [../README.md](../README.md)

---

> 전체 필드/속성 표는 영문 레퍼런스 문서(provider `docs/resources/ssh_key.md`)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
