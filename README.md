# 📈 Upstage Stock Multi-Agent Debate System

**Upstage Solar LLM**과 **LangGraph**를 활용한 지능형 가상 주식 투자 분석 플랫폼입니다. 4종의 특화 에이전트가 기술적·기본적·감성적 분석을 수행하며, 토론(Debate) 과정을 통해 최종 투자 전략을 도출합니다.

---

## 🛠 기술 스택

### **AI & Orchestration**
* **LLM**: Upstage Solar LLM (추론 및 대화 핵심 모델)
* **Framework**: LangChain & LangGraph (멀티 에이전트 워크플로우 및 상태 관리)
* **Search**: Tavily / DuckDuckGo API (실시간 뉴스 검색)

### **Data & Backend**
* **Finance Data**: yfinance (실시간 주가 및 재무제표 데이터 확보)
* **Technical Indicators**: Pandas, TA-Lib (이동평균선, RSI, MACD 계산)
* **Documentation**: Swagger UI (FastAPI 기반 API 문서화)

<<<<<<< HEAD
### **Infrastructure & DevOps**
* **Containerization**: Docker (멀티 스테이지 빌드)
* **Orchestration**: Kubernetes (K8s)
* **CI/CD**: GitHub Actions
* **Vector DB**: ChromaDB
* **Web Server**: Nginx Ingress Controller

=======
>>>>>>> origin/develop
### **Environment & Tools**
* **Language**: Python 3.11+
* **Package Manager**: **uv** (초고속 패키지 및 가상환경 관리)
* **Environment**: python-dotenv (API Key 보안 관리)

---

## 📂 프로젝트 구조

`app/` 디렉토리를 중심으로 각 계층의 관심사를 분리한 클린 아키텍처 구조입니다.

```
upstage-stock-agent/
├── .env                # API Key 관리 (Upstage, Tavily, OpenAI 등)
├── .gitignore          # Git 제외 파일 (.env, .venv, __pycache__ 등)
<<<<<<< HEAD
├── .dockerignore       # Docker 빌드 제외 파일
├── pyproject.toml      # uv 패키지 및 프로젝트 의존성 관리
├── Dockerfile          # 멀티 스테이지 Docker 이미지 (Backend, Frontend)
├── docker-compose.yml  # 로컬 Docker 환경 오케스트레이션
├── main.py             # 시스템 실행 진입점 (FastAPI)
│
├── .github/
│   └── workflows/
│       └── deploy.yml  # CI/CD 파이프라인 (자동 빌드/배포)
│
├── app/                # 실제 소스 코드 디렉토리
│   ├── agents/         # 각 에이전트의 페르소나 및 프롬프트 로직 정의
│   │   ├── news_agent.py      # 뉴스/감성 분석 에이전트
│   │   ├── finance_agent.py   # 재무제표/펀더멘탈 분석 에이전트
│   │   ├── chart_agent.py     # 차트/기술적 분석 에이전트
│   │   └── moderator_agent.py # 사회자 및 최종 전략가
│   │
│   ├── tools/          # 에이전트가 데이터 수집 시 사용하는 도구들
│   │   ├── search_tools.py    # 뉴스 검색 (Tavily/DuckDuckGo)
│   │   ├── finace_tools.py    # 주가 및 재무 정보 수집 (yfinance)
│   │   └── chart_tools.py     # 기술적 지표 계산 (TA-Lib/Pandas)
│   │
│   ├── graph/          # LangGraph를 이용한 토론 흐름 제어
│   │   ├── state.py           # 에이전트 간 공유할 상태(State) 정의
│   │   └── workflow.py        # 토론 순서 및 로직 구성 (노드와 엣지)
│   │
│   ├── api/            # FastAPI 라우터
│   ├── core/           # 설정, DB 연결, 로거
│   ├── models/         # 데이터 스키마 (Pydantic)
│   ├── repository/     # 외부 API 클라이언트 및 DB 접근
│   ├── service/        # 비즈니스 로직
│   └── utils/          # 공통 유틸리티
│
├── infra/              # 인프라 설정 파일
│   ├── frontend/       # Streamlit UI 코드
│   │   └── ui.py
│   └── k8s/            # Kubernetes 배포 매니페스트
│       └── application/
│           ├── 01-namespace.yaml
│           ├── 02-configmap.yaml
│           ├── 03-chromadb.yaml
│           ├── 04-backend.yaml
│           ├── 05-frontend.yaml
│           └── 06-ingress.yaml
│
├── notebooks/          # 자유로운 실험 공간 (Jupyter Notebooks)
│
├── start.sh            # 로컬 환경 일괄 실행 스크립트
├── stop.sh             # 로컬 개발 서버 중지 스크립트
├── start_docker.sh     # Docker 컨테이너 실행 스크립트
└── stop_docker.sh      # Docker 컨테이너 중지 스크립트
```

---

=======
├── pyproject.toml      # uv 패키지 및 프로젝트 의존성 관리
├── main.py             # 시스템 실행 진입점 (FastAPI 또는 CLI 실행)
└── app/                # 실제 소스 코드 디렉토리
    ├── agents/         # 각 에이전트의 페르소나 및 프롬프트 로직 정의
    │   ├── __init__.py
    │   ├── news_agent.py      # 뉴스/감성 분석 에이전트
    │   ├── finance_agent.py   # 재무제표/펀더멘탈 분석 에이전트
    │   ├── chart_agent.py     # 차트/기술적 분석 에이전트
    │   └── moderator_agent.py # 사회자 및 최종 전략가 (주혁님 설계안 반영)
    ├── tools/          # 에이전트가 데이터 수집 시 사용하는 도구들
    │   ├── __init__.py
    │   ├── search_tools.py    # 뉴스 검색 (Tavily/DuckDuckGo)
    │   ├── finance_tools.py   # 주가 및 재무 정보 수집 (yfinance)
    │   └── chart_tools.py     # 기술적 지표 계산 (TA-Lib/Pandas)
    ├── graph/          # LangGraph를 이용한 토론 흐름 제어
    │   ├── __init__.py
    │   ├── state.py           # 에이전트 간 공유할 상태(State) 정의
    │   └── workflow.py        # 토론 순서 및 로직 구성 (노드와 엣지)
    └── utils/          # 공통 유틸리티
        ├── __init__.py
        └── llm.py             # LLM 모델(Solar 등) 초기화 및 설정
```

>>>>>>> origin/develop
## 🧠 프로젝트 아키텍처: 4-Agent 토론 시스템

본 프로젝트는 각 분야에 특화된 에이전트들이 독립적으로 분석하고, 상호 검증(Debate) 과정을 통해 객관적인 투자 전략을 도출하도록 설계되었습니다.

### **1. 에이전트 역할 (Roles)**

| 에이전트 | 역할 요약 | 핵심 분석 범위 |
| :--- | :--- | :--- |
| **차트 분석가** | 시장 심리 해석 | 이평선, RSI, MACD, 거래량 기반 단기 심리 분석 |
| **재무 분석가** | 기업 본질 체력 평가 | 매출 성장, 수익성, 부채비율 등 중장기 안정성 평가 |
| **뉴스 감성 분석가** | 외부 리스크 감지 | 실시간 뉴스 감성 분석, 규제 및 리스크 탐지 |
| **사회자/전략가** | **최종 의사결정** | 토론 통제, 분석 일관성 검증 및 최종 투자 판단 |

<<<<<<< HEAD
=======


>>>>>>> origin/develop
### **2. 5단계 분석 프로세스**

1. **개별 분석**: 각 분석 에이전트가 독립적으로 데이터를 수집하고 핵심 근거와 리스크를 도출합니다.
2. **반론 중심 토론**: 사회자의 주도하에 서로의 주장 중 취약한 지점을 지적하고 논리적 허점을 찾는 상호 검증을 진행합니다.
3. **사회자 판정**: 각 주장의 타당성과 반론 대응력을 평가하여 핵심 쟁점을 정리합니다.
4. **최종 투자 판단**: 전략가가 토론 결과를 바탕으로 단기/중기 관점을 조정하여 최종 투자 등급(`BUY/HOLD/SELL`)을 명시합니다.
5. **설명 가능한 결과 제공**: 사용자에게 최종 판단 사유와 주의해야 할 리스크 요약을 함께 제공합니다.

---

## ⚙️ 설치 및 실행 방법

<<<<<<< HEAD
### **사전 준비**

1. API 키 발급
   - [Upstage Console](https://console.upstage.ai/)에서 API 키 발급
   - (Optional) [Serper.dev](https://serper.dev/)에서 검색 API 키 발급

2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어서 발급받은 API 키를 입력하세요
```

### **방법 1: 로컬 환경 실행**

```bash
# 실행
sh start.sh

# 종료
sh stop.sh
```

**접속**:
- Backend API: http://localhost:8001
- API 문서: http://localhost:8001/docs
- Frontend: http://localhost:8002 (구현 완료 시)

### **방법 2: Docker 환경 실행**

```bash
# 실행
sh start_docker.sh

# 종료
sh stop_docker.sh
```

**접속**:
- Backend API: http://localhost:8001
- Frontend: http://localhost:8002
- ChromaDB: http://localhost:8000

### **방법 3: Kubernetes 배포**

#### 배포 전 설정

1. **GitHub Secrets 설정**
   - Repository → Settings → Secrets and variables → Actions
   - 다음 Secrets 추가:
     - `EC2_HOST`: EC2 서버 IP
     - `EC2_SSH_KEY`: EC2 SSH private key

2. **Kubernetes Manifest 수정**
   ```bash
   # 04-backend.yaml, 05-frontend.yaml
   image: ghcr.io/YOUR_GITHUB_USERNAME/stock-agent-backend:latest
   # → YOUR_GITHUB_USERNAME을 실제 GitHub 계정명으로 변경
   
   # 06-ingress.yaml
   host: YOUR_DUCKDNS_DOMAIN.duckdns.org
   # → YOUR_DUCKDNS_DOMAIN을 실제 DuckDNS 도메인으로 변경
   ```

3. **EC2 서버 준비**
   ```bash
   # EC2에 접속
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # 프로젝트 클론
   mkdir -p ~/deploy
   cd ~/deploy
   git clone https://github.com/YOUR_USERNAME/upstage-stock-agent-main.git
   cd upstage-stock-agent-main
   
   # 환경 변수 설정
   cp .env.example .env
   vi .env  # API 키 입력
   
   # Secret 생성
   kubectl create secret generic app-secret \
     --from-env-file=.env \
     -n stock-agent
   
   # 매니페스트 적용
   cd infra/k8s/application
   kubectl apply -f .
   ```

4. **자동 배포**
   ```bash
   # main 브랜치에 Push하면 자동으로 빌드/배포됩니다
   git add .
   git commit -m "Update application"
   git push origin main
   ```

**접속**:
- Frontend: http://your-duckdns-domain.duckdns.org
- Backend API: http://your-duckdns-domain.duckdns.org/agent

---

## 📊 결과물 예시 (Explainable Output)

=======
### **1. 환경 변수 설정**
루트 디렉토리에 `.env` 파일을 생성하고 필요한 API 키를 입력합니다. (보안을 위해 `.gitignore`에 반드시 등록하세요.)

```
UPSTAGE_API_KEY=your_solar_api_key
TAVILY_API_KEY=your_tavily_key
```

### **2. 의존성 설치 (uv)**
본 프로젝트는 초고속 패키지 관리자 uv를 사용합니다.
```
uv sync
```

### **3. 시스템 실행** 
```
# 삼성전자(005930) 종목 분석 실행 예시
uv run main.py --symbol 005930
```

## 📊 결과물 예시 (Explainable Output)
>>>>>>> origin/develop
에이전트 토론 과정을 거쳐 사용자에게 전달되는 최종 리포트 예시입니다.

```
최종 투자 판단: HOLD
- 판단 사유: "단기 기술적 반등 신호는 존재하나, 최근 규제 뉴스 및 재무 건전성 리스크가 충분히 해소되지 않아 관망 전략이 합리적임."
- 핵심 리스크: "중기 추세 하락 가능성 및 외부 정책 변화 주의"
```

<<<<<<< HEAD
---

## 🚀 개발 로드맵

### Phase 1: Infrastructure Setup ✅
- [x] Docker 환경 구축
- [x] Kubernetes Manifest 작성
- [x] CI/CD 파이프라인 구축

### Phase 2: Agent Implementation (진행 중)
- [ ] Chart Agent 구현
- [ ] Finance Agent 구현
- [ ] News Agent 구현
- [ ] Moderator Agent 구현

### Phase 3: Frontend Development (대기 중)
- [ ] Streamlit UI 구현
- [ ] 실시간 스트리밍 채팅
- [ ] 토론 과정 시각화

### Phase 4: Integration & Testing
- [ ] Agent 통합 테스트
- [ ] End-to-End 테스트
- [ ] 성능 최적화

---

## ⚠️ 주의사항

- **API 호출 제한**: 실시간 데이터 수집 시 API 호출 횟수 제한(Rate Limit)에 유의하세요.
- **보안**: `.env` 파일은 절대 GitHub에 올리지 마십시오.
- **투자 책임**: 본 시스템의 분석 결과는 참고용이며, 투자 판단과 그에 따른 결과는 전적으로 사용자 책임입니다.

---

## 📝 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

## 👥 기여자

- DevOps & Infrastructure: [Your Name]
- Agent Development: [Team Member 1]
- Frontend Development: [Team Member 2]

---

## 📞 문의

프로젝트 관련 문의사항은 Issue를 통해 남겨주세요.
=======
## ⚠️ 주의사항
- API 호출 제한: 실시간 데이터 수집 시 API 호출 횟수 제한(Rate Limit)에 유의하세요.
- 보안: .env 파일은 절대 깃허브에 올리지 마십시오.
>>>>>>> origin/develop
