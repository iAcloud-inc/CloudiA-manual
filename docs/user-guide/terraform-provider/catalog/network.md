# 네트워크 (한국어 카탈로그)

VPC와 그 하위 네트워크 리소스. 본 카테고리에 속한 data source는 현재 없습니다 (조회는 영문 docs의 `cloudia_vpc` data source가 v1.x에 추가될 예정 — TBD).

> 본 카탈로그는 **최소 동작 예제만** 제공합니다. 전체 schema와 자세한 가이드는 영문 docs를 참고하세요.

## 페이지 인덱스

- [`cloudia_vpc`](#vpc)
- [`cloudia_subnet`](#subnet)
- [`cloudia_security_group`](#security-group)
- [`cloudia_default_security_group`](#default-security-group)
- [`cloudia_floating_ip`](#floating-ip)
- [전체 결합 예제 — VPC + 서브넷 + 보안그룹](#full-example)

---

<a id="vpc"></a>
## `cloudia_vpc`

VPC(가상 사설 네트워크) 생성. 생성 시 백엔드가 default security group과 vRouter용 public IP를 자동 할당합니다.

```hcl
resource "cloudia_vpc" "main" {
  name        = "main-vpc"
  cidr        = "10.20.0.0/16"
  description = "main vpc"
}
```

> ⚠️ 프로젝트 `public_ip_quota >= 1` 필요 (백엔드가 vRouter용 IP 자동 할당). 자세한 건 [project §quota](project.md#project) 참고.

**Import**: `terraform import cloudia_vpc.main <project_id>/<vpc_id>`

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="subnet"></a>
## `cloudia_subnet`

VPC 안의 서브넷.

```hcl
resource "cloudia_subnet" "public" {
  vpc_id = cloudia_vpc.main.id
  name   = "public-subnet"
  cidr   = "10.20.1.0/24"
  type   = "PUBLIC_SUBNET"   # 또는 "PRIVATE_SUBNET"
}
```

**Import**: `terraform import cloudia_subnet.public <project_id>/<vpc_id>/<subnet_id>`

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="security-group"></a>
## `cloudia_security_group`

VPC 안의 사용자 정의 보안그룹. inbound/outbound rule 포함.

```hcl
resource "cloudia_security_group" "web" {
  vpc_id      = cloudia_vpc.main.id
  name        = "web-sg"
  description = "HTTP/HTTPS allow"

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"   # 모든 프로토콜
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

> SSH (22번)을 열 때는 `cidr_blocks = ["0.0.0.0/0"]` 대신 관리자 IP 대역(`["10.0.0.0/8"]`)으로 좁히세요.

**Import**: `terraform import cloudia_security_group.web <project_id>/<vpc_id>/<security_group_id>`

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="default-security-group"></a>
## `cloudia_default_security_group`

VPC를 만들면 백엔드가 자동으로 생성하는 기본 SG를 **adopt(어댑트)** 해 관리합니다. 새로 만드는 게 아니라 기존 자동 생성된 것을 Terraform 관리 대상으로 가져옴.

```hcl
resource "cloudia_default_security_group" "main_default" {
  vpc_id      = cloudia_vpc.main.id
  description = "기본 SG — 관리자 대역에서만 SSH 허용"

  ingress {
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["10.0.0.0/8"]
  }
}
```

> 일반 `cloudia_security_group`과의 차이: VPC 1개당 1개만 존재, `name`이 백엔드 고정(`<vpc-name>-default-sg`), destroy 시 실제 백엔드 SG는 안 지워지고 state에서만 빠짐.

**Import**: `terraform import cloudia_default_security_group.main_default <project_id>/<vpc_id>`

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="floating-ip"></a>
## `cloudia_floating_ip`

프로젝트의 public IP pool에서 플로팅 IP를 할당하고, 필요하면 인스턴스나 내부 IP에 bind합니다.

```hcl
resource "cloudia_floating_ip" "web" {
  vpc_id      = cloudia_vpc.main.id
  name        = "web-fip"
  description = "public entrypoint"

  binding = {
    resource_type = "INSTANCE"   # 또는 "IP"
    resource_id   = cloudia_instance.web.id
    resource_ip   = "10.20.1.10"
  }
}
```

> `binding`을 생략하면 unbound 상태로 유지됩니다. 특정 public IP를 고정하고 싶으면 `ip_address`를 명시할 수 있지만, 바꿀 때는 기존 public IP가 release되고 새 IP가 할당됩니다.

**Import**: `terraform import cloudia_floating_ip.web <project_id>/<vpc_id>/<floating_ip_id>`

**전체 schema**: 본 문서는 최소 예제만 다룹니다. 전체 필드/속성 표는 provider generated reference를 참고하세요.

---

<a id="full-example"></a>
## 전체 결합 예제

VPC + public subnet + 보안그룹을 한 번에:

```hcl
resource "cloudia_vpc" "main" {
  name = "main-vpc"
  cidr = "10.20.0.0/16"
}

resource "cloudia_subnet" "public" {
  vpc_id = cloudia_vpc.main.id
  name   = "public-subnet"
  cidr   = "10.20.1.0/24"
  type   = "PUBLIC_SUBNET"
}

resource "cloudia_security_group" "ssh" {
  vpc_id = cloudia_vpc.main.id
  name   = "allow-ssh"

  ingress {
    protocol    = "tcp"
    from_port   = 22
    to_port     = 22
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

이렇게 만든 subnet과 SG를 [compute §instance](compute.md#instance) 예제에 그대로 연결해서 인스턴스를 띄울 수 있습니다.

> 여러 VPC를 동시에 만들 때 race가 발생할 수 있음 — [문제 해결 §동시성](../troubleshooting.md#concurrency) 참고.
