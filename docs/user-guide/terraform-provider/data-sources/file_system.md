# cloudia_file_system (데이터소스)

NFS와 VIRTIOFS를 포함한 공유 파일시스템 한 개를 조회합니다. `lookup_id`로 ID 직접 조회하거나, `name`과 `type`을 함께 지정해 이름 검색을 할 수 있습니다. 이름 검색 시 `type`이 필수인 이유는 NFS와 VIRTIOFS가 같은 프로젝트 네임스페이스를 공유하기 때문입니다.

## 예제

```hcl
# ID로 조회
data "cloudia_file_system" "by_id" {
  lookup_id = cloudia_nfs_file_system.shared.id
}

output "fs_kind" {
  value = data.cloudia_file_system.by_id.type   # "NFS" 또는 "VIRTIOFS"
}

# 이름 + 타입으로 조회
data "cloudia_file_system" "shared_nfs" {
  name = "shared-nfs"
  type = "NFS"
}

output "nfs_path" {
  value = data.cloudia_file_system.shared_nfs.path
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `lookup_id` | 선택 (ExactlyOneOf) | 조회할 파일시스템 ID. `name`과 둘 중 하나만 지정. |
| `name` | 선택 (ExactlyOneOf) | 조회할 파일시스템 이름. `type`과 함께 지정해야 타입 간 중복을 구분. |
| `project_id` | 선택 | 프로젝트 ID. 생략 시 provider 설정값 사용. |
| `type` | 선택 | 파일시스템 타입 (`NFS` 또는 `VIRTIOFS`). `name` 검색 시 필수. 성공적으로 조회된 후 state에 항상 기록됨. |

## 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 조회된 파일시스템 ID. |
| `created_at` | String | 생성 시각. |
| `deletable` | Boolean | 현재 삭제 가능 여부 (마운트 중이면 `false`). |
| `deleted` | Boolean | 소프트 삭제 여부. |
| `instance_count` | Number | 현재 이 파일시스템을 마운트 중인 인스턴스 수. |
| `network_id` | String | NFS 서버 VM이 위치한 VPC ID. VIRTIOFS는 null. |
| `network_name` | String | 네트워크 이름. VIRTIOFS는 null. |
| `path` | String | 백엔드가 보고하는 파일시스템 경로 (VIRTIOFS 호스트 디렉터리 / NFS 내보내기 경로). |
| `security_group_ids` | Set(String) | NFS 서버 VM 기본 NIC에 적용된 보안그룹 ID 세트. VIRTIOFS는 빈 세트. |
| `size_gib` | Number | 파일시스템 크기 (GiB). NFS만 값이 있음; VIRTIOFS는 null. |
| `size_mib` | Number | 백엔드가 보고하는 원시 크기 (MiB). NFS만 값이 있음. |
| `storage_domain_id` | String | 파일시스템을 backing하는 스토리지 도메인 ID. |
| `storage_domain_name` | String | 스토리지 도메인 이름. |
| `storage_domain_type` | String | 스토리지 도메인 타입 (`LOCAL`, `GFS2`, `NFS`, `CEPH`). |
| `subnet_id` | String | NFS 서버 VM 기본 NIC의 서브넷 ID. VIRTIOFS는 null. |
| `subnet_name` | String | 기본 NIC 서브넷 이름. VIRTIOFS는 null. |
| `updated_at` | String | 마지막 수정 시각. |

## 관련 항목

- [../resources/nfs_file_system.md](../resources/nfs_file_system.md) — NFS 파일시스템 리소스
- [../resources/virtiofs_file_system.md](../resources/virtiofs_file_system.md) — VIRTIOFS 파일시스템 리소스
- [storage_domains.md](storage_domains.md) — 스토리지 도메인 목록 조회
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/file_system.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
