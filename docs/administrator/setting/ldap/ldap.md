# 사용자 연동

## LDAP Provider 목록

### 주요 작업
- `생성`: 새 LDAP Provider를 등록합니다.
- `편집`: 선택한 Provider를 수정합니다. 한 건을 선택했을 때만 사용할 수 있습니다.
- `삭제`: 선택한 Provider를 삭제합니다. 한 건을 선택했을 때만 사용할 수 있습니다.
- `활성화`: 선택한 Provider가 `inactive(false)` 상태일 때 사용할 수 있습니다.
- `비활성화`: 선택한 Provider가 `active(true)` 상태일 때 사용할 수 있습니다.
- `더보기 > 모든 사용자 동기화`: 선택한 Provider의 전체 사용자 동기화를 실행합니다.
- `더보기 > 변경된 사용자 동기화`: 선택한 Provider의 변경 사용자만 동기화합니다.
- `더보기 > 연동 해제`: 선택한 Provider의 LDAP 연동을 해제합니다.
- `더보기 > 가져온 사용자 삭제`: 해당 Provider를 통해 가져온 사용자를 삭제합니다.

### 테이블 컬럼
| 컬럼 | 설명 |
|---|---|
| 이름 | 클릭하면 LDAP Provider 상세 화면으로 이동합니다. |
| ID | Provider 식별자를 표시합니다. |
| 활성화 상태 | 현재 활성화 여부를 표시합니다. |
| 연결 URL | LDAP 서버 연결 URL을 표시합니다. |

### 사용 시 참고
- 목록은 로컬 페이지네이션으로 `10`건씩 표시됩니다.
- 목록은 한 번에 한 건만 선택할 수 있습니다.
- `더보기` 메뉴는 Provider를 한 건 선택했을 때만 활성화됩니다.
- 삭제 확인 모달 제목은 `사용자 연동 삭제`입니다.
- 동기화, 연동 해제, 가져온 사용자 삭제 실행 모달 제목은 `사용자 연동`이며 확인 버튼 라벨은 `실행`입니다.

## LDAP Provider 생성/편집

### 접근 경로 및 권한
- 생성 경로: `/administrator/setting/ldap/create`
- 편집 경로: `/administrator/setting/ldap/update?prdid={providerId}`
- 필요 권한: `userfederation-edit`

### General Options
- 이름: 필수 입력이며 최대 `20`자까지 입력할 수 있습니다.
- Vendor: 필수 선택 항목이며 `ad`, `other` 중 하나를 선택합니다.

### Connection Settings
- Connection URL
- Enable StartTLS
- Use Truststore SPI: `always`, `never`
- Connection Pooling
- Connection Timeout(ms)
- 연결 테스트 버튼: `testConnection`, 성공 후 `reenter`

### Authentication Settings
- Bind Type: `simple`, `none`
- Bind DN
- Bind Credentials
- 인증 테스트 버튼: `testAuthentication`, 성공 후 `reenter`

### LDAP Searching and Updating
- Edit Mode
- Users DN
- Username LDAP Attribute
- RDN LDAP Attribute
- UUID LDAP Attribute
- User Object Classes
- User LDAP Filter
- Search Scope: `ONE_LEVEL`, `SUBTREE`
- Read Timeout(ms)
- Pagination: `enabled`, `disabled`
- Referral: `disabled`, `ignore`, `follow`

### Synchronization Settings
- Import Users
- Sync Registrations
- Batch Size
- Periodic Full Sync
- Full Sync Period(초)
- Periodic Changed Users Sync
- Changed Users Sync Period(초)

### Advanced Settings
- LDAPv3 Password Modify
- Validate Password Policy
- Trust Email
- Connection Trace

### 저장 조건
- `General Options`가 유효해야 합니다.
- `Connection Settings`가 유효하고 연결 테스트에 성공해야 합니다.
- `Authentication Settings`가 유효하고 인증 테스트에 성공해야 합니다.
- `LDAP Searching and Updating`의 필수 항목이 모두 유효해야 합니다.
- `Synchronization Settings`, `Advanced Settings`는 별도 추가 검증 없이 현재 입력값을 반영합니다.

### 사용 시 참고
- 연결 테스트 성공 상태(`isTestConnection=true`)여야 상위 폼이 유효한 상태로 처리됩니다.
- 인증 테스트 성공 상태(`isTestAuthentication=true`)여야 상위 폼이 유효한 상태로 처리됩니다.
- `reenter`를 클릭하면 테스트 성공 상태가 해제되고 관련 필드를 다시 수정할 수 있습니다.
- 편집 화면은 기존 저장값을 불러온 뒤 연결 테스트와 인증 테스트가 모두 완료된 상태로 시작합니다.
- 주기 토글을 끄면 각 Period 값은 `-1`로 저장됩니다.

## LDAP Provider 상세

### 표시 섹션
- General Options
- Connection and Authentication Settings
- LDAP Searching and Updating
- Synchronization Settings
- Advanced Settings

### 표시 규칙
- LDAP boolean 문자열 값인 `'true'`, `'false'`는 화면에서 `ON`, `OFF`로 표시합니다.
- 동기화 주기 값이 `-1`이면 화면에는 `OFF`로 표시합니다.
- Bind Credentials 값도 상세 정보 영역에 그대로 표시됩니다.

## LDAP Mapper 목록

### 주요 작업
- `생성`: 새 LDAP Mapper를 등록합니다.
- `편집`: 선택한 Mapper를 수정합니다.
- `삭제`: 선택한 Mapper를 삭제합니다.

### 테이블 컬럼
| 컬럼 | 설명 |
|---|---|
| 이름 | 클릭하면 Mapper 상세 화면으로 이동합니다. |
| ID | Mapper 식별자를 표시합니다. |
| User Model Attribute | 사용자 모델 속성 이름을 표시합니다. |
| LDAP Attribute | 매핑 대상 LDAP 속성 이름을 표시합니다. |
| Attribute Default Value | 기본값 설정 여부를 표시합니다. |

### 사용 시 참고
- Mapper 목록은 LDAP Provider 상세 화면 하단에 표시됩니다.
- 목록은 로컬 페이지네이션으로 `5`건씩 표시됩니다.
- 목록은 한 번에 한 건만 선택할 수 있습니다.

## LDAP Mapper 생성/편집/상세

### 입력 항목
- 이름: 고정값이며 비활성 상태로 표시됩니다.
- Mapper Type: 고정값이며 비활성 상태로 표시됩니다.
- User Model Attribute: `mobileNumber`, `username`, `email`
- LDAP Attribute
- Read Only
- Always Read Value From LDAP
- Is Mandatory In LDAP
- Attribute Default Value
- Force Default Value
- Is Binary Attribute

### 생성 화면 기본값
- 이름: `ldap-telephone-to-mobile`
- Mapper Type: `user-attribute-ldap-mapper`
- User Model Attribute: `mobileNumber`
- LDAP Attribute: `telephoneNumber`
- Attribute Default Value: `0100000000`

### 저장 조건
- 생성 화면은 별도 유효성 검사 없이 저장할 수 있습니다.
- 편집 화면은 기존 값 대비 변경사항이 있을 때만 저장할 수 있습니다.
