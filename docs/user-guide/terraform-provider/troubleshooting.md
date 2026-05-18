# 문제 해결 (Troubleshooting)

> 영문 SSOT: `terraform-provider-cloudia/docs/guides/troubleshooting.md`. 본 한국어 본은 그 sibling이며, 차이가 있을 경우 영문판이 우선합니다.
>
> 본 문서의 예시는 사내 dev 클러스터(`192.168.160.10`) 기준입니다. `<your-...>` 플레이스홀더와 실제 값 매핑은 [가이드 홈의 Reference 표](README.md#reference-table)를 참고하세요.

Cloud:iA provider를 처음 도입할 때 가장 자주 마주치는 문제를 모았습니다. credential 설정은 [인증](authentication.md), 전체 흐름은 [시작하기](getting-started.md)를 먼저 참고하세요.

<a id="auth"></a>
## 인증

### 첫 apply에서 `401 Unauthorized`

`/oauth2/token`으로의 OAuth2 토큰 요청이 실패했습니다. 다음을 순서대로 확인하세요.

1. `auth.type = "password"` (기본)일 때: `CLOUDIA_AUTH_USERNAME` / `CLOUDIA_AUTH_PASSWORD`가 대상 `CLOUDIA_ENDPOINT`의 실제 계정과 일치하는지.
2. `CLOUDIA_AUTH_CLIENT_ID` / `CLOUDIA_AUTH_CLIENT_SECRET`가 백엔드에 등록된 OAuth2 client에 대응하는지. `password`에서 쓰는 client (예: `cloudia-secure-login` 같은 login client)는 사용자 credential과 *별개*이고, `client_credentials`용 service-account client와도 *다릅니다* — 각 client 발급 절차는 Cloud:iA 운영자에게 확인하세요.
3. `CLOUDIA_API_BASE_PATH`가 대상 환경에 맞는지 (예: API를 subpath 아래에 마운트한 설치에서는 `/cloudia`).
4. `auth.type = "client_credentials"`이면 `username`/`password`는 전혀 사용되지 않습니다. service-account client가 백엔드에서 활성화되어 있는지 다시 확인하세요.

Cloud:iA OAuth2 client가 아직 없다면 client registry를 관리하는 Cloud:iA 운영자에게 발급을 요청해야 합니다. provider가 client를 스스로 부트스트랩하지는 않습니다.

### project-scoped 리소스 생성에서 `403 Forbidden`

credential 자체는 유효하지만 권한이 부족한 경우입니다. 대표적인 원인: 일반 사용자 계정으로 `cloudia_project`를 만들려고 했거나, 대상 project에 속하지 않은 admin 전용 계정으로 `cloudia_vpc`를 만들려고 한 경우. provider 설정을 `admin`/`user` alias로 분리하세요 — [인증 §Admin vs User alias 패턴](authentication.md#admin-user-alias) 참고.

### `Project context is required` 또는 `project_id is empty`

project-scoped 리소스(VPC, subnet, security group, instance 등)가 project context를 결정하지 못했습니다. 다음 중 하나를 설정하세요.

- `CLOUDIA_PROJECT_ID` 환경 변수 (provider 기본값)
- `provider "cloudia" { project_id = ... }` (HCL)
- 리소스 자체의 `project_id = ...`

리소스 레벨 값이 provider 레벨 값보다 우선합니다.

<a id="async-polling"></a>
## 비동기 polling

Cloud:iA의 대부분 쓰기 작업은 `requestId`와 함께 `202 Accepted`를 반환합니다. provider가 완료까지 polling해주므로 사용자 입장에서는 `plan`/`apply`가 동기처럼 보입니다. polling 동작은 두 개의 knob으로 제어됩니다.

| 환경 변수 | 기본값 | 효과 |
|---|---|---|
| `CLOUDIA_POLL_INTERVAL_SECONDS` | `5` | `/requests/{id}` 조회 주기 |
| `CLOUDIA_POLL_TIMEOUT_SECONDS` | `600` | 실패로 간주하기 전까지의 polling 최대 시간 |

### `polling timed out after 600s`

timeout 안에 작업이 끝나지 않았습니다. 대응 옵션:

1. **기다렸다 재시도** — Cloud:iA 콘솔에서 작업이 실제로 끝났는지 확인하세요. 끝났다면 `tofu apply`를 다시 실행하면 다음 read에서 state가 reconcile됩니다.
2. **timeout 증가** — 느린 image copy가 필요한 인스턴스의 경우 `CLOUDIA_POLL_TIMEOUT_SECONDS`를 더 큰 값 (예: `1800`)으로 설정.
3. **stuck instance에 한정한 escape hatch** — provider 블록에 `instance_force_delete_on_timeout = true`를 설정. `cloudia_instance` delete polling이 timeout에 도달하면 provider가 백엔드 force-delete endpoint를 fallback으로 호출합니다. 운영 사고용 대피로이지 일상 설정이 아닙니다 — provider schema의 caveat을 반드시 읽어보세요.

### apply가 오류 없이 멈춘 것처럼 보일 때

polling은 기본적으로 조용합니다. hang이 의심되면 디버그 로깅을 켜세요.

```bash
TF_LOG=DEBUG tofu apply
```

`cloudia: polling requestId=...` 라인을 보세요. 같은 `requestId`가 상태 변화 없이 반복된다면 백엔드가 stuck입니다 — request ID를 들고 운영팀에 에스컬레이션하세요.

## 동시성

### 여러 VPC를 한 번에 apply할 때 `cloudia_vpc` Create가 간헐적으로 실패

Cloud:iA 백엔드의 vRouter 자동 생성 경로는 단일 `tofu apply` 내에서 여러 VPC를 동시에 생성할 때 race-safe하지 않습니다. 증상: 산발적인 5xx, 일부 VPC의 default security group / DNS gateway 누락, 주소 할당 충돌.

회피 방법: OpenTofu / Terraform의 apply parallelism flag로 리소스 Create를 직렬화하세요.

```bash
tofu apply -parallelism=1
```

`-parallelism=1`은 apply 동안 전체 리소스 그래프를 직렬화하므로 다소 무거운 옵션입니다. 큰 구성이라 VPC만 직렬화하고 싶다면 VPC 생성을 별도 apply (또는 별도 workspace)로 분리하고, 나머지는 기본 parallelism (`10`)으로 돌리세요. provider 자체에 직렬화를 박아두지는 않았습니다 — 호출 단위 opt-in입니다. 백엔드 race가 수정되면 본 가이드는 제거됩니다.

<a id="tls"></a>
## TLS

### `x509: certificate signed by unknown authority`

provider가 검증할 수 없는 인증서를 가진 endpoint에 접속했습니다. self-signed cert를 쓰는 개발 환경에서 흔합니다 — 사내 dev 클러스터(`192.168.160.10`)가 이 경우에 해당합니다.

#### 옵션 1 — CA를 시스템 trust store에 등록 (권장)

운영자에게서 받은 CA 인증서를 시스템 trust store에 추가하면 `tls_insecure` 없이도 검증을 통과합니다.

- 사내 dev에서 받는 CA 경로 예시: `<your-ca-bundle>` (본인 환경에 보관한 위치. 예: `~/cloudia-certs/ca-certificate.crt`)
- macOS:
  ```bash
  sudo security add-trusted-cert -d -r trustRoot \
      -k /Library/Keychains/System.keychain <your-ca-bundle>
  ```
- Linux (Debian/Ubuntu):
  ```bash
  sudo cp <your-ca-bundle> /usr/local/share/ca-certificates/cloudia-dev.crt
  sudo update-ca-certificates
  ```

#### 옵션 2 — `CLOUDIA_TLS_INSECURE=true` (dev 전용, 최후의 수단)

```bash
export CLOUDIA_TLS_INSECURE=true
```

TLS 검증을 완전히 비활성화하므로 control plane 트래픽이 MITM에 노출됩니다. **운영 환경에서는 절대 쓰지 마세요.** 사내 dev 클러스터에서만, CA 등록이 어려운 일시적 상황(예: 임시 컨테이너 안)에서 임시로 사용하세요.

## Import

### `Resource ID is malformed`

project-scoped 리소스는 슬래시 구분 import key를 씁니다. 형식은 각 리소스의 Import 섹션에 문서화되어 있습니다. 예:

| 리소스 | Import 형식 |
|---|---|
| `cloudia_project` | `<project_id>` |
| `cloudia_vpc` | `<project_id>/<vpc_id>` |
| `cloudia_subnet` | `<project_id>/<vpc_id>/<subnet_id>` |
| `cloudia_security_group` | `<project_id>/<vpc_id>/<security_group_id>` |
| `cloudia_instance` | `<project_id>/<instance_id>` |

`cloudia_instance_snapshot_restore`는 action 스타일 리소스로 import를 지원하지 않습니다.

### Import는 성공했는데 `plan`에 drift가 잡힐 때

백엔드가 HCL에 명시하지 않은 기본값을 반환했을 수 있습니다. 가져온 state를 `tofu show <addr>`로 보고 HCL과 비교한 뒤, 누락된 속성을 추가하거나 drift를 수용하세요. ForceNew 속성(예: instance의 `network_id`, `image_id`)은 `plan`으로 reconcile되지 않습니다 — 리소스를 다시 만들어야 합니다.

## 버그 리포트

위 어느 항목에도 해당하지 않으면, 다음을 모아 provider 저장소의 issue tracker에 등록해 주세요.

- provider 버전 (`tofu version` 출력)
- Terraform/OpenTofu 버전
- HCL 스니펫 (credential은 redact)
- 실패 주변의 `TF_LOG=DEBUG` 로그
- 관련된 백엔드 `requestId`
