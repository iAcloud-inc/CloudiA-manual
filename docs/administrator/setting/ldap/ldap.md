# 사용자 연동

## LDAP Provider 목록

### 기본 정보
- 페이지 크기: `10` (로컬 페이지네이션)
- 선택 방식: 단일 선택
- 컬럼
  - 이름(상세 이동)
  - ID
  - 활성화 상태
  - 연결 URL

### 상단 액션
- 생성
- 편집
- 삭제
- 활성화
- 비활성화
- 더보기
  - 모든 사용자 동기화
  - 변경된 사용자 동기화
  - 연동 해제
  - 가져온 사용자 삭제

### 상태 제약
- 활성화 버튼: 선택 Provider가 `inactive(false)`일 때 활성
- 비활성화 버튼: 선택 Provider가 `active(true)`일 때 활성

### 실행형 모달
- 삭제 모달: `사용자 연동 삭제`
- 실행 모달(동기화/연동해제/가져온 사용자 삭제)
  - 타이틀: `사용자 연동`
  - 확인 버튼: `실행`

## LDAP Provider 생성/편집

### 경로 및 권한
- 생성: `/administrator/setting/ldap/create` (`userfederation-edit`)
- 편집: `/administrator/setting/ldap/update?prdid={providerId}` (`userfederation-edit`)

### 저장 활성 조건
- General Options 유효
- Connection Settings 유효 + 연결 테스트 성공
- Authentication Settings 유효 + 인증 테스트 성공
- Searching Required Settings 유효

### 섹션 1. General Options
- 이름* (최대 20)
- Vendor* (`ad`, `other`)

### 섹션 2. Connection and Authentication
Connection 항목
- Connection URL*
- Enable StartTLS
- Use Truststore SPI (`always/never`)
- Connection Pooling
- Connection Timeout(ms)
- 연결 테스트 버튼(`testConnection` / 성공 후 `reenter`)

Authentication 항목
- Bind Type* (`simple/none`)
- Bind DN*
- Bind Credentials*
- 인증 테스트 버튼(`testAuthentication` / 성공 후 `reenter`)

테스트 상태 규칙
- 연결 테스트 성공 상태(`isTestConnection=true`)여야 상위 폼 유효
- 인증 테스트 성공 상태(`isTestAuthentication=true`)여야 상위 폼 유효
- `재입력(reenter)` 클릭 시 테스트 성공 상태를 해제하고 필드를 수정할 수 있음

### 섹션 3. LDAP Searching and Updating
필수 항목
- Edit Mode
- Users DN*
- Username LDAP Attribute*
- RDN LDAP Attribute*
- UUID LDAP Attribute*
- User Object Classes*

선택 항목
- User LDAP Filter
- Search Scope (`ONE_LEVEL/SUBTREE`)
- Read Timeout(ms)
- Pagination 토글
- Referral (`disabled/ignore/follow`)

### 섹션 4. Synchronization Settings
- Import Users
- Sync Registrations
- Batch Size
- Periodic Full Sync + Full Sync Period(초)
- Periodic Changed Users Sync + Changed Users Sync Period(초)
- 주기 토글을 끄면 Period 값은 `-1`로 저장

### 섹션 5. Advanced Settings
- LDAPv3 Password Modify
- Validate Password Policy
- Trust Email
- Connection Trace

## LDAP Provider 상세



### 상세 영역
- General Options
- Connection and Authentication Settings
- LDAP Searching and Updating
- Synchronization Settings
- Advanced Settings

### 표시 포맷
- LDAP boolean 문자열(`'true'/'false'`)은 `ON/OFF`로 표시
- Sync period가 `-1`이면 `OFF`로 표시

## LDAP Mapper

### Mapper 목록
- 위치: Provider 상세 하단
- 페이지 크기: `5` (로컬 페이지네이션)
- 컬럼
  - 이름(상세 이동)
  - ID
  - User Model Attribute
  - LDAP Attribute
  - Attribute Default Value
- 액션: 생성/편집/삭제

### Mapper 생성, 편집, 상세

### Mapper 입력 항목
- 이름(고정값, 비활성)
- Mapper Type(고정값, 비활성)
- User Model Attribute(`mobileNumber/username/email`)
- LDAP Attribute
- Read Only 토글
- Always Read Value From LDAP 토글
- Is Mandatory In LDAP 토글
- Attribute Default Value
- Force Default Value 토글
- Is Binary Attribute 토글

### 저장 조건
- 편집 모드는 기존 값 대비 변경사항이 있을 때만 저장 가능합니다.
