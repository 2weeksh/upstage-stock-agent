# ======================================================================
# Builder Stage - 의존성 설치를 위한 임시 공간
# ======================================================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# 필수 빌드 도구 및 uv 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libffi-dev && \
    pip install --no-cache-dir uv && \
    rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY pyproject.toml ./
RUN uv sync --no-dev --no-cache || echo "No pyproject.toml or dependencies to install"

# 전체 코드 복사
COPY . .

# ======================================================================
# Backend Runtime Stage - FastAPI 서버
# ======================================================================
FROM python:3.12-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 보안을 위한 비root 사용자 생성
RUN useradd -m appuser

# 빌더에서 가상환경 복사 (있는 경우에만)
COPY --from=builder /app/.venv /app/.venv

# 백엔드 코드 복사
COPY --from=builder /app/main.py /app/main.py
COPY --from=builder /app/app /app/app
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# 파일 소유권 변경
RUN chown -R appuser:appuser /app

# 가상환경 경로 설정
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

USER appuser

EXPOSE 8001

# FastAPI 서버 실행
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

# ======================================================================
