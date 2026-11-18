# 문제 해결

| 증상 | 원인 | 조치 |
|---|---|---|
| `no CloudiA endpoint configured` (종료 코드 2) | 접속할 주소가 없음 | `cloudiactl login --endpoint https://<웹 콘솔 주소>` 로 처음 로그인하거나 `cloudiactl config set endpoint <주소>` |
| `plain http:// is allowed only for loopback` | `http://` 주소 | 웹 콘솔의 `https://` 주소를 씁니다 |
| 인증서 오류(`x509: certificate signed by unknown authority`) | 사설 인증서를 쓰는 설치 | 관리자에게 CA 인증서를 받아 `--ca-bundle <파일>` 또는 `cloudiactl config set ca-bundle <파일>`. 시험 환경에서만 `--insecure` |
| 종료 코드 3, `REAUTH_REQUIRED` | 로그인 만료, 비밀번호 변경, 계정 비활성화 | `cloudiactl login` 으로 다시 로그인 |
| 승인 화면에서 **허용**이 눌리지 않음 | 코드 확인란 미선택, 비밀번호 또는 일회용 코드 칸이 비어 있음 | 터미널 코드와 같은지 확인하고 확인란을 선택, 빈 칸을 채움 |
| 승인 화면이 "요청이 만료됐습니다" | 10분이 지남 | 터미널에서 `cloudiactl login` 을 다시 실행 |
| 승인 화면이 "비밀번호를 세 번 틀려 요청을 폐기했습니다" | 비밀번호나 일회용 코드를 세 번 틀림 | 터미널에서 다시 로그인을 시작 |
| 종료 코드 4 (권한 없음) | 그 작업 권한이 없거나 프로젝트 구성원이 아님 | 오류의 `requiredPermissions` 를 관리자에게 전달 |
| `CLOUDIA_AUTH_CLIENT_ID must not be cloudia-secure-login` | 웹 콘솔 로그인용 클라이언트를 환경 변수에 넣음 | `CLOUDIA_AUTH_*` 환경 변수를 지우고 `cloudiactl login` 을 씁니다 |
| `the keychain is not available` 경고 | 키 저장소를 쓸 수 없는 환경 | 로그인 정보가 소유자 전용 파일에 저장됩니다. 그 기기를 다른 사람과 같이 쓰지 마세요 |
| macOS 에서 실행이 막힘 | 브라우저로 받은 파일의 격리 표시 | [설치하기](./install.md)의 `xattr` 명령 |
| Windows 에서 `irm … \| iex` 가 연결 단계에서 실패 | Windows 10 은 TLS 1.3 을 지원하지 않음 | [설치하기](./install.md)의 "다른 방법: 파일로 받기" |
| `curl … install.sh` 가 `SSL certificate problem` | 지문이 없는 옛 명령을 썼다 | **CLI 다운로드** 창에서 명령을 다시 복사해 실행([설치하기](./install.md)) |
| `cannot read …/ca.crt (curl and openssl are required)` | `openssl` 이 없거나 웹 콘솔에 닿지 않는다 | `openssl` 을 설치하거나 웹 콘솔 주소에 접속되는지 확인 |
| `CA certificate fingerprint does not match` | 받은 CA 인증서가 창이 본 것과 다르다(중간에서 바뀌었거나 다른 서버) | 설치하지 말고 관리자에게 알린다 |
| `cloudiactl update` 가 `cannot write to …` | 설치된 파일의 폴더에 쓸 권한이 없음 | `cloudiactl install` 로 사용자 폴더에 다시 설치하고 그 파일을 씁니다 |
| `cloudiactl update` 가 `does not serve cloudiactl downloads` | 이 Cloud:iA 에 CLI 다운로드가 없음 | 관리자에게 문의합니다 |

## 요청과 응답 보기

`--debug` 를 붙이면 보낸 요청과 받은 응답의 요약이 표준 오류에 나옵니다. 토큰은 나오지 않습니다. 문의할 때는 오류의 `requestId` 를 함께 알려 주세요.

```bash
cloudiactl --debug instance list
```
