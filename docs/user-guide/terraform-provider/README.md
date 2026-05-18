# Cloud:iA Terraform Provider 한국어 가이드

`terraform-provider-cloudia`(Terraform Registry: `iacloud/cloudia`)를 OpenTofu/Terraform로 사용할 때 참고하는 한국어 사용자 가이드입니다.

> 본 문서는 사용자(운영자/개발자) 대상 한국어 매뉴얼입니다. 영문 정식 문서는 Terraform Registry와 provider 저장소 [`terraform-provider-cloudia`](https://github.com/iacloud/terraform-provider-cloudia)의 `docs/guides/`에서 확인할 수 있으며, 본 한국어 본은 그 sibling으로 운영됩니다. 영문판이 정식 정의(SSOT)이며, 차이가 있을 경우 영문판을 따릅니다.

## 본 매뉴얼의 표기 원칙

코드 예시에 등장하는 값은 두 종류로 구분합니다.

- **`<your-...>` 플레이스홀더** — 환경마다 또는 사용자마다 달라지는 값. 그대로 복사해서 쓰면 동작하지 않습니다. 본인 환경 값으로 바꾸세요.
- **고정 예시값 (예: 표준 client_id, CIDR 예시)** — 그대로 가져다 써도 의미가 통하는 일반 예시.

민감 정보(`<your-password>`, `<your-client-secret>` 등)는 **HCL에 평문으로 적지 말고** 환경 변수 또는 secret manager로 주입하세요.

<a id="reference-table"></a>
## Reference: 사내 dev (192.168.160.10) 환경 값

본 매뉴얼을 작성할 때 검증한 사내 dev 클러스터의 실제 설정값입니다. 본인 환경이 이와 다르면 `<your-...>` 플레이스홀더 자리에 본인 값을 채우세요.

| 플레이스홀더 | 사내 dev 실값 | 비고 |
|---|---|---|
| `<your-endpoint>` | `https://192.168.160.10` | dev cluster (TLS self-signed) |
| `<your-api-base-path>` | `/cloudia` | 설치본이 subpath에 마운트되어 있음. 운영 환경은 보통 비워둠 |
| `<your-auth-type>` | `password` | 사람이 직접 실행 시 |
| `<your-client-id>` | `cloudia-secure-login` | login client 표준 이름. 운영 클러스터에서 같은 이름을 쓸 수도 있고 다를 수도 있음 |
| `<your-client-secret>` | (마스킹) | **민감 정보** — secret manager에서 주입 |
| `<your-username>` | (마스킹) | **민감 정보** — 본인 Cloud:iA 계정명 |
| `<your-password>` | (마스킹) | **민감 정보** — 본인 Cloud:iA 계정 비밀번호 |
| `<your-tls-insecure>` | `true` | **dev only**. 운영 환경에서는 `false` (또는 미설정) + CA를 시스템 trust store에 등록 |
| `<your-project-id>` | `25` (사내 dev에서 예시로 사용) | 실제 project ID는 콘솔 또는 `cloudia_projects` data source로 확인 |
| `<your-vpc-cidr>` | `10.250.0.0/16` (예시) | 본인 네트워크 설계에 맞게 선택 |
| `<your-subnet-cidr>` | `10.250.1.0/24` (예시) | VPC CIDR 안의 서브넷 |
| `<your-ca-bundle>` | `~/cloudia-certs/ca-certificate.crt` (일반화 표기) | 사내 dev: `/Users/<you>/iacloud/certs/<env>/certs/ca/ca-certificate.crt` 형태로 발급받아 보관 |

> **dev 클러스터 접속 정보가 필요하다면**: 본 매뉴얼은 그 값을 포함하지 않습니다. 사내 운영자에게 client secret, 계정 자격증명, CA bundle을 요청하세요.

## 가이드 목차

권장 학습 순서:

1. **[개념 정리 (입문자)](concepts.md)** — IaC가 처음이라면 먼저 읽으세요. Terraform/OpenTofu/HCL/Provider/State 같은 용어 정리
2. **[설치하기](install.md)** — provider 로컬 빌드 + `dev_overrides` 설정 (현재 Registry 미배포 상태라 직접 빌드 필요)
3. [인증 (Authentication)](authentication.md) — `auth { ... }` 블록, password vs client_credentials, 환경 변수, admin/user alias 패턴, CI/CD 연동
4. [시작하기 (Getting Started)](getting-started.md) — VPC → subnet → security group → image → SSH key → instance 까지 최소 흐름
5. [데이터소스 선택 (Singular vs Plural)](data-sources.md) — 단일 조회와 컬렉션 조회 중 어떤 것을 쓸지
6. [문제 해결 (Troubleshooting)](troubleshooting.md) — 인증 실패, polling timeout, force-delete, TLS, import 형식 오류 등

이미 IaC에 익숙하다면 1번을 건너뛰고 2번부터 보셔도 됩니다.

## 관련 자료

- Cloud:iA UI 기반 사용자 가이드: [user-guide/quickstarts](../quickstarts/README.md), [user-guide/examples-and-labs](../examples-and-labs/README.md)
- 영문 Provider Reference (Terraform Registry): `iacloud/cloudia`
- 영문 가이드 SSOT: provider 저장소 `docs/guides/`
- 이슈/개선 제안: provider 저장소 issue tracker
