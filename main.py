import os
import time
import concurrent.futures
from datetime import datetime
from fastapi import FastAPI, Response, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import yfinance as yf

# DB 관련 임포트
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# AI 라우터 확인
try:
    from app.api import moderator_router
    HAS_MODERATOR = True
except ImportError:
    HAS_MODERATOR = False
    print("Warning: 'app.api.moderator_router' Not Found.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if HAS_MODERATOR:
    app.include_router(moderator_router.router, prefix="/api/v1")

# =========================================================
# 1. 데이터베이스 설정 (SQLite)
# =========================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    password = Column(String)
    nickname = Column(String)
    joined_at = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================
# 2. 인증(Auth) 기능
# =========================================================

class SignupRequest(BaseModel):
    username: str = Field(..., pattern="^[A-Za-z0-9]{4,10}$")
    password: str = Field(..., pattern="^[A-Za-z0-9]{4,10}$")
    nickname: str

class LoginRequest(BaseModel):
    username: str
    password: str

# 아이디 중복 확인 API
@app.get("/api/auth/check-username/{username}")
async def check_username(username: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return {"available": False, "message": "이미 사용 중인 아이디입니다."}
    return {"available": True, "message": "사용 가능한 아이디입니다."}

# 닉네임 중복 확인 API
@app.get("/api/auth/check-nickname/{nickname}")
async def check_nickname(nickname: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.nickname == nickname).first()
    if existing_user:
        return {"available": False, "message": "이미 사용 중인 닉네임입니다."}
    return {"available": True, "message": "사용 가능한 닉네임입니다."}

# 회원가입
@app.post("/api/auth/signup")
async def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == req.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    join_date = datetime.now().strftime("%Y-%m-%d")
    new_user = User(
        username=req.username,
        password=req.password,
        nickname=req.nickname,
        joined_at=join_date
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"✅ 회원가입 성공(DB): ID={req.username}")
    return {"message": "회원가입 성공"}

# 로그인
@app.post("/api/auth/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    
    if not user or user.password != req.password:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 일치하지 않습니다.")
    
    print(f"🔑 로그인 성공(DB): {req.username}")
    
    return {
        "token": f"access-token-{req.username}",
        "nickname": user.nickname,
        "joined_at": user.joined_at
    }

# =========================================================
# 3. 시장 데이터 로직
# =========================================================

class UserRequest(BaseModel):
    user_question: str

MARKET_CACHE = {"data": [], "last_updated": 0}
CACHE_DURATION = 300
SYMBOLS_MAP = {
    "S&P 500": {"symbol": "^GSPC", "icon": "🇺🇸"},
    "NASDAQ": {"symbol": "^IXIC", "icon": "💻"},
    "Nikkei 225": {"symbol": "^N225", "icon": "🇯🇵"},
    "Bitcoin": {"symbol": "BTC-USD", "icon": "🪙"},
    "Gold": {"symbol": "GC=F", "icon": "🥇"},
    "WTI Crude": {"symbol": "CL=F", "icon": "🛢️"},
    "USD/KRW": {"symbol": "KRW=X", "icon": "💵"},
    "Tesla": {"symbol": "TSLA", "icon": "🚗"}
}

def fetch_single_ticker(name, info):
    symbol = info["symbol"]
    icon = info["icon"]
    try:
        ticker = yf.Ticker(symbol)
        try:
            current_price = ticker.fast_info['last_price']
            prev_close = ticker.fast_info['previous_close']
        except:
            hist = ticker.history(period="2d")
            if len(hist) < 2: return None
            current_price = hist["Close"].iloc[-1]
            prev_close = hist["Close"].iloc[-2]

        if not current_price or not prev_close: return None
        
        change_amount = current_price - prev_close
        change_percent = (change_amount / prev_close) * 100
        is_up = change_amount >= 0

        return {
            "name": name,
            "price": f"{current_price:,.2f}",
            "change": f"{'+' if is_up else ''}{change_percent:.2f}%",
            "isUp": is_up,
            "icon": icon
        }
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return None

@app.get("/market-summary")
async def get_market_summary():
    global MARKET_CACHE
    current_time = time.time()
    if current_time - MARKET_CACHE["last_updated"] < CACHE_DURATION and MARKET_CACHE["data"]:
        return MARKET_CACHE["data"]

    market_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_single_ticker, name, info) for name, info in SYMBOLS_MAP.items()]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res: market_data.append(res)
    
    market_data.sort(key=lambda x: list(SYMBOLS_MAP.keys()).index(x['name']))
    if market_data:
        MARKET_CACHE["data"] = market_data
        MARKET_CACHE["last_updated"] = current_time
    return market_data

@app.get("/kospi-data")
async def get_kospi_data():
    try:
        kospi = yf.Ticker("^KS11")
        try:
            current = kospi.fast_info['last_price']
            prev = kospi.fast_info['previous_close']
        except:
            hist = kospi.history(period="2d")
            current = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2]

        change_amt = current - prev
        change_pct = (change_amt / prev) * 100
        is_up = change_amt >= 0

        hist_data = kospi.history(period="1mo")
        dates = [d.strftime("%m-%d") for d in hist_data.index]
        prices = hist_data["Close"].tolist()

        return {
            "price": f"{current:,.2f}",
            "change": f"{'+' if is_up else ''}{change_pct:.2f}%",
            "diff": f"{'+' if is_up else ''}{change_amt:.2f}",
            "isUp": is_up,
            "chart_labels": dates,
            "chart_data": prices
        }
    except Exception as e:
        return {"error": "Load Failed"}

# =========================================================
# 4. 정적 파일 & HTML 경로 설정
# =========================================================

ORIGINAL_FRONTEND_PATH = "infra/frontend"
ORIGINAL_HTML_PATH = "infra/frontend/html"

if os.path.exists("js"):
    app.mount("/js", StaticFiles(directory="js"), name="js_root")
elif os.path.exists(f"{ORIGINAL_FRONTEND_PATH}/js"):
    app.mount("/js", StaticFiles(directory=f"{ORIGINAL_FRONTEND_PATH}/js"), name="js_infra")

if os.path.exists("css"):
    app.mount("/css", StaticFiles(directory="css"), name="css_root")
elif os.path.exists(f"{ORIGINAL_FRONTEND_PATH}/css"):
    app.mount("/css", StaticFiles(directory=f"{ORIGINAL_FRONTEND_PATH}/css"), name="css_infra")

if os.path.exists("img"):
    app.mount("/img", StaticFiles(directory="img"), name="img_root")
elif os.path.exists(f"{ORIGINAL_FRONTEND_PATH}/img"):
    app.mount("/img", StaticFiles(directory=f"{ORIGINAL_FRONTEND_PATH}/img"), name="img_infra")

def get_html_path(filename):
    if os.path.exists(filename): return filename
    infra_path = os.path.join(ORIGINAL_HTML_PATH, filename)
    if os.path.exists(infra_path): return infra_path
    return None

@app.get("/")
async def read_root():
    path = get_html_path("start.html")
    if path: return FileResponse(path)
    return {"error": "start.html not found"}

@app.get("/{filename}.html")
async def read_html(filename: str):
    path = get_html_path(f"{filename}.html")
    if path: return FileResponse(path)
    raise HTTPException(status_code=404, detail="Page not found")

if os.path.exists(ORIGINAL_FRONTEND_PATH):
    app.mount("/", StaticFiles(directory=ORIGINAL_FRONTEND_PATH), name="frontend_fallback")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)