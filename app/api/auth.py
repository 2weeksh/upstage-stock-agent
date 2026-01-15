# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.utils.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# [수정 1] 이메일(email) 필드 삭제
class UserSignup(BaseModel):
    username: str
    password: str
    nickname: str
    # email: str  <-- 이거 지웠습니다!


class UserLogin(BaseModel):
    username: str
    password: str


# ... (중복 확인 API들은 그대로 두세요) ...
# app/api/auth.py 의 check_username, check_nickname 수정

@router.get("/check-username/{username}")
def check_username(username: str, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.username == username).first()
    if exists:
        # 이미 있으면 available: False
        return {"message": "이미 존재하는 아이디입니다.", "available": False}
    # 없으면 available: True
    return {"message": "사용 가능한 아이디입니다.", "available": True}

@router.get("/check-nickname/{nickname}")
def check_nickname(nickname: str, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.nickname == nickname).first()
    if exists:
        return {"message": "이미 존재하는 닉네임입니다.", "available": False}
    return {"message": "사용 가능한 닉네임입니다.", "available": True}

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    # [수정 2] 이메일 중복 체크 로직 삭제
    # (이메일을 안 받으니 체크할 필요도 없죠)

    # 아이디 중복 체크
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="이미 등록된 아이디입니다.")

    new_user = User(
        username=user.username,
        # [수정 3] 이메일 없이 저장 (혹은 빈 문자열로 저장)
        email=None,
        hashed_password=get_password_hash(user.password),
        nickname=user.nickname
    )
    db.add(new_user)
    db.commit()
    return {"message": "회원가입이 완료되었습니다."}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="아이디 또는 비밀번호 오류")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="아이디 또는 비밀번호 오류")

    # 토큰에는 식별자로 username을 넣습니다.
    access_token = create_access_token(data={"sub": db_user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "nickname": db_user.nickname,
        "created_at": str(db_user.created_at).split(" ")[0]  # 👈 [추가] 가입일 (YYYY-MM-DD)
    }