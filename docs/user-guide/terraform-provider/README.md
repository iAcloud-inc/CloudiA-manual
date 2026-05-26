# Cloud:iA Terraform Provider 한국어 가이드

`terraform-provider-cloudia`를 OpenTofu/Terraform로 사용할 때 참고하는 한국어 사용자 가이드입니다.

> 본 문서는 사용자(운영자/개발자) 대상 한국어 매뉴얼입니다. provider 자체와 영문 정식 문서(schema reference)는 추후 Terraform Registry / OpenTofu Registry에 게시될 예정이며, 게시 후에는 그쪽이 영문 SSOT 역할을 합니다.

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

## 가이드 목차

권장 학습 순서:

1. **[개념 정리 (입문자)](concepts.md)** — IaC가 처음이라면 먼저 읽으세요. Terraform/OpenTofu/HCL/Provider/State 같은 용어 정리
2. **[설치하기](install.md)** — provider 로컬 빌드 + `dev_overrides` 설정 (현재 Registry 미배포 상태라 직접 빌드 필요)
3. [인증 (Authentication)](authentication.md) — `auth { ... }` 블록, password vs client_credentials, 환경 변수, admin/user alias 패턴, CI/CD 연동
4. [시작하기 (Getting Started)](getting-started.md) — VPC → subnet → security group → image → SSH key → instance 까지 최소 흐름
5. [데이터소스 선택 (Singular vs Plural)](data-sources.md) — 단일 조회와 컬렉션 조회 중 어떤 것을 쓸지
6. [문제 해결 (Troubleshooting)](troubleshooting.md) — 인증 실패, polling timeout, force-delete, TLS, import 형식 오류 등

이미 IaC에 익숙하다면 1번을 건너뛰고 2번부터 보셔도 됩니다.

### 리소스 / 데이터소스 카탈로그

각 리소스와 데이터소스의 **최소 동작 예제만** 모은 한국어 카탈로그입니다. 전체 필드/속성 표는 provider generated reference를 기준으로 관리되며, 이 한국어 본에서는 사용 예제와 운영상 주의점만 다룹니다.

- [카탈로그 홈 (전체 리소스/데이터소스 인덱스)](catalog/README.md)
- [프로젝트 & 권한](catalog/project.md)
- [네트워크](catalog/network.md) — VPC, subnet, security group
- [컴퓨트](catalog/compute.md) — instance, ssh_key, snapshot, affinity_group + 7 data sources
- [스토리지](catalog/storage.md) — volume, image, file system + 3 data sources

> 깊은 운영 가이드(예: instance의 LIVE/STOP/REPLACE update 분기, GPU/NPU 설정 상세)는 **추후 작성 예정**입니다. provider 안정화 이후 보강합니다.

## 관련 자료

- Cloud:iA UI 기반 사용자 가이드: [user-guide/quickstarts](../quickstarts/README.md), [user-guide/examples-and-labs](../examples-and-labs/README.md)
- Cloud:iA 용어집: [glossary](../../glossary/glossary.md)
- 영문 Provider Reference: 추후 Terraform Registry / OpenTofu Registry에 게시 예정
