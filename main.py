from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
import os

# .env 파일에서 DATABASE_URL 을 읽는다 (비밀번호를 코드에 쓰지 않기 위해)
load_dotenv(Path(__file__).parent / ".env")

# .env 에 주소가 없으면 내 PC의 local.db 파일(SQLite)을 사용 — 연습용
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./local.db"

if DATABASE_URL.startswith("sqlite"):
    # SQLite 는 기본적으로 한 스레드에서만 쓸 수 있어서 FastAPI 용으로 옵션 추가
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
Base = declarative_base()

# 테이블 모델(테이블 이름을 users)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(120))

class UserCreate(BaseModel):
    username: str
    email: str

# 테이블이 없으면 생성
Base.metadata.create_all(bind=engine)

# 요청마다 세션을 열고, 끝나면 닫는 함수
def get_db():
    db = Session(bind=engine)
    try: 
        yield db
    finally:
        db.close()

app = FastAPI()

# C:Create 회원가입
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "ok": "true",
        "id": new_user.id, 
        "username": new_user.username,
        "email": new_user.email
    }

# R:Read 가입한 정보 불러오기(전체조회)
@app.get("/users")
def read_users(db: Session=Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id, 
            "username": user.username, 
            "email": user.email
        } for user in users
    ]

# R:Read 하나 조회
@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None: 
        raise HTTPException(status_code=404, detail="사용자가 없습니다.")
    return {
        "id": user.id, 
        "username" : user.username, 
        "email": user.email
    }

# U:Update => 수정
@app.put("/users/{user_id}")
def update_user(user_id: int, data: UserCreate,  db: Session=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None: 
        raise HTTPException(status_code=404, detail="사용자가 없습니다.")

    user.username = data.username
    user.email = data.email
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username, 
        "email": user.email
    }
    
# D:Delete => 삭제
@app.delete("/users/{user_id}")
def delete_user(user_id:int, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="사용자가 없습니다.")

    db.delete(user)
    db.commit()

    return {
        "ok": True,
        "deleted_id": user_id
    }


@app.get("/")
def read_home():
    return {
        "hello" : "world"
    }