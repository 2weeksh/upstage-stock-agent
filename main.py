from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import moderator_router
import os

app = FastAPI()

# API 라우터 등록
app.include_router(moderator_router.router, prefix="/api/v1")

# 프론트엔드 연결
frontend_path = "infra/frontend"
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")