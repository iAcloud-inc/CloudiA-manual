# 리소스 / 데이터소스 카탈로그 (한국어)

Cloud:iA Terraform provider가 제공하는 모든 리소스와 데이터소스를 카테고리별로 정리한 한국어 가이드입니다.

> **이 문서의 성격**: 한국어 사용 가이드(개념·예제·자주 만나는 함정 중심)입니다. 전체 schema 레퍼런스(필드 타입, 모든 옵션, 자동 생성된 표)는 영문 docs에 있고 본 문서에서는 사용 예제와 운영 팁만 다룹니다.
>
> 영문 SSOT: provider 저장소 `docs/resources/*.md` 및 `docs/data-sources/*.md`. Registry 게시 후에는 `https://registry.terraform.io/providers/iacloud/cloudia/latest/docs` 에서도 조회 가능.

## 카테고리

| 카테고리 | 다루는 리소스/데이터소스 | 페이지 |
|---|---|---|
| **프로젝트 & 권한** | `cloudia_project` 등 | [project.md](project.md) |
| **네트워크** | `cloudia_vpc`, `cloudia_subnet`, `cloudia_security_group`, `cloudia_default_security_group` | [network.md](network.md) |
| **컴퓨트** | `cloudia_instance`, `cloudia_ssh_key`, `cloudia_affinity_group`, `cloudia_instance_snapshot`, `cloudia_instance_snapshot_restore` + 7 data sources | [compute.md](compute.md) |
| **스토리지** | `cloudia_volume`, `cloudia_image`, `cloudia_image_clone`, `cloudia_nfs_file_system`, `cloudia_virtiofs_file_system` + 4 data sources | [storage.md](storage.md) |

## 빠른 인덱스 — 알파벳순

### 리소스 (15개)

| 이름 | 카테고리 | 한 줄 설명 |
|---|---|---|
| [`cloudia_affinity_group`](compute.md#affinity-group) | 컴퓨트 | 인스턴스/호스트 배치 정책 그룹 |
| [`cloudia_default_security_group`](network.md#default-security-group) | 네트워크 | VPC 생성 시 자동 만들어지는 기본 SG의 어댑트 관리 |
| [`cloudia_image`](storage.md#image) | 스토리지 | OS 이미지(qcow2) 업로드 |
| [`cloudia_image_clone`](storage.md#image-clone) | 스토리지 | 이미지 복제 (LOCAL → CEPH 등 SD 간 이동) |
| [`cloudia_instance`](compute.md#instance) | 컴퓨트 | 가상머신 인스턴스 (가장 큰 리소스) |
| [`cloudia_instance_snapshot`](compute.md#instance-snapshot) | 컴퓨트 | 인스턴스 스냅샷 생성 |
| [`cloudia_instance_snapshot_restore`](compute.md#instance-snapshot-restore) | 컴퓨트 | 스냅샷 복원 (action 스타일, import 불가) |
| [`cloudia_nfs_file_system`](storage.md#nfs-file-system) | 스토리지 | NFS 공유 파일시스템 (multi-attach) |
| [`cloudia_project`](project.md#project) | 프로젝트 | 프로젝트 (admin 권한 필요) |
| [`cloudia_security_group`](network.md#security-group) | 네트워크 | 보안그룹 + inbound/outbound rule |
| [`cloudia_ssh_key`](compute.md#ssh-key) | 컴퓨트 | SSH 공개키 등록 |
| [`cloudia_subnet`](network.md#subnet) | 네트워크 | 서브넷 (VPC 내 IP 블록) |
| [`cloudia_virtiofs_file_system`](storage.md#virtiofs-file-system) | 스토리지 | VIRTIOFS host-local 공유 파일시스템 |
| [`cloudia_volume`](storage.md#volume) | 스토리지 | 블록 볼륨 (인스턴스에 attach) |
| [`cloudia_vpc`](network.md#vpc) | 네트워크 | VPC (네트워크 격리 단위) |

### 데이터소스 (15개)

| 이름 | 카테고리 | 한 줄 설명 |
|---|---|---|
| [`cloudia_file_system`](storage.md#ds-file-system) | 스토리지 | NFS/VIRTIOFS 공통 단일 조회 |
| [`cloudia_image`](storage.md#ds-image) | 스토리지 | 이미지 단일 조회 (이름/ID) |
| [`cloudia_images`](storage.md#ds-images) | 스토리지 | 이미지 컬렉션 (필터) |
| [`cloudia_instance`](compute.md#ds-instance) | 컴퓨트 | 인스턴스 단일 조회 |
| [`cloudia_instance_disks`](compute.md#ds-instance-disks) | 컴퓨트 | 인스턴스에 붙은 모든 디스크 |
| [`cloudia_instance_interface`](compute.md#ds-instance-interface) | 컴퓨트 | 인스턴스 NIC 1개 (selector singular) |
| [`cloudia_instance_snapshots`](compute.md#ds-instance-snapshots) | 컴퓨트 | 인스턴스 스냅샷 컬렉션 |
| [`cloudia_instance_type`](compute.md#ds-instance-type) | 컴퓨트 | 인스턴스 타입 카탈로그 단일 조회 |
| [`cloudia_instance_types`](compute.md#ds-instance-types) | 컴퓨트 | 인스턴스 타입 컬렉션 (GPU/NPU 필터) |
| [`cloudia_instances`](compute.md#ds-instances) | 컴퓨트 | 인스턴스 컬렉션 (name_prefix/power_state 필터) |
| [`cloudia_project`](project.md#ds-project) | 프로젝트 | 프로젝트 단일 조회 |
| [`cloudia_projects`](project.md#ds-projects) | 프로젝트 | 프로젝트 컬렉션 |
| [`cloudia_secure_types`](compute.md#ds-secure-types) | 컴퓨트 | 인스턴스 보안 등급 카탈로그 |
| [`cloudia_ssh_key`](compute.md#ds-ssh-key) | 컴퓨트 | SSH 키 단일 조회 |
| [`cloudia_storage_domains`](storage.md#ds-storage-domains) | 스토리지 | 사용 가능한 스토리지 도메인 |

## 공통 사항

- **`project_id`**: 모든 project-scoped 리소스는 `project_id`가 필요합니다. provider 블록의 `project_id` 또는 `CLOUDIA_PROJECT_ID` 환경 변수로 기본값을 주거나, 각 리소스에서 명시할 수 있습니다.
- **비동기 작업**: 대부분의 쓰기 작업은 백엔드가 비동기로 처리합니다. provider가 polling을 대신 해주므로 사용자는 동기처럼 사용 가능. timeout은 `CLOUDIA_POLL_TIMEOUT_SECONDS` (기본 600초).
- **Import 형식**: project-scoped 리소스는 슬래시 구분 import key를 씁니다 — `<project_id>/<resource_id>` 또는 `<project_id>/<parent_id>/<resource_id>`. 각 리소스 페이지 §Import 참고.
- **민감 정보**: 인증 정보를 HCL에 평문으로 적지 마세요. 환경 변수 또는 secret manager 사용.
