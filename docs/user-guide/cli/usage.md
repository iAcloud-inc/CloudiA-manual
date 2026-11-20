# 기본 사용법

## 명령 형태

```text
cloudiactl <리소스> <동작> [대상] [옵션]
```

```bash
cloudiactl instance list
cloudiactl instance get web-1
cloudiactl vpc create --name app-vpc --cidr 10.10.0.0/16
```

쓸 수 있는 리소스와 동작은 `cloudiactl --help`, `cloudiactl <리소스> --help` 로 확인합니다. 명령마다 예시가 함께 나옵니다.

## 프로젝트 지정

대부분의 명령은 프로젝트 안에서 동작합니다. 프로젝트는 이름이나 ID 로 지정합니다.

```bash
cloudiactl --project my-project instance list   # 한 번만
export CLOUDIA_PROJECT=my-project                # 이 셸에서 계속
cloudiactl config set project my-project         # 이 프로필에 저장
```

## 출력 형식

| 옵션 | 형식 | 쓰임 |
|---|---|---|
| `-o table` | 표 | 터미널에서 읽을 때(터미널이면 기본값) |
| `-o json` | JSON | 스크립트·AI 에이전트(파이프로 넘기면 기본값) |
| `-o md` | Markdown 표 | 문서·채팅에 붙일 때 |

크기 값은 `"100Gi"` 처럼 단위를 붙여 보여 줍니다. 다음 명령의 크기 옵션에 그대로 넣을 수 있습니다.

## 목록 조회

```bash
cloudiactl instance list --filter name=web            # 이름에 web 이 들어간 것
cloudiactl instance list --filter name=web- --match prefix
cloudiactl instance list --fields id,machineName,status
cloudiactl instance list --query "items[?status=='UP']"
cloudiactl instance list --all                         # 상한 없이 전부
```

- `--filter name=` 은 기본으로 대소문자를 가리지 않는 부분 일치입니다. `--match prefix` 나 `--match exact` 로 바꿀 수 있습니다.
- `--query` 는 JMESPath 식입니다.
- 출력을 파이프로 넘기면 목록은 기본 100개까지만 나옵니다. 전부 받으려면 `--all` 을 붙입니다. 터미널에서는 상한이 없습니다.
- 인스턴스의 `TERMINATED` 는 **꺼진 상태**이고, 삭제된 것이 아닙니다.

## 만들기와 기다리기

시간이 걸리는 작업은 대부분 접수만 하고 바로 돌아옵니다. `--wait` 를 붙이면 대상이 목표 상태가 될 때까지 기다립니다. `instance create`, `block attach|detach`, 스냅샷 `restore`, `k8s node-pool scale` 은 `--wait` 가 없어도 요청이 끝날 때까지는 기다립니다.

```bash
cloudiactl instance create --name web-1 --image rocky-9 --type t2.large \
  --subnet web --login-user cloudia --ssh-key my-key --wait
cloudiactl instance stop web-1 --confirm-target <ID>=web-1 --wait --timeout 10m
```

- 크기는 단위를 붙여 정수로 씁니다: `--size 100Gi`. `100`, `100G`, `1.5Gi` 는 받지 않습니다.
- 시간도 단위를 붙입니다: `--timeout 10m`.
- 다른 곳에서 시작한 작업은 `cloudiactl request wait <요청 ID>` 나 `cloudiactl instance wait <대상> --for status=UP` 으로 기다립니다.

## 위험한 작업의 대상 확인

삭제·복원처럼 되돌릴 수 없는 작업은 대상의 실제 ID 와 이름을 `--confirm-target <ID>=<이름>` 으로 한 번 더 적어야 실행됩니다. 하나라도 맞지 않으면 아무것도 실행하지 않습니다.

```bash
cloudiactl instance get web-1                       # ID 와 이름 확인
cloudiactl instance delete web-1 --confirm-target 1234=web-1
```

| 확인 | 동작 |
|---|---|
| 항상 확인 | `delete`, `detach-file-system`, `restore`, `upgrade`, `remove-listener`, `remove-member`, `remove-record`, `remove-rule`, `change-type`, `clone`, `copy`, `create-image`, `create-instance`, `disable`, `disable-backup`, `enable`, `enable-backup`, `live-migrate`, `migrate`, `reapply`, `recover`, `redeploy`, `renew-credential`, `replace`, `replace-listeners`, `resize`, `resume`, `suspend`, `uninstall-gpu-operator` |
| 기본으로 확인 | `stop`, `reboot`, `detach`, `disassociate`, `reconfigure`, `scale`, `set-gpu-time-slicing`, `set-gpu-mig` |
| 확인 없음 | `create`, `update`, `start`, `attach`, `attach-file-system`, `associate`, `add-listener`, `add-member`, `add-record`, `add-rule`, `kubeconfig`, `install-gpu-operator` |

- 서버 기능에 따라 생기는 그 밖의 변경 동작(예: 되돌리기)도 항상 확인합니다.
- 대상이 여럿이면 `--confirm-target` 을 대상마다 반복합니다.
- `--dry-run=client` 를 붙이면 보낼 요청만 보여 주고 실행하지 않습니다. 이때도 `--confirm-target` 이 필요합니다.

## 쿠버네티스

```bash
cloudiactl k8s cluster list
cloudiactl k8s node-pool list --cluster my-cluster
cloudiactl k8s file-system attach shared --cluster my-cluster      # NFS 파일 시스템을 클러스터에 연결
cloudiactl k8s file-system detach shared --cluster my-cluster --confirm-target 61=shared
cloudiactl k8s cluster kubeconfig my-cluster --output-file ~/.kube/my-cluster.yaml
```

GPU Operator 는 클러스터마다 하나라 클러스터의 동작으로 다룹니다.

```bash
cloudiactl k8s cluster gpu-operator-status my-cluster              # 설치 여부·버전·GPU 노드 수
cloudiactl k8s cluster install-gpu-operator my-cluster --wait      # 노드에 드라이버가 있으면 --preinstalled-driver
cloudiactl k8s cluster set-gpu-time-slicing my-cluster --replicas 4 --confirm-target 11=my-cluster
cloudiactl k8s cluster set-gpu-mig my-cluster --strategy single --profile all-1g.10gb --confirm-target 11=my-cluster
cloudiactl k8s cluster uninstall-gpu-operator my-cluster --confirm-target 11=my-cluster
```

설치 전에 `gpu-operator-status` 의 `attachedGpuNodeCount`(GPU 가 붙은 노드 수)가 1 이상인지 확인하세요. time-slicing·MIG 변경과 제거는 실행 중인 GPU 워크로드에 영향을 줄 수 있어 대상 확인을 받습니다. `--replicas` 는 1~10 이고 1 은 공유 해제입니다. `--profile all-disabled` 는 MIG 해제입니다.

`--output-file` 로 저장한 kubeconfig 는 Linux·macOS 에서 소유자만 읽을 수 있습니다. 이미 있는 파일은 `--force` 없이 덮어쓰지 않습니다. `--force` 는 내용을 합치지 않고 파일을 통째로 바꾸므로, 다른 클러스터 정보가 든 `~/.kube/config` 에는 쓰지 마세요.

## 스토리지

```bash
cloudiactl file-system create --name shared --type nfs --size 100Gi --subnet app --ssh-key my-key --wait
cloudiactl file-system create --name scratch --type virtiofs --size 20Gi
cloudiactl file-system instances shared                 # 이 파일 시스템을 마운트한 인스턴스
cloudiactl file-system resize shared --size 200Gi --confirm-target 61=shared
cloudiactl file-system reconfigure shared --export-write-mode sync --confirm-target 61=shared
cloudiactl object-storage get logs                      # 엔드포인트 확인
cloudiactl object-storage credential logs               # S3 액세스 키·시크릿 키
cloudiactl project-iso list                             # 이 프로젝트에서 쓸 수 있는 ISO
cloudiactl project-iso create --file ./rocky-9.iso --wait   # ISO 업로드
```

- NFS 파일 시스템은 서버가 NFS 서버 인스턴스를 만들어 `--subnet` 에 둡니다. 마운트용 보안 그룹(tcp 2049)은 서버가 붙입니다.
- 사용 중인 파일 시스템은 지울 수 없습니다. `file-system instances|clusters` 로 쓰는 곳을 확인하고 먼저 분리합니다. 클러스터에서는 `k8s file-system detach` 로, 인스턴스에서는 웹 콘솔에서 분리합니다.
- `k8s file-system detach` 는 연결 기록만 지웁니다. 클러스터에 이미 만든 스토리지 클래스·PV 는 남고 워크로드도 계속 씁니다. 다만 분리하면 파일 시스템을 지울 수 있게 되므로, `--confirm-target` 없이 실행해 클러스터 안에서 아직 참조하는 것을 먼저 확인합니다.
- 오브젝트 스토리지 키는 사용자 단위입니다. `renew-credential` 로 새 키를 받으면 이전 키는 모든 오브젝트 스토리지에서 쓸 수 없습니다. 시크릿 키는 채팅·티켓·로그에 남기지 마세요.
- NFS 파일 시스템의 크기 확장(`resize`)과 설정 변경(`reconfigure`)은 NFS 서버 인스턴스를 껐다 켜서 반영합니다. 그동안 마운트한 인스턴스·클러스터의 입출력이 멈추므로 대상 확인을 받습니다. 크기는 늘리기만 할 수 있고, virtiofs 는 크기를 바꿀 수 없습니다(이름만 `reconfigure --name`).
- `reconfigure` 는 준 옵션만 바꿉니다. `--ssh-key`·`--security-group` 은 지금 목록을 준 것으로 통째 바꿉니다(NFS 전용 보안 그룹은 서버가 남깁니다). 비밀번호는 `--password-stdin` 으로만 받습니다.
- `project-iso create` 는 `--os-variant` 를 주지 않으면 웹 콘솔처럼 파일 앞부분으로 OS 를 감지합니다. 확실하지 않으면 멈추고 `--os-variant` 를 요구합니다. 설치 미디어가 아니면 `--os-variant unknown` 을 씁니다. ISO 는 RBD(Ceph) 스토리지 도메인에 둘 수 없어 도메인을 고를 때 뺍니다.

## L7 로드 밸런서

```bash
cloudiactl l7-load-balancer create --name web-l7 --subnet app --type EXTERNAL --listener HTTP:80=web-tg
cloudiactl l7-load-balancer create --name tls-l7 --subnet app --type EXTERNAL --listener HTTPS:443=web-tg --default-certificate site.pem
cloudiactl l7-load-balancer update web-l7 --description "public web"   # 리스너는 그대로 둔다
cloudiactl l7-load-balancer listeners web-l7 -o json > listeners.json   # 고쳐서 replace-listeners 로 보낸다
cloudiactl l7-load-balancer replace-listeners web-l7 --from-file listeners.json --certificate api=api.pem --confirm-target 94=web-l7
cloudiactl l7-load-balancer change-type web-l7 --type INTERNAL --confirm-target 94=web-l7 --dry-run   # 반납할 외부 IP 확인
cloudiactl l7-load-balancer change-type web-l7 --type INTERNAL --confirm-target 94=web-l7
cloudiactl l7-load-balancer change-type web-l7 --type EXTERNAL --public-ip 203.0.113.20 --confirm-target 94=web-l7
```

- `update` 는 이름·설명만 바꿉니다.
- `change-type` 은 타입(외부·내부)과 외부 IP 주소만 바꾸고 이름·설명·내부 IP·리스너는 그대로 둡니다. 내부 IP 변경은 웹 콘솔에서 합니다.
  - 내부로 바꾸거나 다른 외부 IP 로 바꾸면 이전 외부 IP 는 로드 밸런서에서 풀리고 프로젝트에서도 삭제됩니다. 그래서 항상 대상 확인을 받고, `--dry-run` 과 확인 안내에 삭제될 주소를 보여 줍니다.
  - 내부에서 외부로 바꿀 때 `--public-ip` 를 주지 않으면 프로젝트의 미사용 외부 IP 를 쓰고, 없으면 새로 할당합니다.
  - `--public-ip` 는 프로젝트의 미사용 외부 IP 이거나 아직 할당되지 않은 주소여야 합니다. 할당되지 않은 주소는 새 외부 IP 로 할당되어 프로젝트 할당량에 들어가고, 다른 프로젝트가 가진 주소는 서버가 거절합니다.
- 서버는 리스너 목록(규칙·동작·인증서 포함)을 통째로 받습니다. `replace-listeners` 는 파일에 없는 리스너·규칙·인증서를 지우므로 항상 대상 확인을 받습니다. 남길 항목은 `listeners` 출력의 id 를 그대로 둡니다.
- 규칙·리다이렉트·고정 응답·SNI 인증서는 `--from-file`(JSON 또는 YAML)로 줍니다. 전달 대상은 `targetGroupId` 대신 `targetGroup`(ID 또는 이름)으로 적어도 됩니다.
- 인증서는 인증서 체인과 개인 키를 담은 `.pem` 파일입니다. 파일의 `fileKey` 와 `--certificate <fileKey>=<파일>` 로 잇습니다. 이미 있는 인증서(id 만 있고 fileKey 가 없음)는 PEM 을 그대로 둡니다. CLI 는 파일 내용을 출력하지 않습니다.

## 종료 코드

스크립트에서는 종료 코드로 결과를 판단합니다.

| 코드 | 뜻 |
|---|---|
| 0 | 성공 |
| 1 | 그 밖의 오류 |
| 2 | 사용법 오류(옵션·단위·대상 확인) |
| 3 | 로그인 필요 |
| 4 | 권한 없음 |
| 5 | 대상 없음 |
| 6 | 비동기 작업 실패 |
| 7 | 기다리는 시간 초과(작업은 계속 진행 중일 수 있음) |
| 8 | 여러 대상 중 일부 실패. 결과의 대상별 `exitCode` 를 봅니다 |
| 9 | 요청 하나가 일부만 수행됨 |
| 10 | 잠시 뒤 다시 시도할 수 있음(다른 작업 진행 중 등) |
| 11 | 결과를 알 수 없음(응답 유실). 같은 명령을 다시 보내기 전에 `get` 으로 반영 여부를 확인하세요 |

JSON 출력이면 오류는 표준 오류(stderr)에 `errorCode`, `message`, `hint` 와 함께 나옵니다.
