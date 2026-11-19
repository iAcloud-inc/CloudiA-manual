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
| 항상 확인 | `delete`, `restore`, `upgrade`, `remove-listener`, `remove-member`, `remove-rule`, `clone`, `copy`, `create-image`, `create-instance`, `disable`, `disable-backup`, `enable`, `enable-backup`, `live-migrate`, `migrate`, `reapply`, `redeploy`, `replace`, `resize`, `resume`, `suspend` |
| 기본으로 확인 | `stop`, `reboot`, `detach`, `disassociate`, `scale` |
| 확인 없음 | `create`, `update`, `start`, `attach`, `associate`, `add-listener`, `add-member`, `kubeconfig` |

- 서버 기능에 따라 생기는 그 밖의 변경 동작(예: 되돌리기)도 항상 확인합니다.
- 대상이 여럿이면 `--confirm-target` 을 대상마다 반복합니다.
- `--dry-run=client` 를 붙이면 보낼 요청만 보여 주고 실행하지 않습니다. 이때도 `--confirm-target` 이 필요합니다.

## 쿠버네티스

```bash
cloudiactl k8s cluster list
cloudiactl k8s node-pool list --cluster my-cluster
cloudiactl k8s cluster kubeconfig my-cluster --output-file ~/.kube/my-cluster.yaml
```

`--output-file` 로 저장한 kubeconfig 는 Linux·macOS 에서 소유자만 읽을 수 있습니다. 이미 있는 파일은 `--force` 없이 덮어쓰지 않습니다. `--force` 는 내용을 합치지 않고 파일을 통째로 바꾸므로, 다른 클러스터 정보가 든 `~/.kube/config` 에는 쓰지 마세요.

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
