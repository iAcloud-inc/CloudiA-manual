# 가이드

Cloud:iA Terraform Provider를 사용하기 위한 개념·설치·설정·운영 가이드 모음입니다. IaC가 처음이라면 아래 순서대로 읽는 것을 권장합니다.

1. [개념 정리 (IaC 입문)](concepts.md) — Terraform/OpenTofu/HCL/Provider/State 같은 용어 정리
2. [설치하기](installation.md) — provider 로컬 빌드 + `dev_overrides` 설정
3. [Provider 설정](configuration.md) — `provider "cloudia"` 블록, endpoint·api_base_path, admin/user alias, 환경 변수, TLS, 고급 설정
4. [인증](authentication.md) — `auth { ... }` 블록, password vs client_credentials, 환경 변수, CI/CD 연동
5. [시작하기](getting-started.md) — VPC → subnet → security group → image → SSH key → instance 최소 흐름
6. [자주 쓰는 워크플로](common-workflows.md) — 멀티 NIC, 데이터 볼륨, 스냅샷/롤백, 플로팅 IP, NFS 공유, 골든 이미지
7. [데이터소스 선택 (Singular vs Plural)](data-sources.md) — 단일 조회와 컬렉션 조회 중 어떤 것을 쓸지
8. [리소스 import](import.md) — import key 형식과 리소스별 ID 규칙
9. [문제 해결](troubleshooting.md) — 인증 실패, polling timeout, TLS, import 형식 오류 등

이미 IaC에 익숙하다면 1번을 건너뛰고 2번부터 보셔도 됩니다.

## 함께 보기

- [리소스](../resources/README.md) — 16개 리소스의 사용 예제와 운영 노트
- [데이터소스](../data-sources/README.md) — 18개 데이터소스의 조회 예제
- [가이드 홈 (개요)](../README.md)
