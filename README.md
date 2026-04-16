# Cloud:iA 매뉴얼

# Cloud:iA 소개

Cloud:iA는 조직이 자체 데이터센터 내에 프라이빗 클라우드 환경을 구축할 수 있도록 하는 엔터프라이즈급 IaaS 솔루션입니다. Linux 커널 기반 가상화 기술과 오픈 표준을 활용하여 AI 컴퓨팅을 포함한 다양한 워크로드를 최적화하며, 효율적인 AI 서비스 배포를 위한 GPU/NPU 가상화를 제공합니다.

## 주요 기능
- 소프트웨어 정의 네트워킹(SDN): 고급 SDN 기술로 네트워크 유연성과 자동화를 향상합니다.
- 고성능 스토리지: 까다로운 워크로드를 처리할 수 있는 효율적이고 확장 가능한 스토리지 솔루션을 제공합니다.
- AI 워크로드 최적화: 인공지능·머신러닝 워크로드에 최적화된 환경을 제공합니다.
- GPU/NPU 가상화: 하드웨어 가속 컴퓨팅을 통해 효율적인 AI 서비스 배포를 지원합니다.

이러한 기능을 통합해 Cloud:iA는 고성능과 높은 신뢰성을 갖춘 엔터프라이즈용 IaaS 플랫폼을 제공하여 조직의 클라우드 인프라 관리를 효율화합니다.

## 관리자 매뉴얼

- **대시보드**
  - [전체 대시보드](docs/administrator/dashboard/total-dashboard/total-dashboard.md)
  - [컴퓨트 대시보드](docs/administrator/dashboard/compute-dashboard/compute-dashboard.md)
- **물리머신**
  - [노드](docs/administrator/host-machine/machine/machine.md)
  - [노드 그룹](docs/administrator/host-machine/machine-group/machine-group.md)
  - [컴퓨트 노드](docs/administrator/host-machine/compute-node/compute-node.md)
- **네트워크**
  - [외부 IP 풀](docs/administrator/network/ip-pool/ip-pool.md)
  - [방화벽](docs/administrator/network/firewall/firewall.md)
  - [보안그룹 템플릿](docs/administrator/network/security-group-template/security-group-template.md)
- **스토리지**
  - [스토리지 도메인](docs/administrator/storage/storage-domain/storage-domain.md)
  - [공용 이미지 관리](docs/administrator/storage/public-image/public-image.md)
  - [ISO](docs/administrator/storage/iso/iso.md)
- **프로젝트**
  - [프로젝트 관리](docs/administrator/project/project-management/project-management.md)
- **접근관리**
  - [멤버](docs/administrator/access-management/member/member.md)
  - [역할](docs/administrator/access-management/role/role.md)
  - [관리자 역할](docs/administrator/access-management/admin-role/admin-role.md)
  - [권한](docs/administrator/access-management/permission/permission.md)
  - [세션](docs/administrator/access-management/session/session.md)
- **모니터링**
  - [이벤트](docs/administrator/monitoring/event/event.md)
  - [감사 로그](docs/administrator/monitoring/audit-log/audit-log.md)
  - [이벤트 트리거](docs/administrator/monitoring/event-trigger/event-trigger.md)
- **환경설정**
  - [정책 설정](docs/administrator/setting/policy-setting/policy-setting.md)
  - [알림 설정](docs/administrator/setting/alarm-setting/alarm-setting.md)
  - [사용자 연동](docs/administrator/setting/ldap/ldap.md)

---

## 프로젝트 매뉴얼
- [프로젝트 관리](docs/project/project-management/project-management.md)
- [프로젝트 홈](docs/project/project-home/project-home.md)
- [네트워크 토폴로지](docs/project/project-home/network-topology/network-topology.md)
- **가상머신**
  - [인스턴스](docs/project/vm/instance/instance.md)
  - [시작 템플릿](docs/project/vm/launch-template/launch-template.md)
  - [오토 스케일링 그룹](docs/project/vm/auto-scaling/auto-scaling.md)
  - [선호도 그룹](docs/project/vm/affinity-group/affinity-group.md)
  - [SSH 키](docs/project/vm/ssh-key/ssh-key.md)
- **네트워크**
  - [VPC](docs/project/network/vpc/vpc.md)
  - [서브넷](docs/project/network/subnet/subnet.md)
  - [외부 IP](docs/project/network/external-ip/external-ip)
  - [플로팅 IP](docs/project/network/floating-ip/floating-ip.md)
  - [포트 포워딩](docs/project/network/port-forwarding/port-forwarding.md)
  - [로드 밸런서](docs/project/network/load-balancer/load-balancer.md)
  - [타겟 그룹](docs/project/network/target-group/target-group.md)
  - [내부 DNS](docs/project/network/private-dns/private-dns.md)
- **네트워크 보안**
  - [네트워크 ACL](docs/project/security/nacl/nacl.md)
  - [보안그룹](docs/project/security/security-group/security-group.md)
- **스토리지**
  - [이미지](docs/project/storage/image/image.md)
  - [블록](docs/project/storage/block/block.md)
  - [파일 시스템](docs/project/storage/file-system/file-system.md)
  - [스냅샷](docs/project/storage/snapshot/snapshot.md)
- **쿠버네티스**
  - [클러스터](docs/project/kubernetes/cluster/cluster.md)
- **스케줄러**
  - [일정](docs/project/scheduler/schedule/schedule.md)
- **모니터링**
  - [이벤트](docs/project/monitoring/event/event.md)

---

## 사용자 가이드
- **빠른 시작 가이드**
  - [빠른 시작 가이드 홈](docs/user-guide/quickstarts/README.md)
  - [Cloud:iA 계정 생성하기](docs/user-guide/quickstarts/01-create-account.md)
  - [프로젝트 생성하기](docs/user-guide/quickstarts/02-create-project.md)
  - [가상 네트워크 생성과 Linux 인스턴스 생성하기](docs/user-guide/quickstarts/03-create-network-and-linux-instance.md)
  - [플로팅 IP로 인스턴스 접속하기](docs/user-guide/quickstarts/04-access-instance-via-floating-ip.md)
  - [블록 생성과 인스턴스 연결하기](docs/user-guide/quickstarts/05-create-block-and-add-to-new-instance.md)
  - [쿠버네티스 클러스터 구성하기](docs/user-guide/quickstarts/06-configure-kubernetes-cluster.md)

- **예제 및 실습 가이드**
  - [예제 및 실습 가이드 홈](docs/user-guide/examples-and-labs/README.md)
  - [역할 만들기 및 권한 부여](docs/user-guide/examples-and-labs/01-create-role-and-assign-permissions.md)
  - [알림 설정 및 이벤트 트리거](docs/user-guide/examples-and-labs/02-configure-alert-and-event-trigger.md)
  - [인스턴스 마이그레이션하기 (콜드, 라이브 둘의 차이점 설명 포함)](docs/user-guide/examples-and-labs/03-migrate-instance-cold-and-live.md)
  - [윈도우 가상머신 ISO 생성 및 콘솔 확인](docs/user-guide/examples-and-labs/04-create-windows-instance-from-iso-and-open-console.md)
  - [시작 템플릿을 통한 빠른 인스턴스 구성하기](docs/user-guide/examples-and-labs/05-provision-instance-from-launch-template.md)
  - [선호도 그룹을 통한 가상머신 배치하기](docs/user-guide/examples-and-labs/06-place-instances-with-affinity-group.md)
  - [SSH 키를 사용한 인스턴스 접속하기](docs/user-guide/examples-and-labs/07-access-instance-with-ssh-key.md)
  - [오토 스케일링 그룹을 통한 인스턴스 관리하기](docs/user-guide/examples-and-labs/08-manage-instances-with-auto-scaling-group.md)
  - [로드 밸런서를 활용한 트래픽 분산하기](docs/user-guide/examples-and-labs/09-distribute-traffic-with-load-balancer.md)
  - [포트 포워딩으로 인스턴스 연결하기](docs/user-guide/examples-and-labs/10-connect-instance-via-port-forwarding.md)
  - [내부 DNS 활용하기](docs/user-guide/examples-and-labs/11-use-private-dns-and-verify-with-dig.md)
  - [네트워크 접근 제어 커스터마이징하기](docs/user-guide/examples-and-labs/12-customize-nacl-and-bind-subnet.md)
  - [보안그룹을 통한 인스턴스 통신 정책 만들기](docs/user-guide/examples-and-labs/13-create-security-group-traffic-policy.md)
  - [스케줄러를 통한 주기적인 인스턴스 스냅샷 생성](docs/user-guide/examples-and-labs/14-schedule-recurring-instance-snapshots.md)
  - [인스턴스 스냅샷 롤백하기](docs/user-guide/examples-and-labs/15-rollback-instance-to-snapshot.md)
  - [스냅샷 이미지 생성으로 골든 이미지 만들기 및 인스턴스 실행](docs/user-guide/examples-and-labs/16-create-golden-image-from-snapshot.md)
  - [파일 시스템을 통한 인스턴스 간 공유 볼륨 구성하기](docs/user-guide/examples-and-labs/17-share-volumes-between-instances-with-nfs.md)
  - [쿠버네티스 스토리지 클래스 추가하기 & PVC 만들기](docs/user-guide/examples-and-labs/18-add-kubernetes-storage-class-and-pvc.md)
