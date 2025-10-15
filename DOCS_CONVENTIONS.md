# 문서 컨벤션 가이드 (Markdown)

이 문서는 저장소 내 모든 Markdown(.md) 문서에 적용되는 작성 규칙을 정의합니다.

---

## 1) 폴더 구조

- 공용 이미지: `/assets/img`
- 모듈별: `/docs/{module}/{module}.md`
- 템플릿: `/docs/_templates/`
---

## 2) 파일명 & 제목

- 파일명: `모듈.md` (예: `대시보드.md`, `물리머신.md`)
- 문서의 최상단 제목 H1은 파일명과 의미가 일치하도록 작성
- 문서당 H1은 **한 번만** 사용

```
# 대시보드
```

---

## 3) 제목(Heading) 규칙

- 깊이: H1(`#`) → H2(`##`) → H3(`###`) → H4(`####`)
- 단계 건너뛰기 금지(H2 다음 H4 바로 사용 X)

예)
```
## 개요
### 배경
### 범위
## 설정
### 사전 준비
### 절차
```

---

## 5) 문체 & 용어

- 존댓말, 짧고 명확한 문장
- UI 라벨은 굵게(**예: 저장**)로 표기
- 고유명/모듈명 일관 사용 (예: 제품명 **CloudiA**)
- 금지: 팀 내부 약어, 구현/코드 세부사항 과다 노출

---

## 6) 링크

- **상대 경로** 원칙 (레포 외부 링크 X)
- 문장 중 링크는 자연스럽게:  
  `자세한 내용은 [접근관리](../접근관리/역할.md)를 참고하세요.`

---

## 7) 이미지 캡처 

- chrome custom device 추가 (1440x900) 
- chrome extension 'FireShot' 추가
  - https://chromewebstore.google.com/detail/take-webpage-screenshots/mcbpblocgmgfnpjjppndjkmgjaogfceg 
- Web debug tool > Toggle device toolbar 클릭 및 custom device로 변경 
- 원하는 페이지에서 FireShot 실행 > 현재 화면 캡처 
- Git Repo `/docs/assets/img/{Module}/파일명.확장자` 업로드 

---

## 8) 이미지 삽입

- 경로: `/assets/img/{module}/파일명.확장자`
- 구문:

```md
![역할_목록_화면_예시)](../assets/img/접근관리/역할리스트.png)
```
![역할_목록_화면_예시)](../assets/img/접근관리/역할리스트.png)

---

## 9) 표

```md
| 항목 | 설명 | 필수 |
|---|---|---|
| 이름 | 역할 표시명 | 예 |
```

## 10) 리스트 & 절차

- 절차는 번호 리스트 사용
- 각 단계는 **행동 동사**로 시작

```md
1. **편집**을 클릭합니다.
2. SMTP 정보를 입력합니다.
3. **저장**을 눌러 적용합니다.
```

---

## 11) 템플릿

`/docs/_templates/guide-template.md` 예시:

```md
# {문서 제목}

## 개요
- 목적 
- 선행 조건

## 빠른 시작
1.
2.
3.

## 상세 절차
### 단계 1
### 단계 2[guide-template.md](docs/_templates/guide-template.md)

## 변경 이력
- 2025-10-14: 최초 작성
```
