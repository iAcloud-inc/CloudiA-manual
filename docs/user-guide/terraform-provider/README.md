# Cloud:iA Terraform Provider 한국어 가이드

`terraform-provider-cloudia`를 OpenTofu/Terraform로 사용할 때 참고하는 한국어 사용자 가이드입니다.

> 본 문서는 사용자(운영자/개발자) 대상 한국어 매뉴얼입니다. 전체 schema 등 영문 정식 문서는 provider의 영문 레퍼런스를 기준으로 합니다.

## 본 매뉴얼의 표기 원칙

코드 예시에 등장하는 값은 두 종류로 구분합니다.

- **`<your-...>` 플레이스홀더** — 환경마다 또는 사용자마다 달라지는 값. 그대로 복사해서 쓰면 동작하지 않습니다. 본인 환경 값으로 바꾸세요.
- **고정 예시값 (예: 예제 CIDR `10.0.0.0/16`)** — 그대로 가져다 써도 의미가 통하는 일반 예시.

민감 정보(`<your-password>`, `<your-client-secret>` 등)는 **HCL에 평문으로 적지 말고** 환경 변수 또는 secret manager로 주입하세요.

<a id="reference-table"></a>
## 플레이스홀더 reference

본 매뉴얼 전체에서 일관되게 쓰이는 `<your-...>` 플레이스홀더 목록입니다. 실제 값은 본인이 사용하는 Cloud:iA 환경의 운영자에게 문의하세요.

| 플레이스홀더 | 의미 | 비고 |
|---|---|---|
| `<your-cloudia-endpoint>` | Cloud:iA API endpoint URL | 예: `https://cloudia.example.com` |
| `<your-api-base-path>` | API base path prefix | 설치본이 subpath에 마운트된 경우만 필요 (예: `/cloudia`), 그렇지 않으면 빈 문자열 |
| `<your-auth-type>` | `password` 또는 `client_credentials` | 사람이 직접 실행 시 `password`, 자동화 시 `client_credentials` |
| `<your-client-id>` | OAuth2 client ID | 운영자에게서 발급 |
| `<your-client-secret>` | OAuth2 client secret | **민감 정보** — secret manager에서 주입 |
| `<your-username>` | Cloud:iA 계정명 | **민감 정보** |
| `<your-password>` | Cloud:iA 계정 비밀번호 | **민감 정보** |
| `<your-project-id>` | 작업 대상 project ID | 콘솔 또는 `cloudia_projects` data source로 조회 |
| `<your-vpc-cidr>` | VPC CIDR | 예: `10.0.0.0/16` |
| `<your-subnet-cidr>` | 서브넷 CIDR | VPC CIDR 안의 블록 |
| `<your-admin-cidr>` | 보안그룹 inbound 허용 대역 | 관리자 대역 권장. `0.0.0.0/0`은 금지 |
| `<your-image-name>` | OS 이미지 이름 | 환경마다 다름. 운영자에게 확인 |
| `<your-instance-type-name>` | 인스턴스 타입 이름 | 환경마다 다름 |
| `<your-ca-bundle>` | CA 인증서 경로 | self-signed 클러스터에서만 필요 (예: `~/cloudia-certs/ca-certificate.crt`) |

## 문서 구성

본 매뉴얼은 세 부분으로 구성됩니다.

- **[가이드](guides/README.md)** — 개념·설치·설정·인증·워크플로·문제 해결. IaC가 처음이거나 환경을 처음 세팅한다면 여기부터 시작하세요.
- **[리소스](resources/README.md)** — `cloudia_*` 리소스 16종의 사용 예제와 운영 노트.
- **[데이터소스](data-sources/README.md)** — 기존 리소스·카탈로그를 조회하는 데이터소스 18종.

처음이라면 권장 순서: [개념 정리](guides/concepts.md) → [설치하기](guides/installation.md) → [Provider 설정](guides/configuration.md) → [인증](guides/authentication.md) → [시작하기](guides/getting-started.md). 이미 IaC에 익숙하다면 설치부터 보셔도 됩니다.

## 관련 자료

- Cloud:iA UI 기반 사용자 가이드: [user-guide/quickstarts](../quickstarts/README.md), [user-guide/examples-and-labs](../examples-and-labs/README.md)
- Cloud:iA 용어집: [glossary](../../glossary/glossary.md)
- 영문 Provider Reference: provider 저장소의 `docs/resources/`, `docs/data-sources/`
