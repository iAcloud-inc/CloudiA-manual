# 서버 버전 호환

`cloudiactl` 은 접속한 Cloud:iA 와 **같은 버전**으로 쓰는 것이 기본입니다. 웹 콘솔이 자기와 같은 버전의 CLI 를 내려주고, `cloudiactl update` 도 콘솔과 같은 버전으로 맞춥니다([설치하기](./install.md)의 "업데이트"). 여러 Cloud:iA 를 한 CLI 로 다룰 때는 아래 표로 버전이 다른 서버에서 무엇이 달라지는지 확인합니다.

## 명령이 만들어지는 방식

명령은 두 종류입니다.

- **기본 명령**: 인스턴스·VPC·보안 그룹·블록·로드 밸런서·쿠버네티스 클러스터처럼 CLI 에 들어 있는 명령입니다. 서버가 옛 버전이어도 남아 있고, 서버에 필요한 API 가 없으면 실행할 때 실패하거나 옛 방식으로 동작합니다.
- **서버 API 로 만드는 명령**: CLI 가 접속한 서버의 API 설명을 읽어 만듭니다. 설명을 받았으면 서버에 없는 기능은 명령에도 나타나지 않습니다(`unknown command`). 설명을 받지 못하면 CLI 에 들어 있는 목록을 써서 명령은 보이지만, 서버에 API 가 없으면 실행할 때 실패합니다. 어떤 명령이 서버에서 왔는지는 `cloudiactl commands` 의 `generated` 열로 봅니다.

CLI 는 서버가 알리는 기능 목록도 읽어, 옛 서버에서는 새 방식 대신 옛 방식으로 요청합니다. 목록을 읽지 못하면 옛 서버로 보고 동작합니다.

## 기능별 최소 서버 버전

| 기능 | 명령 | 최소 서버 버전 | 그보다 옛 서버에서 |
|---|---|---|---|
| 웹 콘솔 승인 로그인 | `login`, `logout`, 로그인 자동 갱신 | 1.7.0 | 로그인을 시작하지 못하고 `cannot start the login` 으로 끝납니다 |
| 스토리지 도메인 조회 | `block create`, `image create`, `file-system create`(VirtioFS), `k8s cluster create`, `k8s node-pool create` | 1.7.0 | `--storage-domain` 을 지정해도 도메인 목록을 먼저 읽으므로 실패합니다(`permission denied` 또는 `target not found`) |
| 같은 요청 재시도 보호(`--client-token`) | 인스턴스·VPC·블록·노드 풀 생성 등 | 1.7.0 | `--client-token` 을 주면 `this server does not support --client-token` 으로 멈춥니다. 주지 않으면 키 없이 요청합니다 |
| 노드 풀 크기 변경 | `k8s node-pool scale` | 1.7.0 | 오토 스케일링 그룹 수정 API 로 바꿉니다. 이때 필요한 권한이 오토 스케일링 그룹 편집으로 바뀝니다 |
| 다음 마이너 버전으로 클러스터 업그레이드 | `k8s cluster upgrade --k8s-image` | 1.7.0 | 서버가 현재 마이너 버전 이미지만 받습니다. CLI 가 그 사실을 안내합니다 |
| 보안 그룹 규칙 하나씩 추가·회수 | `security-group add-rule`, `remove-rule` | 1.8.0 | 규칙 목록 전체를 바꾸는 방식으로 동작합니다. 보내기 직전에 목록을 다시 읽어, 그사이 바뀌었으면 보내지 않고 종료 코드 10 으로 멈춥니다 |
| 블록 하나씩 붙이기·떼기 | `block attach`, `block detach` | 1.8.0 | 인스턴스의 블록 목록 전체를 바꾸는 방식으로 동작합니다. 보내기 직전에 목록이 바뀌었으면 보내지 않고 종료 코드 10 으로 멈춥니다 |
| 이미지 파일 나눠 올리기 | `image create --file` | 1.8.0 | 파일을 한 번에 올립니다. 실패하면 명령을 다시 실행해 처음부터 올립니다 |
| 프로젝트 ISO | `project-iso create`, `list`, `get` | 1.8.0 | 쓸 수 없습니다. 서버에 API 가 없어 `permission denied`(종료 코드 4)나 `target not found` 로 끝납니다. 권한 문제가 아닙니다 |
| 노드 풀 ID 로 바로 조회 | `k8s node-pool get <ID>`(`--cluster` 없이) | 1.8.0 | `--cluster` 를 붙이라고 안내합니다 |
| 서버 API 로 만드는 명령 대부분 | `launch-template`, `schedule`, `nacl`, `affinity-group`, `auto-scaling-group`, `instance clone`, `block copy`, `l7-load-balancer delete`, `l7-target-group create` 등 | 1.8.0 | 명령이 나타나지 않습니다. 1.7.0 서버에서는 이런 명령 대부분이, 1.6 서버에서는 전부 없고 기본 명령만 남습니다 |
| CLI 다운로드와 `cloudiactl update` | `update`, `update --check` | 1.8.0 | `does not serve cloudiactl downloads` 로 끝납니다 |

- 위에 없는 기본 명령(인스턴스·VPC·서브넷·플로팅 IP·L4/L7 로드 밸런서·DNS·포트 포워딩·오브젝트 스토리지·스냅샷·SSH 키·파일 시스템·GPU Operator·kubeconfig 등)은 1.6 서버에도 API 가 있습니다.
- 표의 버전은 Cloud:iA 릴리스 버전입니다. 1.7.x 핫픽스는 1.7.0 과 같습니다.
- 1.7.0 보다 옛 서버에는 로그인할 수 없으므로 지원하지 않습니다.
- 서버에 없는 API 를 부르면 서버가 권한 거부(`permission denied`)로 답하는 경우가 있습니다. 관리자가 권한을 줘도 해결되지 않으니 먼저 서버 버전을 확인합니다.

## 버전 확인

```bash
cloudiactl version            # CLI 버전
cloudiactl update --check     # 웹 콘솔이 내주는 CLI 버전과 같은지
cloudiactl commands -o json   # source: 명령 목록을 어디서 만들었는지(cache=서버, builtin=CLI 내장)
```

`source` 가 `builtin` 이면 서버 API 설명을 읽지 못한 것입니다. `cloudiactl commands refresh` 로 다시 받습니다.
