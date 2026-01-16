FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir \
    fastapi uvicorn python-dotenv yfinance \
    langchain langchain-upstage langchain-community \
    tavily-python pandas sqlalchemy passlib \
    python-jose python-multipart bcrypt \
    finance-datareader chromadb argon2-cffi
COPY . .
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
