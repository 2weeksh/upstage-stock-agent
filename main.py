import os
import time
import concurrent.futures
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import yfinance as yf
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.core.database import engine, Base
from app.api import auth, chat
import app.models.user

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 터미널에 에러 원인을 빨간색으로 자세히 출력합니다
    print("\n❌ [422 에러 발생] 프론트엔드 데이터가 규격과 다릅니다!")
    print(f"👉 원인: {exc.errors()}\n")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# 1. DB 테이블 생성
Base.metadata.create_all(bind=engine)

# 2. CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 라우터 등록
app.include_router(auth.router)
app.include_router(chat.router, prefix="/api/v1")

# ==========================================
# 시장 데이터 캐싱 및 로직
# ==========================================
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
        print("캐시된 데이터 반환 (Fast Mode)")
        return MARKET_CACHE["data"]

    print("새로운 데이터 수집 시작 (Parallel Mode)...")
    market_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_single_ticker, name, info) for name, info in SYMBOLS_MAP.items()]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                market_data.append(result)

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
        print(f"KOSPI Error: {e}")
        return {"error": "Load Failed"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "stock-agent-backend"}

@app.get("/")
async def read_index():
    path = "infra/frontend/html/start.html"
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "start.html not found"}


@app.get("/userInput.html")
async def user_input_page():
    return FileResponse("infra/frontend/html/userInput.html")


@app.get("/loading.html")
async def loading_page():
    return FileResponse("infra/frontend/html/loading.html")


@app.get("/analysis.html")
async def analysis_page():
    return FileResponse("infra/frontend/html/analysis.html")


@app.get("/login.html")
async def login_page():
    return FileResponse("infra/frontend/html/login.html")

@app.get("/mypage.html")
async def mypage_page():
    return FileResponse("infra/frontend/html/mypage.html")

@app.get("/signup.html")
async def signup_page():
    return FileResponse("infra/frontend/html/signup.html")

@app.get("/history.html")
async def history_page():
    return FileResponse("infra/frontend/html/history.html")

frontend_path = "infra/frontend"
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path), name="frontend")