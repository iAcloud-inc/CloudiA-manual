# 호스트 헤더와 경로 조건으로 L7 요청 라우팅하기

이 문서는 어플리케이션 로드 밸런서의 HTTPS 리스너에서 `호스트 헤더`와 `경로` 조건을 함께 사용해 요청을 서로 다른 타겟 그룹으로 전달하는 실습입니다. 하나의 규칙 안에서 `호스트 헤더`와 `경로`를 함께 설정하면 두 조건이 모두 일치할 때만 규칙이 적용됩니다. 같은 조건 안에 여러 값을 추가하면 여러 값 중 하나만 일치해도 조건이 일치한 것으로 처리됩니다.

후반부에서는 같은 환경으로 두 종류의 세션 고정성도 확인합니다. 리스너 작업의 `세션 고정성`은 첫 요청에서 선택된 타겟 그룹을 고정하므로 페이지 색상이 유지되는지 확인합니다. 타겟 그룹 정책의 `세션 고정성`은 선택된 타겟 그룹 안의 타겟 인스턴스를 고정하므로 페이지의 `Instance` 값이 유지되는지 확인합니다.

## 사전 준비
- Cloud:iA 웹콘솔 접근 가능
- 프로젝트 계정(`project-owner`)으로 로그인 가능
- [VPC](../../project/network/vpc/vpc.md)와 [서브넷](../../project/network/subnet/subnet.md) 준비
- 정적 페이지를 제공할 [인스턴스](../../project/vm/instance/instance.md) 6대 준비
- 타겟 인스턴스의 [보안그룹](../../project/security/security-group/security-group.md)에서 `8080/tcp` 인바운드 허용
- `BLUE`, `GREEN`, `CANARY` 용도의 [어플리케이션 타겟 그룹](../../project/network/l7-target-group/l7-target-group.md) 3개 준비
- 외부 타입 [어플리케이션 로드 밸런서](../../project/network/l7-load-balancer/l7-load-balancer.md) 준비. 인증서 생성에 로드 밸런서 외부 IP가 필요하므로, 처음에는 리스너 프로토콜이 `HTTP`인지 `HTTPS`인지와 관계없이 외부 타입 로드 밸런서와 외부 IP가 준비되어 있으면 됩니다.
- 인증서 SAN과 도메인 매핑에 사용할 로드 밸런서 `외부 IP 주소` 확인. 외부 IP 준비가 필요한 경우 [외부 IP](../../project/network/external-ip/external-ip.md) 매뉴얼을 참고합니다.
- 로드 밸런서 외부 IP 확인 후 HTTPS 검증용 PEM 인증서 생성. 인증서에는 `test.iacloud.kr`, `second.test.iacloud.kr` 도메인과 로드 밸런서 외부 IP가 포함되어 있어야 함
- 인증서 생성 후 `HTTPS / 443` 리스너를 추가하거나 기존 HTTPS 리스너에 인증서를 등록할 수 있어야 함
- 테스트를 수행할 클라이언트에서 `test.iacloud.kr`, `second.test.iacloud.kr`가 로드 밸런서 외부 IP로 해석되도록 DNS 또는 hosts 파일 매핑 준비
- 세션 고정성 확인을 위해 반복 요청을 수행할 브라우저 준비

### 인스턴스 세팅
이 실습은 역할별 백엔드 응답을 구분해야 하므로 `BLUE`, `GREEN`, `CANARY` 역할의 인스턴스를 각각 2대씩 준비합니다. 인스턴스 생성 방법은 [인스턴스](../../project/vm/instance/instance.md) 매뉴얼을 참고합니다.

| 역할 | 권장 인스턴스 | 응답 API path | 연결할 타겟 그룹 |
|---|---|---|---|
| `BLUE` | `BLUE-1`, `BLUE-2` | `/apiv1/test.html` | `example-blue-tg` |
| `GREEN` | `GREEN-1`, `GREEN-2` | `/apiv2/test.html` | `example-green-tg` |
| `CANARY` | `CANARY-1`, `CANARY-2` | `/apiv3/test.html` | `example-canary-tg` |

각 인스턴스에는 같은 VPC의 서브넷과 `8080/tcp`를 허용한 보안그룹을 연결합니다. 인스턴스 접속은 Cloud:iA 웹 콘솔의 `콘솔`을 사용하거나, 플로팅 IP와 SSH를 사용할 수 있습니다.

인스턴스에 접속한 뒤 아래 Python 스크립트를 생성합니다.

```bash
cat > ~/l7-backend.py <<'PY'
#!/usr/bin/env python3
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

ROLE = os.environ.get("ROLE", "BLUE").upper()
PORT = int(os.environ.get("PORT", "8080"))

API_PATHS = {
    "BLUE": "/apiv1/test.html",
    "GREEN": "/apiv2/test.html",
    "CANARY": "/apiv3/test.html",
}

COLORS = {
    "BLUE": "#2563eb",
    "GREEN": "#16a34a",
    "CANARY": "#facc15",
}

if ROLE not in API_PATHS:
    raise SystemExit("ROLE must be one of: BLUE, GREEN, CANARY")

API_PATH = API_PATHS[ROLE]
BG_COLOR = COLORS[ROLE]
FG_COLOR = "#111111" if ROLE == "CANARY" else "#ffffff"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", API_PATH):
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"not-found")
            return

        body = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>{ROLE} backend</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: {BG_COLOR};
      color: {FG_COLOR};
      font-family: sans-serif;
    }}
    main {{
      padding: 48px;
      border-radius: 20px;
      background: rgba(255,255,255,0.16);
    }}
    h1 {{ font-size: 56px; margin: 0 0 16px; }}
    p {{ font-size: 24px; margin: 8px 0; }}
  </style>
</head>
<body>
  <main>
    <h1>{ROLE}</h1>
    <p>API path: <strong>{API_PATH}</strong></p>
    <p>Instance: <strong>{os.uname().nodename}</strong></p>
  </main>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
PY
chmod +x ~/l7-backend.py
```

각 인스턴스의 역할에 맞춰 서버를 실행합니다. 예를 들어 `BLUE-1`, `BLUE-2`에서는 `ROLE=BLUE`로 실행하고, `GREEN-1`, `GREEN-2`에서는 `ROLE=GREEN`으로 실행합니다.

```bash
ROLE=BLUE PORT=8080 nohup python3 ~/l7-backend.py > ~/l7-backend.log 2>&1 &
```

```bash
ROLE=GREEN PORT=8080 nohup python3 ~/l7-backend.py > ~/l7-backend.log 2>&1 &
```

```bash
ROLE=CANARY PORT=8080 nohup python3 ~/l7-backend.py > ~/l7-backend.log 2>&1 &
```

실행 후 인스턴스 내부에서 응답을 확인합니다.

```bash
curl -i http://127.0.0.1:8080/
curl -i http://127.0.0.1:8080/apiv1/test.html
curl -i http://127.0.0.1:8080/apiv2/test.html
curl -i http://127.0.0.1:8080/apiv3/test.html
```

확인 기준은 다음과 같습니다.

| 역할 | 200 응답 경로 | 404 응답 경로 |
|---|---|---|
| `BLUE` | `/`, `/apiv1/test.html` | `/apiv2/test.html`, `/apiv3/test.html` |
| `GREEN` | `/`, `/apiv2/test.html` | `/apiv1/test.html`, `/apiv3/test.html` |
| `CANARY` | `/`, `/apiv3/test.html` | `/apiv1/test.html`, `/apiv2/test.html` |

이 준비가 끝나면 역할별 인스턴스를 각 어플리케이션 타겟 그룹에 등록합니다. 타겟 그룹의 `프로토콜`은 `HTTP`, `포트 번호`는 `8080`을 사용합니다. `상태 검사 설정`에서 `활성화 여부`를 `활성화`로 설정한 뒤 `상태 검사 경로`를 `/`로 입력합니다.

### 인증서 생성
HTTPS 리스너와 호스트 헤더 조건을 검증하려면 `test.iacloud.kr`, `second.test.iacloud.kr` 도메인을 포함한 인증서가 필요합니다. 인증서 SAN에 로드 밸런서 외부 IP를 포함하려면 먼저 외부 타입 로드 밸런서가 생성되어 있어야 합니다. 이 단계에서는 HTTPS 리스너가 아직 없어도 됩니다.

작업 PC 또는 인증서를 생성할 수 있는 환경(예시는 Linux 환경)에서 외부 타입 로드 밸런서의 외부 IP를 확인한 뒤 `<LB_EXTERNAL_IP>` 값을 실제 IP로 바꿔 실행합니다.

```bash
mkdir -p ~/cert-test
cd ~/cert-test

cat > san.cnf <<'EOF'
[ req ]
default_bits       = 2048
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[ dn ]
C  = KR
ST = Seoul
L  = Seoul
O  = Cloudia
OU = Test
CN = test.iacloud.kr

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = test.iacloud.kr
DNS.2 = second.test.iacloud.kr
IP.1  = <LB_EXTERNAL_IP>
EOF

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout test.key \
  -out test.crt \
  -config san.cnf \
  -extensions req_ext

cat test.key test.crt > test.iacloud.kr.pem
openssl x509 -in test.crt -noout -text | grep -A2 "Subject Alternative Name"
```

생성한 `test.iacloud.kr.pem` 파일은 이후 HTTPS 리스너 등록에 사용할 인증서 파일입니다. 인증서 파일 형식과 등록 기준은 [어플리케이션 로드 밸런서의 HTTPS 인증서](../../project/network/l7-load-balancer/l7-load-balancer.md#https-인증서)를 참고합니다.

도메인 기반 검증을 위해 테스트를 수행할 클라이언트에서 두 도메인이 로드 밸런서 외부 IP로 해석되도록 설정합니다.

```bash
echo "<LB_EXTERNAL_IP> test.iacloud.kr second.test.iacloud.kr" | sudo tee -a /etc/hosts
getent hosts test.iacloud.kr second.test.iacloud.kr
```

인증서 생성과 hosts 매핑이 끝나면 다음 단계에서 `HTTPS / 443` 리스너를 준비합니다. 이후 브라우저 또는 `curl -k`로 `https://test.iacloud.kr`, `https://second.test.iacloud.kr` 주소를 사용해 라우팅을 검증할 수 있습니다.

## 개요
1. [검증 환경 확인](#step-1)
2. [HTTPS 443 리스너 준비](#step-2)
3. [HTTPS 리스너에 호스트 헤더와 경로 조건 규칙 추가](#step-3)
4. [기본 작업을 고정 응답으로 변경](#step-4)
5. [라우팅 결과 확인](#step-5)
6. [타겟 그룹 세션 고정성 확인](#step-6)
7. [타겟 세션 고정성 확인](#step-7)

<a id="step-1"></a>
## 1단계: 검증 환경 확인
**수행 계정/화면:** `프로젝트 계정` / `프로젝트 페이지`

### 절차
1. `네트워크 > 타겟 그룹`에서 `BLUE`, `GREEN`, `CANARY` 타겟 그룹이 준비되어 있는지 확인합니다.
2. 각 타겟 그룹의 프로토콜과 포트가 `HTTP / 8080`인지 확인합니다.
3. 각 타겟 그룹에 역할별 인스턴스가 등록되어 있는지 확인합니다.
4. `네트워크 > 로드 밸런서`에서 대상 외부 타입 어플리케이션 로드 밸런서 상세로 이동합니다.
5. 로드 밸런서의 `외부 IP 주소`를 확인합니다.
6. 클라이언트에서 사용할 도메인이 로드 밸런서 외부 IP로 해석되는지 확인합니다.
7. `HTTPS / 443` 리스너가 이미 있으면 재사용할 수 있고, 없으면 다음 단계에서 추가합니다.

### 입력 예시
| 항목 | 값 |
|---|---|
| 로드 밸런서 | `example-l7-lb-001 / 외부` |
| 로드 밸런서 외부 IP | `<LB_EXTERNAL_IP>` |
| HTTPS 리스너 | 다음 단계에서 `HTTPS / 443`으로 추가 또는 기존 리스너 재사용 |
| 인증서 도메인 | `test.iacloud.kr`, `second.test.iacloud.kr` |
| BLUE 타겟 그룹 | `example-blue-tg / HTTP:8080 / BLUE-1, BLUE-2` |
| GREEN 타겟 그룹 | `example-green-tg / HTTP:8080 / GREEN-1, GREEN-2` |
| CANARY 타겟 그룹 | `example-canary-tg / HTTP:8080 / CANARY-1, CANARY-2` |
| hosts 매핑 예시 | `<LB_EXTERNAL_IP> test.iacloud.kr second.test.iacloud.kr` |

### 확인
- 각 타겟 그룹의 타겟이 정상 상태입니다.
- 외부 타입 로드 밸런서의 외부 IP 주소를 확인했습니다.
- HTTPS 443 리스너는 기존 항목을 사용하거나 다음 단계에서 추가할 수 있는 상태입니다.
- `test.iacloud.kr`, `second.test.iacloud.kr`가 동일한 로드 밸런서 외부 IP로 해석됩니다.

<a id="step-2"></a>
## 2단계: HTTPS 443 리스너 준비
**수행 계정/화면:** `프로젝트 계정` / `프로젝트 페이지`

### 절차
1. 대상 로드 밸런서 상세 화면의 `리스너 정보`로 이동합니다.
2. `HTTPS / 443` 리스너가 없으면 리스너를 추가합니다.
3. 프로토콜은 `HTTPS`, 포트는 `443`으로 입력합니다.
4. `기본 인증서 파일`에 인증서 생성 단계에서 만든 `test.iacloud.kr.pem` 파일을 등록합니다. 자세한 기준은 [어플리케이션 로드 밸런서의 HTTPS 인증서](../../project/network/l7-load-balancer/l7-load-balancer.md#https-인증서)를 참고합니다.
5. 기본 작업은 이 실습의 미일치 요청 확인을 위해 `고정 응답 반환`으로 설정합니다.
6. `저장`을 클릭합니다.
7. `HTTPS / 443` 리스너가 이미 있으면 해당 리스너를 편집해 인증서와 기본 작업이 아래 입력 예시와 같은지 확인합니다.

### 입력 예시
| 항목 | 값 |
|---|---|
| 프로토콜 | `HTTPS` |
| 포트 번호 | `443` |
| 기본 인증서 파일 | `test.iacloud.kr.pem` |
| 기본 작업 | `고정 응답 반환` |
| 상태 코드 | `418` |
| Content-Type | `text/plain` |
| 메시지 본문 | `default-fallback` |

### 확인
- `리스너 정보`에 `HTTPS / 443` 리스너가 표시됩니다.
- HTTPS 리스너에 `test.iacloud.kr.pem` 인증서가 연결되어 있습니다.
- 기본 작업이 `고정 응답 반환`으로 표시됩니다.

<a id="step-3"></a>
## 3단계: HTTPS 리스너에 호스트 헤더와 경로 조건 규칙 추가
**수행 계정/화면:** `프로젝트 계정` / `프로젝트 페이지`

### 절차
1. 대상 로드 밸런서 상세 화면의 `리스너 정보`에서 `HTTPS / 443` 리스너를 찾습니다.
2. 해당 리스너의 `규칙 정보`에서 `보기`를 클릭합니다.
3. `추가`를 클릭해 첫 번째 규칙을 만듭니다.
4. `조건`에서 `조건 유형=호스트 헤더`, 값은 `test.iacloud.kr`로 입력합니다.
5. `조건 추가`를 클릭하고 `조건 유형=경로`, 값은 `/apiv1/`로 입력합니다.
6. `작업`에서 `타겟 그룹으로 전달`을 선택하고 `example-blue-tg`를 `가중치=100`으로 추가합니다.
7. 같은 방식으로 두 번째, 세 번째 규칙을 추가합니다.
8. 규칙 목록에서 우선 순위가 `BLUE`, `GREEN`, `CANARY` 순서인지 확인합니다. 필요하면 드래그 앤 드롭으로 조정합니다.
9. `저장`을 클릭합니다.

### 입력 예시
| 규칙 | 조건 | 작업 |
|---|---|---|
| 규칙 1 | `호스트 헤더=test.iacloud.kr` 그리고 `경로=/apiv1/` | `타겟 그룹으로 전달` -> `example-blue-tg`, `가중치=100` |
| 규칙 2 | `호스트 헤더=second.test.iacloud.kr` 그리고 `경로=/apiv2/` | `타겟 그룹으로 전달` -> `example-green-tg`, `가중치=100` |
| 규칙 3 | `호스트 헤더=test.iacloud.kr 또는 second.test.iacloud.kr` 그리고 `경로=/apiv3/` | `타겟 그룹으로 전달` -> `example-canary-tg`, `가중치=100` |

### 확인
- 규칙 1은 `호스트 헤더`와 `경로` 조건이 모두 표시됩니다.
- 규칙 2는 `second.test.iacloud.kr`와 `/apiv2/` 조합으로 표시됩니다.
- 규칙 3은 `호스트 헤더` 조건에 두 도메인이 함께 표시되고, `경로=/apiv3/` 조건이 함께 표시됩니다.
- 각 규칙의 작업이 의도한 타겟 그룹으로 표시됩니다.

<a id="step-4"></a>
## 4단계: 기본 작업을 고정 응답으로 변경
**수행 계정/화면:** `프로젝트 계정` / `프로젝트 페이지`

### 절차
1. HTTPS 리스너의 `규칙 정보` 화면에서 마지막 `기본 작업` 행을 확인합니다.
2. `기본 작업`이 이미 `고정 응답 반환`이면 설정값만 확인합니다.
3. 다른 작업으로 설정되어 있으면 `기본 작업` 행을 편집하고 작업을 `고정 응답 반환`으로 변경합니다.
4. 상태 코드, Content-Type, 메시지 본문을 입력합니다.
5. `저장`을 클릭합니다.

### 입력 예시
| 항목 | 값 |
|---|---|
| 작업 | `고정 응답 반환` |
| 상태 코드 | `418` |
| Content-Type | `text/plain` |
| 메시지 본문 | `default-fallback` |

### 확인
- 어떤 규칙에도 매칭되지 않는 요청은 타겟 그룹으로 전달되지 않고 고정 응답으로 처리됩니다.
- 기본 작업 행에 `고정 응답 반환` 설정이 표시됩니다.

<a id="step-5"></a>
## 5단계: 라우팅 결과 확인
**수행 계정/화면:** `프로젝트 계정 + 로컬 터미널` / `브라우저 또는 curl`

### 절차
1. 브라우저 또는 `curl`로 규칙별 URL을 호출합니다.
2. 호스트 헤더와 경로가 모두 일치하는 요청이 해당 타겟 그룹으로 전달되는지 확인합니다.
3. 호스트 헤더만 일치하거나 경로만 일치하는 요청은 기본 작업으로 처리되는지 확인합니다.
4. 규칙 3에서 두 호스트 중 어느 도메인을 사용해도 `/apiv3/` 경로가 일치하면 CANARY 타겟 그룹으로 전달되는지 확인합니다.

### 입력 예시
| 확인 항목 | 요청 예시 | 기대 결과 |
|---|---|---|
| 규칙 1 AND 일치 | `https://test.iacloud.kr/apiv1/test.html` | `BLUE` 응답 |
| 규칙 1 Host만 일치 | `https://test.iacloud.kr/unknown` | `418`, `default-fallback` |
| 규칙 1 Path만 일치 | `https://<LB_EXTERNAL_IP>/apiv1/test.html` | `418`, `default-fallback` |
| 규칙 2 AND 일치 | `https://second.test.iacloud.kr/apiv2/test.html` | `GREEN` 응답 |
| 규칙 2 Host만 일치 | `https://second.test.iacloud.kr/unknown` | `418`, `default-fallback` |
| 규칙 3 Host OR 값 1 일치 | `https://test.iacloud.kr/apiv3/test.html` | `CANARY` 응답 |
| 규칙 3 Host OR 값 2 일치 | `https://second.test.iacloud.kr/apiv3/test.html` | `CANARY` 응답 |
| 전체 미일치 | `https://<LB_EXTERNAL_IP>/unknown` | `418`, `default-fallback` |

### curl 예시
```bash
curl -k https://test.iacloud.kr/apiv1/test.html
curl -k https://second.test.iacloud.kr/apiv2/test.html
curl -k https://test.iacloud.kr/apiv3/test.html
curl -k -i https://test.iacloud.kr/unknown
curl -k -i https://<LB_EXTERNAL_IP>/unknown
```

### 확인
- `호스트 헤더`와 `경로`가 모두 일치하는 요청만 각 규칙에 매칭됩니다.
- 같은 `호스트 헤더` 조건 안의 여러 값은 OR 조건처럼 동작합니다.
- 서로 다른 조건인 `호스트 헤더`와 `경로`는 AND 조건처럼 동작합니다.
- 어떤 규칙에도 매칭되지 않는 요청은 `기본 작업`의 고정 응답을 반환합니다.

<a id="step-6"></a>
## 6단계: 타겟 그룹 세션 고정성 확인
**수행 계정/화면:** `프로젝트 계정 + 브라우저` / `프로젝트 페이지`

이 단계는 HTTPS 리스너의 `기본 작업`에서 여러 타겟 그룹을 전달 대상으로 지정하고, 첫 요청에서 선택된 타겟 그룹이 같은 브라우저 세션에서 계속 유지되는 동작을 확인합니다. 페이지 색상은 어떤 타겟 그룹으로 전달되었는지 구분하는 기준입니다.

### 절차
1. 대상 로드 밸런서 상세 화면의 `리스너 정보`에서 `HTTPS / 443` 리스너를 찾습니다.
2. 해당 리스너의 `규칙 정보`에서 `보기`를 클릭합니다.
3. 마지막 `기본 작업` 행을 편집합니다.
4. 작업을 `타겟 그룹으로 전달`로 변경합니다.
5. 전달 대상에 `example-blue-tg`, `example-green-tg`, `example-canary-tg`를 추가하고 각 `가중치`를 `100`으로 입력합니다.
6. 같은 작업 화면에서 `세션 고정성=활성화`, `쿠키 유효 시간=120초`로 설정합니다.
7. 설정 기준은 [어플리케이션 로드 밸런서의 기본 작업](../../project/network/l7-load-balancer/l7-load-balancer.md#기본-작업)을 참고합니다.
8. 브라우저에서 `https://test.iacloud.kr/`를 열고 새로고침으로 여러 번 반복 요청합니다.
9. 응답 화면의 색상이 계속 같은 타겟 그룹을 가리키는지 확인합니다.

### 입력 예시
| 항목 | 값 |
|---|---|
| 수정 대상 | `HTTPS / 443` 리스너의 `기본 작업(*)` |
| 작업 | `타겟 그룹으로 전달` |
| 전달 대상 | `example-blue-tg`, `example-green-tg`, `example-canary-tg` |
| 가중치 | 각 `100` |
| 세션 고정성 | `활성화` |
| 쿠키 유효 시간 | `120초` |
| 확인 URL | `https://test.iacloud.kr/` |
| 확인 방법 | 같은 브라우저에서 여러 번 새로고침 |

### 확인
- 같은 브라우저에서 반복 요청하면 페이지 색상이 같은 타겟 그룹을 가리킵니다.
- 다른 브라우저 또는 시크릿 창을 사용하면 별도의 세션으로 처리되므로 다른 타겟 그룹이 선택될 수 있습니다.
- 이 단계의 확인 기준은 타겟 그룹입니다. 타겟 그룹 안의 `Instance` 값은 타겟 그룹 정책의 세션 고정성이 꺼져 있으면 달라질 수 있습니다.
- 쿠키가 삭제되거나 만료되면 타겟 그룹이 다시 선택될 수 있습니다.

<a id="step-7"></a>
## 7단계: 타겟 세션 고정성 확인
**수행 계정/화면:** `프로젝트 계정 + 브라우저` / `프로젝트 페이지`

이 단계는 `example-green-tg`의 `세션 고정성`을 활성화해 같은 브라우저 세션의 요청이 같은 타겟 인스턴스로 유지되는 동작을 확인합니다. 기존 규칙 2를 사용하므로 확인 URL은 `second.test.iacloud.kr`와 `/apiv2/` 경로를 사용합니다.

### 절차
1. `네트워크 > 타겟 그룹` 목록에서 `example-green-tg` 행을 선택합니다.
2. 상단의 `편집` 버튼을 클릭합니다.
3. `타겟 그룹 정책`에서 `세션 고정성=활성화`, `쿠키 유효 시간=120초`로 설정합니다.
4. 설정 기준은 [어플리케이션 타겟 그룹의 세션 고정성](../../project/network/l7-target-group/l7-target-group.md#세션-고정성)을 참고합니다.
5. 설정을 저장하고 `example-green-tg`의 타겟 `GREEN-1`, `GREEN-2`가 정상 상태인지 확인합니다.
6. 브라우저에서 `https://second.test.iacloud.kr/apiv2/test.html`를 열고 새로고침으로 여러 번 반복 요청합니다.
7. 응답 화면의 `Instance` 값이 유지되는지 확인합니다.

### 입력 예시
| 항목 | 값 |
|---|---|
| 수정 대상 | `example-green-tg` |
| 알고리즘 | `라운드 로빈` |
| 세션 고정성 | `활성화` |
| 쿠키 유효 시간 | `120초` |
| 확인 URL | `https://second.test.iacloud.kr/apiv2/test.html` |
| 확인 기준 | 페이지의 `Instance` 값 |
| 확인 방법 | 같은 브라우저에서 여러 번 새로고침 |

### 확인
- 같은 브라우저에서 반복 요청하면 `Instance` 값이 동일하게 유지됩니다.
- 다른 브라우저 또는 시크릿 창을 사용하면 별도의 세션으로 처리되므로 다른 `Instance`가 선택될 수 있습니다.
- 이 단계의 확인 기준은 타겟 인스턴스입니다. 페이지 색상과 `API path`는 계속 GREEN 타겟 그룹과 `/apiv2/test.html`을 가리킵니다.
- 쿠키가 삭제되거나 만료되면 타겟 인스턴스가 다시 선택될 수 있습니다.
