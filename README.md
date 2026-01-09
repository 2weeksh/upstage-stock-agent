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

### **Environment & Tools**
* **Language**: Python 3.11+
* **Package Manager**: **uv** (초고속 패키지 및 가상환경 관리)
* **Environment**: python-dotenv (API Key 보안 관리)

---

## 📂 프로젝트 구조

`src/` 디렉토리를 중심으로 각 계층의 관심사를 분리한 클린 아키텍처 구조입니다.

```
upstage-stock-agent/
├── .env                # API Key 관리 (Upstage, Tavily 등) - gitignore 필수
├── .env.example        # 환경변수 설정 템플릿
├── pyproject.toml      # uv 패키지 관리 설정
├── main.py             # 시스템 실행 진입점
└── src/
    ├── agents/         # 에이전트 페르소나 및 프롬프트 정의
    │   ├── chart_agent.py      # 차트 분석가 (Technical)
    │   ├── finance_agent.py    # 재무 분석가 (Fundamental)
    │   └── news_agent.py       # 뉴스/감성 분석가 (Sentiment)
    ├── tools/          # 에이전트 전용 도구 (Data Provider)
    │   ├── chart_tools.py      # 주가 지표 추출
    │   ├── finance_tools.py    # 재무 데이터 추출
    │   └── search_tools.py     # 실시간 뉴스 검색
    ├── graph/          # 토론 흐름 제어 로직
    │   ├── state.py            # 에이전트 간 공유 상태(State) 정의
    │   └── workflow.py         # LangGraph 노드 및 엣지 구성
    └── utils/
        └── llm.py              # Solar/GPT 모델 초기화 설정
```

## 🧠 프로젝트 아키텍처: 4-Agent 토론 시스템

본 프로젝트는 각 분야에 특화된 에이전트들이 독립적으로 분석하고, 상호 검증(Debate) 과정을 통해 객관적인 투자 전략을 도출하도록 설계되었습니다.

### **1. 에이전트 역할 (Roles)**

| 에이전트 | 역할 요약 | 핵심 분석 범위 |
| :--- | :--- | :--- |
| **차트 분석가** | 시장 심리 해석 | 이평선, RSI, MACD, 거래량 기반 단기 심리 분석 |
| **재무 분석가** | 기업 본질 체력 평가 | 매출 성장, 수익성, 부채비율 등 중장기 안정성 평가 |
| **뉴스 감성 분석가** | 외부 리스크 감지 | 실시간 뉴스 감성 분석, 규제 및 리스크 탐지 |
| **사회자/전략가** | **최종 의사결정** | 토론 통제, 분석 일관성 검증 및 최종 투자 판단 |



### **2. 5단계 분석 프로세스**

1. **개별 분석**: 각 분석 에이전트가 독립적으로 데이터를 수집하고 핵심 근거와 리스크를 도출합니다.
2. **반론 중심 토론**: 사회자의 주도하에 서로의 주장 중 취약한 지점을 지적하고 논리적 허점을 찾는 상호 검증을 진행합니다.
3. **사회자 판정**: 각 주장의 타당성과 반론 대응력을 평가하여 핵심 쟁점을 정리합니다.
4. **최종 투자 판단**: 전략가가 토론 결과를 바탕으로 단기/중기 관점을 조정하여 최종 투자 등급(`BUY/HOLD/SELL`)을 명시합니다.
5. **설명 가능한 결과 제공**: 사용자에게 최종 판단 사유와 주의해야 할 리스크 요약을 함께 제공합니다.

---

## ⚙️ 설치 및 실행 방법

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
에이전트 토론 과정을 거쳐 사용자에게 전달되는 최종 리포트 예시입니다.

```
최종 투자 판단: HOLD
- 판단 사유: "단기 기술적 반등 신호는 존재하나, 최근 규제 뉴스 및 재무 건전성 리스크가 충분히 해소되지 않아 관망 전략이 합리적임."
- 핵심 리스크: "중기 추세 하락 가능성 및 외부 정책 변화 주의"
```

## ⚠️ 주의사항
- API 호출 제한: 실시간 데이터 수집 시 API 호출 횟수 제한(Rate Limit)에 유의하세요.
- 보안: .env 파일은 절대 깃허브에 올리지 마십시오.
