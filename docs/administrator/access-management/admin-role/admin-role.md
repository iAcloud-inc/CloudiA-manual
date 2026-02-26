# 관리자 역할

## 관리자 역할 목록
관리자 역할 목록에서는 관리자 권한 체계에 사용되는 역할을 조회하고 관리할 수 있습니다.

- URL: `/administrator/access-management/admin-role`
- 단일 선택 목록, 페이지 크기 `10`, 기본 정렬 `createdAt desc`
- 주요 작업: `생성`, `편집`, `삭제`
- 검색 필드: `이름(roleName)`

> ⚠️ 시스템 관리자 역할(`system=true`)은 편집/삭제할 수 없습니다.

## 관리자 역할 생성/편집
관리자 역할 생성/편집 화면에서 이름과 설명을 관리합니다.

- 생성 URL: `/administrator/access-management/admin-role/create`
- 편집 URL: `/administrator/access-management/admin-role/update?id={roleId}`
- 생성 시에는 `ADMIN` 타입 권한만 선택할 수 있습니다.
- 편집 모드에서는 이름/설명만 변경합니다.

## 관리자 역할 상세/권한 편집
상세 화면에서 역할 기본 정보와 연결 데이터를 확인하고 권한을 수정할 수 있습니다.

- 상세 URL: `/administrator/access-management/admin-role/detail?id={roleId}`
- 권한 편집 URL: `/administrator/access-management/admin-role/permission-update?id={roleId}`
- 권한 탭: 연결된 관리자 권한 목록 + 편집
- 멤버 탭: 해당 관리자 역할이 연결된 멤버 목록
