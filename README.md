# TETRIS

브라우저에서 바로 즐기는 테트리스 게임입니다.

**라이브 데모**: https://kangsoo-lee2.github.io/tetris/

---

## 기능

- 테트리스 게임 (키보드 조작)
- 회원가입 / 로그인 (JWT 인증)
- 게임 종료 시 점수 자동 저장
- 리더보드 (상위 10명)

## 조작 방법

| 키 | 동작 |
|---|---|
| `←` `→` | 좌우 이동 |
| `↑` | 회전 |
| `↓` | 빠르게 내리기 |
| `Space` | 즉시 낙하 |
| `P` | 일시정지 |

---

## 로컬 실행

### 1. 게임만 (백엔드 없이)

```bash
python3 -m http.server 8765
```

브라우저에서 `http://localhost:8765/index.html` 접속.  
로그인 없이 게임 가능 (점수 저장 및 리더보드 기능 비활성화).

### 2. 전체 실행 (백엔드 포함)

```bash
bash start.sh
```

| 주소 | 내용 |
|---|---|
| `http://localhost:8765/index.html` | 게임 |
| `http://localhost:8000/docs` | API 문서 (Swagger) |

---

## 기술 스택

| 구분 | 기술 |
|---|---|
| 프론트엔드 | HTML / CSS / JavaScript (단일 파일) |
| 백엔드 | FastAPI, SQLAlchemy, SQLite |
| 인증 | JWT (python-jose) |
| 배포 | GitHub Pages |

## 프로젝트 구조

```
tetris/
├── index.html        # 게임 + UI (프론트엔드 전체)
├── backend/
│   ├── main.py       # API 엔드포인트
│   ├── models.py     # DB 모델 (User, Score)
│   ├── schemas.py    # Pydantic 스키마
│   ├── auth.py       # 인증 유틸
│   └── database.py   # DB 연결
├── requirements.txt  # 파이썬 의존성
├── start.sh          # 서버 시작 스크립트
└── DEPLOY.md         # GitHub Pages 배포 가이드
```

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/register` | 회원가입 |
| POST | `/api/login` | 로그인 (JWT 발급) |
| GET | `/api/me` | 내 정보 |
| POST | `/api/scores` | 점수 저장 |
| GET | `/api/scores/my` | 내 점수 목록 |
| GET | `/api/leaderboard` | 리더보드 (상위 10명) |
