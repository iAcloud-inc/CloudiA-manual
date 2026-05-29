# 데이터소스

Cloud:iA Terraform Provider가 제공하는 18개 데이터소스입니다. 기존 리소스나 카탈로그 정보를 조회해 HCL에서 참조할 때 사용합니다. 단일 조회(singular)와 컬렉션 조회(plural) 중 무엇을 쓸지는 [데이터소스 선택 가이드](../guides/data-sources.md)를 참고하세요.

## 프로젝트

- [`cloudia_project`](project.md) / [`cloudia_projects`](projects.md) — 프로젝트 단일/컬렉션 조회

## 컴퓨트

- [`cloudia_instance`](instance.md) / [`cloudia_instances`](instances.md) — 인스턴스 단일/컬렉션
- [`cloudia_instance_type`](instance_type.md) / [`cloudia_instance_types`](instance_types.md) — 인스턴스 타입 카탈로그
- [`cloudia_instance_disks`](instance_disks.md) — 인스턴스에 붙은 디스크 목록
- [`cloudia_instance_interface`](instance_interface.md) — 인스턴스 NIC 1개
- [`cloudia_instance_snapshots`](instance_snapshots.md) — 인스턴스 스냅샷 목록
- [`cloudia_ssh_key`](ssh_key.md) — SSH 키 단일 조회
- [`cloudia_secure_types`](secure_types.md) — 보안 등급 카탈로그
- [`cloudia_compute_hosts`](compute_hosts.md) — compute host 목록
- [`cloudia_accelerator_gpus`](accelerator_gpus.md) / [`cloudia_accelerator_npus`](accelerator_npus.md) — GPU/NPU 카탈로그 + 가용량

## 스토리지

- [`cloudia_image`](image.md) / [`cloudia_images`](images.md) — 이미지 단일/컬렉션
- [`cloudia_file_system`](file_system.md) — NFS/VIRTIOFS 공통 단일 조회
- [`cloudia_storage_domains`](storage_domains.md) — 사용 가능한 스토리지 도메인

## 함께 보기

- [리소스](../resources/README.md) — 리소스 생성·관리
- [데이터소스 선택 (Singular vs Plural)](../guides/data-sources.md)
- [가이드 홈 (개요)](../README.md)
