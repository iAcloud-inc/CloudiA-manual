# Cloud:iA 매뉴얼

# Cloud:iA 소개

Cloud:iA는 조직이 자체 데이터센터 내에 프라이빗 클라우드 환경을 구축할 수 있도록 하는 엔터프라이즈급 IaaS 솔루션입니다. Linux 커널 기반 가상화 기술과 오픈 표준을 활용하여 AI 컴퓨팅을 포함한 다양한 워크로드를 최적화하며, 효율적인 AI 서비스 배포를 위한 GPU/NPU 가상화를 제공합니다.

## 주요 기능
- 소프트웨어 정의 네트워킹(SDN): 고급 SDN 기술로 네트워크 유연성과 자동화를 향상합니다.
- 고성능 스토리지: 까다로운 워크로드를 처리할 수 있는 효율적이고 확장 가능한 스토리지 솔루션을 제공합니다.
- AI 워크로드 최적화: 인공지능·머신러닝 워크로드에 최적화된 환경을 제공합니다.
- GPU/NPU 가상화: 하드웨어 가속 컴퓨팅을 통해 효율적인 AI 서비스 배포를 지원합니다.

이러한 기능을 통합해 Cloud:iA는 고성능과 높은 신뢰성을 갖춘 엔터프라이즈용 IaaS 플랫폼을 제공하여 조직의 클라우드 인프라 관리를 효율화합니다.

## 관리자 가이드

- **대시보드**
  - [전체 대시보드](docs/administrator/dashboard/total-dashboard/total-dashboard.md)
  - [컴퓨트 대시보드](docs/administrator/dashboard/compute-dashboard/compute-dashboard.md)
- **물리머신**
  - [노드](docs/administrator/host-machine/machine/machine.md)
  - [노드 그룹](docs/administrator/host-machine/machine-group/machine-group.md)
- **네트워크**
  - [방화벽](docs/administrator/network/firewall/firewall.md)
  - [보안그룹 템플릿](docs/administrator/network/security-group/security-group)
- **프로젝트**
  - [프로젝트 관리](docs/administrator/project/project-management/project-management.md)
  - [공용 이미지 관리](docs/administrator/project/image/image.md)
- **접근관리**
  - [멤버](docs/administrator/access-management/member/member.md)
  - [역할](docs/administrator/access-management/role/role.md)
  - [권한](docs/administrator/access-management/permission/permission.md)
  - [세션](docs/administrator/access-management/session/session.md)
- **모니터링**
  - [이벤트](docs/administrator/monitoring/event/event.md)
  - [감사 로그](docs/administrator/monitoring/audit-log/audit-log.md)
  - [이벤트 트리거](docs/administrator/monitoring/event-trigger/event-trigger.md)

- **환경설정**
  - [정책 설정](docs/administrator/setting/policy-setting/policy-setting.md)
  - [알람 설정](docs/administrator/setting/alarm-setting/alarm-setting.md)
  - [사용자 연동](docs/administrator/setting/ldap/ldap.md)

---

## 사용자 가이드
- [프로젝트 관리](docs/project/project-management/project-management.md)
- [프로젝트 홈](docs/project/project-home/project-home.md)
- **가상머신**
  - [인스턴스](docs/project/vm/instance/instance.md)
  - [시작 템플릿](docs/project/vm/launch-template/launch-template.md)
  - [오토 스케일링 그룹](docs/project/vm/auto-scaling/auto-scaling.md)
  - [선호도 그룹](docs/project/vm/affinity-group/affinity-group.md)
  - [SSH 키](docs/project/vm/ssh-key/ssh-key.md)
- **네트워크**
  - [VPC](docs/project/network/vpc/vpc.md)
  - [서브넷](docs/project/network/subnet/subnet.md)
  - [외부 IP](docs/project/network/public-ip/public-ip.md)
  - [플로팅 IP](docs/project/network/floating-ip/floating-ip.md)
  - [포트 포워딩](docs/project/network/port-forwarding/port-forwarding.md)
  - [로드 밸런서](docs/project/network/load-balancer/load-balancer.md)
  - [타겟 그룹](docs/project/network/target-group/target-group.md)
- **네트워크 보안**
  - [네트워크 접근 제어](docs/project/security/nacl/nacl.md)
  - [보안그룹](docs/project/security/security-group/security-group.md)
- **스토리지**
  - [이미지](docs/project/storage/image/image.md)
  - [블록](docs/project/storage/block/block.md)
  - [파일 시스템](docs/project/storage/file-system/file-system.md)
  - [스냅샷](docs/project/storage/snapshot/snapshot.md)
- **쿠버네티스**
  - [클러스터](docs/project/kubernetes/cluster/cluster.md)
- **모니터링**
  - [이벤트](docs/project/monitoring/event/event.md)
