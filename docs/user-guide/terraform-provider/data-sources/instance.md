# cloudia_instance (데이터소스)

ID 또는 이름으로 기존 인스턴스 한 개를 조회합니다. 주로 다른 리소스에서 인스턴스를 참조하거나, 콘솔에서 생성한 인스턴스를 IaC로 가져올 때 사용합니다. 컬렉션 반복·필터가 필요할 때는 [instances.md](instances.md)를 사용하세요.

## 예제

```hcl
# ID로 조회
data "cloudia_instance" "by_id" {
  lookup_id = "42"
}

# 이름으로 조회 (동일한 이름이 여러 개면 에러)
data "cloudia_instance" "by_name" {
  name = "web-01"
}

output "default_nic_ipv4" {
  value = one([
    for nic in data.cloudia_instance.by_id.network_interfaces :
    nic.ipv4_address if nic.is_default_nic
  ])
}

output "data_volume_ids" {
  value = data.cloudia_instance.by_name.data_volume_ids
}
```

## 인자

| 인자 | 필수 여부 | 설명 |
|---|---|---|
| `lookup_id` | 선택 (ExactlyOneOf) | 조회할 인스턴스 ID. `name`과 둘 중 하나만 지정. |
| `name` | 선택 (ExactlyOneOf) | 조회할 인스턴스 이름. 이름이 중복되면 에러. |
| `project_id` | 선택 | 프로젝트 ID. 생략 시 provider 설정값 사용. |

## 속성

| 속성 | 타입 | 설명 |
|---|---|---|
| `id` | String | 조회된 인스턴스 ID. |
| `name` | String | 인스턴스 이름. |
| `status` | String | 백엔드 관측 상태 (`up` / `down` / `error_down` 등). |
| `power_state` | String | 의도된 전원 상태 (`RUNNING` / `STOPPED`). |
| `vcpu_number` | Number | vCPU 수. |
| `memory_total` | Number | 메모리 (MiB). |
| `network_id` | String | 소속 VPC ID. |
| `image_id` | String | 부팅 이미지 ID. |
| `secure_type` | String | 보안 모드 (`NONE` / `SEV` / `SEV_ES` / `SEV_SNP`). |
| `network_interfaces` | List(Object) | 부착된 NIC 목록. |
| `network_interfaces[*].ipv4_address` | String | NIC IPv4 주소. |
| `network_interfaces[*].is_default_nic` | Boolean | 기본 NIC 여부. |
| `network_interfaces[*].subnet_id` | String | NIC가 속한 서브넷 ID. |
| `network_interfaces[*].security_group_ids` | Set(String) | NIC에 연결된 보안그룹 ID 세트. |
| `data_volume_ids` | Set(String) | 부착된 데이터 볼륨 ID 세트 (부팅 디스크 제외). |
| `hardware_gpu` | Object | GPU passthrough 스펙. 미부착 시 null. |
| `hardware_npu` | Object | NPU passthrough 스펙. 미부착 시 null. |
| `host_machine_id` | String | 현재 스케줄된 하이퍼바이저 호스트 ID. |
| `created_at` | String | 생성 시각 (RFC3339). |
| `updated_at` | String | 마지막 수정 시각 (RFC3339). |

## 관련 항목

- [instances.md](instances.md) — 필터로 여러 인스턴스 조회
- [instance_interface.md](instance_interface.md) — NIC 단일 조회
- [instance_disks.md](instance_disks.md) — 인스턴스 디스크 목록 조회
- [instance_snapshots.md](instance_snapshots.md) — 인스턴스 스냅샷 목록 조회
- [../resources/instance.md](../resources/instance.md) — 인스턴스 리소스
- [../guides/data-sources.md](../guides/data-sources.md) — singular/plural 데이터소스 선택 가이드

---

> 전체 필드/속성 목록은 provider의 영문 레퍼런스 문서(`docs/data-sources/instance.md`, 추후 Terraform Registry 게시)를 기준으로 합니다. 본 페이지는 한국어 사용 예제와 운영 노트를 다룹니다.
