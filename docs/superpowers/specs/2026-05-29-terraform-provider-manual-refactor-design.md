# Cloud:iA Terraform Provider 한국어 매뉴얼 리팩토링 & 보강 — 설계 문서

- 작성일: 2026-05-29
- 대상 경로: `docs/user-guide/terraform-provider/`
- 성격: 기존 부분 가이드의 **적극적 리팩토링 + 내용 보강**
- 구조 레퍼런스: 외부 메이저 Terraform 프로바이더(AWS / Google / Azure) Registry 문서 구조
- 콘텐츠 SSOT: provider 레포(`terraform-provider-cloudia`) `docs/`·`examples/`, e2e 레포(`cloudia-provider-e2e`) `docs/scenarios.md`

---

## 1. 목적

`terraform-provider-cloudia`를 OpenTofu/Terraform로 사용하는 한국어 사용자(운영자·개발자)를 위한 사용자 가이드를, 메이저 프로바이더 Registry 문서와 동일한 **"1 리소스 = 1 페이지"** 구조로 재편하고, e2e 시나리오로 이미 검증된 깊은 운영 콘텐츠(instance LIVE/STOP/REPLACE 분기, GPU/NPU, import 절차)를 한국어로 채운다.

본 매뉴얼은 한국어 **사용 가이드**다. 전체 schema 레퍼런스(모든 필드/타입/자동생성 표)의 SSOT는 영문 generated docs(provider `docs/resources/*`, `docs/data-sources/*`, 추후 Registry)이며, 본 매뉴얼은 **큐레이션된 주요 인자 + 예제 + 운영상 주의점 + import**를 담당한다.

## 2. 현황 진단 (Before)

```
docs/user-guide/terraform-provider/
  README.md            (67줄)   Overview + 플레이스홀더 reference 표
  concepts.md          (152줄)  IaC 입문
  install.md           (321줄)  로컬 빌드 + dev_overrides
  authentication.md    (174줄)  auth 블록
  getting-started.md    (299줄)  최소 흐름
  data-sources.md      (182줄)  singular vs plural
  troubleshooting.md   (156줄)
  catalog/
    README.md          (69줄)   리소스 16 + 데이터소스 18 인덱스
    project.md         (78줄)
    network.md         (195줄)  vpc/subnet/security_group/default_sg/floating_ip
    compute.md         (385줄)  instance + ssh_key + affinity + snapshot×2 + DS 10
    storage.md         (195줄)  volume/image/image_clone/nfs/virtiofs + DS 4
```

진단된 문제:

1. **구조** — 리소스 34종이 4개 카테고리 묶음 파일에 혼재. 메이저 프로바이더의 "1 리소스 = 1 페이지 + 좌측 네비 그룹핑"과 어긋남. 단일 리소스 검색·딥링크·확장이 어렵다.
2. **누락 가이드** — provider 레포가 이미 가진 `import`, `configuration`, `common-workflows` 가이드가 한국어 매뉴얼엔 없음.
3. **깊은 운영 콘텐츠 미작성** — `instance`의 LIVE/STOP/REPLACE update 분기, GPU/NPU 설정이 "추후 작성 예정"으로 stub. e2e `scenarios.md`에 instance matrix(12) + update lifecycle(11) + negative validation(12)로 이미 검증되어 있어 한국어화 가능.
4. **반복 보일러플레이트** — "전체 schema (모든 옵션): … provider generated reference를 참고하세요." 문구가 모든 리소스마다 반복. 공통 안내 1곳으로 이동.
5. **Guides 평면 배치** — 가이드 6종이 섹션 루트에 평면 배치. 메이저 프로바이더는 Guides를 별도 네비 그룹으로 둠.

## 3. 목표 구조 (After) — 풀 레지스트리 미러

```
docs/user-guide/terraform-provider/
  README.md                      # Overview (provider index). 플레이스홀더 표 유지, 네비 안내 갱신
  guides/
    concepts.md                  # IaC 입문 (한국어 특화, 유지)
    installation.md              # (install.md → 개명) 로컬 빌드 + dev_overrides
    configuration.md             # NEW — provider 블록: endpoint, api_base_path, alias(admin/user), 환경변수, poll timeout, TLS/CA
    authentication.md            # auth 블록: password vs client_credentials, secret 주입, CI/CD
    getting-started.md           # VPC→subnet→SG→image→ssh_key→instance 최소 흐름
    common-workflows.md          # NEW — 엔드투엔드 워크플로 (멀티 NIC, 데이터 볼륨, 스냅샷/롤백, 골든이미지, NFS 공유 등 e2e core 시나리오 기반)
    import.md                    # NEW — import key 형식 규칙(<project_id>/<id>, parent 포함), 리소스별 표, import 불가 리소스
    data-sources.md              # singular vs plural 선택 가이드
    troubleshooting.md           # 인증/polling/force-delete/TLS/import 오류
  resources/                     # 16 페이지 (1 리소스 = 1 페이지)
    project.md
    vpc.md
    subnet.md
    security_group.md
    default_security_group.md
    floating_ip.md
    instance.md                  # DEEP — 별도 §4 참조
    ssh_key.md
    affinity_group.md
    instance_snapshot.md
    instance_snapshot_restore.md
    volume.md
    image.md
    image_clone.md
    nfs_file_system.md
    virtiofs_file_system.md
  data-sources/                  # 18 페이지 (1 데이터소스 = 1 페이지)
    project.md / projects.md
    instance.md / instances.md
    instance_type.md / instance_types.md
    instance_disks.md / instance_interface.md / instance_snapshots.md
    image.md / images.md
    ssh_key.md
    secure_types.md
    storage_domains.md
    compute_hosts.md
    accelerator_gpus.md / accelerator_npus.md
    file_system.md
```

- 기존 `catalog/` 디렉터리는 제거되고 내용은 `resources/`·`data-sources/`로 분해·이관된다.
- 기존 `install.md`/평면 가이드들은 `guides/`로 이동(개명 포함). 외부 유입 링크는 없으나(내부 매뉴얼) SUMMARY.md·README.md·상호 참조 링크를 일괄 갱신한다.

### 페이지 표준 템플릿 (리소스)

각 `resources/<name>.md`는 다음 섹션을 가진다(섹션은 복잡도에 맞춰 신축):

```
# cloudia_<name>

<한 줄 설명 + 무엇을 위한 리소스인가>

## 예제 (Example Usage)
### 최소 예제
### (필요 시) 변형 예제

## 주요 인자 (Arguments)
| 인자 | 설명 | 필수 | 비고 |
  — 큐레이션된 핵심 인자만. 전체는 영문 generated reference 링크.

## 주요 속성 (Attributes)   # id 등 참조에 쓰이는 export 값

## 운영 노트 (Operational Notes)
  — RequiresReplace 필드, update 분기, 백엔드 제약, ADR 근거

## Import
  — import 명령 + key 형식 (또는 import 불가 명시)

## 관련 항목
  — 연관 리소스/데이터소스/가이드 링크
```

데이터소스 페이지는 `## 예제` / `## 인자(필터)` / `## 속성` / `## 관련 항목`으로 축약.

## 4. instance.md 딥다이브 (핵심 산출물)

`cloudia_instance`는 가장 큰 리소스이며 별도 심화 페이지로 작성한다. e2e `scenarios.md`를 한국어 운영 가이드로 변환:

- **Sizing** — 직접 입력(`vcpu_number`+`memory_total`) vs 카탈로그 미러(`cloudia_instance_type`). `max_vcpu`/`max_memory` headroom. `hyperthreading_enabled`와 vcpu 짝수 제약(ADR-0010/0011).
- **Update 분기 표 (LIVE / STOP / REPLACE)** — `resource_cloudia_instance.go` update branch와 1:1. 어떤 필드 변경이 무중단/자동 stop-update-run(다운타임)/재생성인지 표로 명시. e2e update lifecycle 11 시나리오가 근거.
  - LIVE: `data_volume_ids` swap, `vnic[*].security_group_ids`
  - STOP: `memory_total`↓, `vcpu`↓, `max_vcpu/max_memory`, `hyperthreading_enabled`, `cloud_init.username`
  - REPLACE: `network_id`, `secure_type`, `vnic[*].subnet_id`, `vnic[*].ipv4_address`, `boot_block_device_size_gib`, `image_id`
- **vNIC** — single/multi NIC, default NIC, fixed IPv4.
- **인증** — password only / ssh_key only / 둘 다 / cloud-init 인증 필수 규칙.
- **cloud-init scripts** — PER_ONCE / PER_INSTANCE / PER_BOOT.
- **secure_type** — `cloudia_secure_types`로 후보 조회, NONE→SEV 전환은 REPLACE이며 호스트 미지원 시 실패.
- **GPU/NPU** — `hardware_gpu`/`hardware_npu` XOR 제약, `cloudia_accelerator_gpus/npus`로 (vendor_id, product_id) 조회.
- **Negative/plan-time 검증** — 자주 만나는 plan 거부 메시지와 원인(vcpu 홀수+HT, gpu+npu 동시, cloud_init 인증 누락 등).

## 5. 콘텐츠 소싱 매핑

| 산출 페이지 | 1차 소스 |
|---|---|
| resources/* | provider `docs/resources/<name>.md`(schema SSOT) + `examples/resources/cloudia_<name>/*.tf`·`import.sh` |
| data-sources/* | provider `examples/data-sources/cloudia_<name>/data-source.tf` + `docs/data-sources/*` |
| instance.md 딥다이브 | e2e `docs/scenarios.md`(matrix/lifecycle/negative) + 관련 ADR(0008/0010/0011/0013/0018 등) |
| guides/import.md | 각 `examples/.../import.sh` + 공통 import key 규칙 |
| guides/configuration.md, authentication.md | provider `docs/guides/configuration|authentication`, `README.ko.md` provider 블록 예시 |
| guides/common-workflows.md | e2e core 시나리오 + 기존 examples-and-labs |

## 6. 컨벤션 (docs_guide.md 준수)

- 존댓말, 짧고 명확한 문장. UI 라벨/명령은 굵게 또는 코드.
- H1 1회, 헤딩 단계 건너뛰기 금지.
- 링크는 상대 경로. 리팩토링으로 깨질 모든 내부 링크(SUMMARY.md, README.md, FAQ, 예제/실습 상호 참조) 갱신.
- 플레이스홀더 `<your-...>` 규칙 + 민감정보 평문 금지 원칙 유지(README 표가 SSOT).
- "전체 schema는 영문 generated reference" 안내는 `resources/README` 또는 섹션 공통 1곳으로 집약, 페이지별 반복 제거.

## 7. SUMMARY.md (GitBook 네비) 재편

`terraform-provider` 블록을 Overview → Guides → Resources → Data Sources 4그룹으로 재작성. Resources/Data Sources는 알파벳 또는 카테고리(프로젝트·네트워크·컴퓨트·스토리지) 그룹 소제목으로 정렬.

## 8. 범위 밖 (Out of Scope)

- 영문 generated schema reference 작성/대체(= provider 레포 책임, Registry SSOT).
- provider 코드/예제 변경. 본 작업은 매뉴얼(.md)만 다룬다.
- 스크린샷/이미지 신규 촬영(필요 시 후속).

## 9. 검증 기준 (Done)

- [ ] `catalog/` 제거, `resources/`(16) + `data-sources/`(18) + `guides/`(9) 생성 완료
- [ ] 16개 리소스 전부 페이지 존재 + 최소 예제 + import(또는 불가 명시)
- [ ] 18개 데이터소스 전부 페이지 존재 + 예제
- [ ] instance.md에 LIVE/STOP/REPLACE 분기 표 + GPU/NPU 포함
- [ ] guides/에 import·configuration·common-workflows 신규 3종 포함
- [ ] SUMMARY.md·README.md·상호 링크 전부 갱신, 깨진 상대 링크 0
- [ ] 모든 페이지 docs_guide.md 컨벤션(존댓말/헤딩/링크) 준수
```
