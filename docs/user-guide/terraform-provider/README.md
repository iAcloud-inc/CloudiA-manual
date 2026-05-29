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

## 가이드

권장 학습 순서:

1. **[개념 정리 (입문자)](guides/concepts.md)** — IaC가 처음이라면 먼저 읽으세요. Terraform/OpenTofu/HCL/Provider/State 같은 용어 정리
2. **[설치하기](guides/installation.md)** — provider 로컬 빌드 + `dev_overrides` 설정 (현재 Registry 미배포 상태라 직접 빌드 필요)
3. [Provider 설정](guides/configuration.md) — `provider "cloudia"` 블록, endpoint·api_base_path, admin/user alias, 환경 변수, TLS
4. [인증](guides/authentication.md) — `auth { ... }` 블록, password vs client_credentials, 환경 변수, CI/CD 연동
5. [시작하기](guides/getting-started.md) — VPC → subnet → security group → image → SSH key → instance 까지 최소 흐름
6. [자주 쓰는 워크플로](guides/common-workflows.md) — 멀티 NIC, 데이터 볼륨, 스냅샷/롤백, 플로팅 IP, NFS 공유, 골든 이미지
7. [데이터소스 선택 (Singular vs Plural)](guides/data-sources.md) — 단일 조회와 컬렉션 조회 중 어떤 것을 쓸지
8. [리소스 import](guides/import.md) — import key 형식과 리소스별 ID 규칙
9. [문제 해결](guides/troubleshooting.md) — 인증 실패, polling timeout, force-delete, TLS, import 형식 오류 등

이미 IaC에 익숙하다면 1번을 건너뛰고 2번부터 보셔도 됩니다.

## 리소스

각 리소스의 사용 예제와 운영상 주의점을 한국어로 정리했습니다. 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서를 기준으로 합니다.

**프로젝트 & 권한**

- [`cloudia_project`](resources/project.md) — 프로젝트 (admin 권한 필요)

**네트워크**

- [`cloudia_vpc`](resources/vpc.md) — VPC (네트워크 격리 단위)
- [`cloudia_subnet`](resources/subnet.md) — 서브넷 (VPC 내 IP 블록)
- [`cloudia_security_group`](resources/security_group.md) — 보안그룹 + inbound/outbound rule
- [`cloudia_default_security_group`](resources/default_security_group.md) — 기본 보안그룹 adopt 관리
- [`cloudia_floating_ip`](resources/floating_ip.md) — 플로팅 IP 할당 + bind/unbind

**컴퓨트**

- [`cloudia_instance`](resources/instance.md) — 가상머신 인스턴스 (가장 큰 리소스, LIVE/STOP/REPLACE 분기 포함)
- [`cloudia_ssh_key`](resources/ssh_key.md) — SSH 공개키 등록
- [`cloudia_affinity_group`](resources/affinity_group.md) — 인스턴스/호스트 배치 정책 그룹
- [`cloudia_instance_snapshot`](resources/instance_snapshot.md) — 인스턴스 스냅샷 생성
- [`cloudia_instance_snapshot_restore`](resources/instance_snapshot_restore.md) — 스냅샷 복원 (action 스타일, import 불가)

**스토리지**

- [`cloudia_volume`](resources/volume.md) — 블록 볼륨
- [`cloudia_image`](resources/image.md) — OS 이미지(qcow2) 업로드
- [`cloudia_image_clone`](resources/image_clone.md) — 이미지 복제 (스토리지 도메인 간 이동)
- [`cloudia_nfs_file_system`](resources/nfs_file_system.md) — NFS 공유 파일시스템 (multi-attach)
- [`cloudia_virtiofs_file_system`](resources/virtiofs_file_system.md) — VIRTIOFS host-local 공유 파일시스템

## 데이터소스

**프로젝트**

- [`cloudia_project`](data-sources/project.md) / [`cloudia_projects`](data-sources/projects.md) — 프로젝트 단일/컬렉션 조회

**컴퓨트**

- [`cloudia_instance`](data-sources/instance.md) / [`cloudia_instances`](data-sources/instances.md) — 인스턴스 단일/컬렉션
- [`cloudia_instance_type`](data-sources/instance_type.md) / [`cloudia_instance_types`](data-sources/instance_types.md) — 인스턴스 타입 카탈로그
- [`cloudia_instance_disks`](data-sources/instance_disks.md) — 인스턴스에 붙은 디스크 목록
- [`cloudia_instance_interface`](data-sources/instance_interface.md) — 인스턴스 NIC 1개
- [`cloudia_instance_snapshots`](data-sources/instance_snapshots.md) — 인스턴스 스냅샷 목록
- [`cloudia_ssh_key`](data-sources/ssh_key.md) — SSH 키 단일 조회
- [`cloudia_secure_types`](data-sources/secure_types.md) — 보안 등급 카탈로그
- [`cloudia_compute_hosts`](data-sources/compute_hosts.md) — compute host 목록
- [`cloudia_accelerator_gpus`](data-sources/accelerator_gpus.md) / [`cloudia_accelerator_npus`](data-sources/accelerator_npus.md) — GPU/NPU 카탈로그 + 가용량

**스토리지**

- [`cloudia_image`](data-sources/image.md) / [`cloudia_images`](data-sources/images.md) — 이미지 단일/컬렉션
- [`cloudia_file_system`](data-sources/file_system.md) — NFS/VIRTIOFS 공통 단일 조회
- [`cloudia_storage_domains`](data-sources/storage_domains.md) — 사용 가능한 스토리지 도메인

## 관련 자료

- Cloud:iA UI 기반 사용자 가이드: [user-guide/quickstarts](../quickstarts/README.md), [user-guide/examples-and-labs](../examples-and-labs/README.md)
- Cloud:iA 용어집: [glossary](../../glossary/glossary.md)
- 영문 Provider Reference: 추후 Terraform Registry / OpenTofu Registry에 게시 예정
