# fastapi-db-19

FastAPI + SQLAlchemy + PostgreSQL(Supabase) 로 회원 CRUD API 를 만드는 수업 실습 (2026-11-16).
강사 저장소 https://github.com/himzei/fastapi-db-19 (`master`) 를 받아서, 아래 두 가지를 바꿨다.

- DB 주소를 코드에서 빼서 `.env` 의 `DATABASE_URL` 로 읽음. 값이 없으면 `local.db`(SQLite)로 동작
- 없는 회원 조회·수정 시 500 이 나던 버그 수정: `return HTTPException(..., deatal=)` → `raise HTTPException(..., detail=)`

## 수업 흐름

강사 설명 기준이다. 아직 진행하지 않은 회차의 세부 내용은 예상이다.

| 날짜 | 주제 | 내용 |
| --- | --- | --- |
| 2026-11-16 (결석) | DB 기초 | Supabase PostgreSQL 연결, SQLAlchemy 로 회원 CRUD (C·R·U 완료, D 미완) |
| **2026-11-17 (오늘)** | **DELETE → 회원가입·로그인** | 먼저 DELETE 로 CRUD 완성. 이어서 강사가 "가장 어려운 부분"이라고 한 회원가입·로그인 (예전에는 직접 만들기 정말 어려웠다고 함) |
| 다음 주 | Next.js | 프론트엔드 프레임워크 |
| 마지막 수업 | Next.js + DB | Next.js 와 DB 를 결합 |

### 오늘(회원가입·로그인) 예상 내용

지금 `users` 테이블에는 username·email 만 있고 비밀번호가 없다. 로그인을 만들려면 대략 아래가 필요하다.

1. **회원가입**: 비밀번호를 받아 **그대로 저장하지 않고 해시(암호화)** 해서 저장 (예: `bcrypt`, `passlib`)
2. **로그인**: 입력한 비밀번호를 해시와 비교 → 맞으면 **토큰(JWT)** 이나 세션 발급
3. **로그인한 사용자만 쓰는 API**: 요청 헤더의 토큰을 확인 (`Depends` 로 현재 사용자 가져오기)

"옛날에는 어려웠다"는 말로 보면, 이 과정을 대신 처리해 주는 **Supabase Auth**(회원가입·로그인·이메일 인증·소셜 로그인 기본 제공)를 쓸 가능성도 있다.
다음 주 Next.js 수업과 이어지려면 Supabase Auth 쪽이 자연스럽다.

## 실행

```bash
uv sync                              # 처음 한 번 (패키지 설치)
uv run uvicorn main:app --reload     # 서버 실행, 끄기는 Ctrl+C
```

- http://127.0.0.1:8000/docs 에서 테스트 (Try it out → Execute → **Server response** 확인)
- `.env` 를 바꾸면 서버를 껐다 켜야 반영된다

## DB 연결 (.env)

`.env.example` 을 복사해 `.env` 를 만들고 Supabase 주소를 넣는다.
Supabase → **Connect → Direct → Session pooler** (5432 포트, URI 형식).

```
DATABASE_URL=postgresql://postgres.<프로젝트ref>:<비밀번호>@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres
```

`.env` 와 `*.db` 는 `.gitignore` 에 있어 git 에 올라가지 않는다.

## API

| CRUD | 메서드·경로 | 설명 |
| --- | --- | --- |
| C | `POST /users` | 회원 추가 `{"username": "...", "email": "..."}` |
| R | `GET /users` | 전체 회원 목록 |
| R | `GET /users/{user_id}` | 회원 한 명 (없으면 404) |
| U | `PUT /users/{user_id}` | 회원 정보 수정 (없으면 404) |
| D | `DELETE /users/{user_id}` | 아직 없음 (2026-11-17 수업에서 진행) |

## 코드 구조 (main.py)

1. `create_engine(DATABASE_URL)` — DB 연결
2. `class User(Base)` — `users` 테이블 (id, username[unique], email)
3. `class UserCreate(BaseModel)` — 요청 본문 검증용 스키마
4. `Base.metadata.create_all()` — 테이블이 없으면 생성
5. `get_db()` + `Depends` — 요청마다 세션을 열고 닫음

## 강사 저장소 업데이트 받기

```bash
git fetch
git log HEAD..origin/master     # 새 커밋 확인
git stash && git pull --ff-only && git stash pop
```

## 알려진 문제

- 이미 있는 `username` 으로 가입하면 500 (`IntegrityError`). `db.rollback()` 후 400 으로 처리하면 된다.
