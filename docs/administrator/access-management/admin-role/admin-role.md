# 관리자 역할

## 관리자 역할 목록

### 테이블 컬럼
| 컬럼 | 설명 |
|---|---|
| 이름 | 클릭 시 관리자 역할 상세 화면으로 이동합니다. |
| 연결된 권한 수 | 연결된 관리자 권한 개수를 표시합니다. |
| 연결된 멤버 수 | 해당 역할이 부여된 관리자 멤버 수를 표시합니다. |
| 설명 | 역할 설명을 표시합니다. |
| 생성일 | 생성 일시를 표시합니다. |

### 검색
- 검색 필드: `이름(roleName)`

### 상단 액션
- 생성, 편집, 삭제

### 제약
- 시스템 관리자 역할(`system=true`)은 편집/삭제할 수 없습니다.

## 관리자 역할 생성/편집

### 경로 및 권한
- 생성: `/administrator/access-management/admin-role/create` (`adminrole-edit`)
- 편집: `/administrator/access-management/admin-role/update?id={roleId}` (`adminrole-edit`)

### 동작
- 일반 역할 생성/편집 구조와 동일합니다.
- 생성 모드에서는 권한 선택 모달에서 `ADMIN` 타입 권한만 선택할 수 있습니다.
- 편집 모드에서는 이름/설명만 변경할 수 있습니다.

### 제약
- 시스템 관리자 역할은 편집 화면 진입이 차단됩니다.

## 관리자 역할 상세
- URL: `/administrator/access-management/admin-role/detail?id={roleId}`
- 라우트 권한: `adminrole-view`

### 상세 정보
- 이름, ID, 연결 권한 수, 연결 멤버 수, 설명, 생성일, 수정일

### 하단 탭
- 권한 탭: 관리자 권한 리스트 + 편집 버튼
- 멤버 탭: 관리자 역할 연결 멤버 리스트

## 관리자 역할 권한 편집

### 경로 및 권한
- URL: `/administrator/access-management/admin-role/permission-update?id={roleId}`
- 라우트 권한: `adminrole-edit`

### 주요 동작
- 권한 추가/삭제/저장 흐름은 일반 역할과 동일합니다.
- 실제 화면은 `RolePermissionUpdate` 공용 컴포넌트를 사용합니다.
- 데이터 소스만 관리자 역할 API를 사용합니다.


