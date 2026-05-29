# 리소스

Cloud:iA Terraform Provider가 제공하는 16개 리소스입니다. 각 페이지는 한국어 사용 예제와 운영 노트(RequiresReplace 필드, update 동작, 백엔드 제약 등)를 담습니다. 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서를 기준으로 합니다.

## 프로젝트 & 권한

- [`cloudia_project`](project.md) — 프로젝트 (admin 권한 필요)

## 네트워크

- [`cloudia_vpc`](vpc.md) — VPC (네트워크 격리 단위)
- [`cloudia_subnet`](subnet.md) — 서브넷 (VPC 내 IP 블록)
- [`cloudia_security_group`](security_group.md) — 보안그룹 + inbound/outbound rule
- [`cloudia_default_security_group`](default_security_group.md) — 기본 보안그룹 adopt 관리
- [`cloudia_floating_ip`](floating_ip.md) — 플로팅 IP 할당 + bind/unbind

## 컴퓨트

- [`cloudia_instance`](instance.md) — 가상머신 인스턴스 (가장 큰 리소스, LIVE/STOP/REPLACE 분기 포함)
- [`cloudia_ssh_key`](ssh_key.md) — SSH 공개키 등록
- [`cloudia_affinity_group`](affinity_group.md) — 인스턴스/호스트 배치 정책 그룹
- [`cloudia_instance_snapshot`](instance_snapshot.md) — 인스턴스 스냅샷 생성
- [`cloudia_instance_snapshot_restore`](instance_snapshot_restore.md) — 스냅샷 복원 (action 스타일, import 불가)

## 스토리지

- [`cloudia_volume`](volume.md) — 블록 볼륨
- [`cloudia_image`](image.md) — OS 이미지(qcow2) 업로드
- [`cloudia_image_clone`](image_clone.md) — 이미지 복제 (스토리지 도메인 간 이동)
- [`cloudia_nfs_file_system`](nfs_file_system.md) — NFS 공유 파일시스템 (multi-attach)
- [`cloudia_virtiofs_file_system`](virtiofs_file_system.md) — VIRTIOFS host-local 공유 파일시스템

## 함께 보기

- [데이터소스](../data-sources/README.md) — 기존 리소스 조회
- [리소스 import](../guides/import.md) — import key 형식
- [가이드 홈 (개요)](../README.md)
