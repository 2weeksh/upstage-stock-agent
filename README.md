# [StockWars] (Upstage Stock Multi-Agent Debate System)

**Upstage Solar LLM**을 활용한 지능형 가상 주식 투자 분석 플랫폼입니다. 3종의 특화 에이전트가 뉴스, 차트, 재무 분석을 수행하며, 토론(Debate) 과정을 통해 최종 투자 전략을 도출합니다.

## 사이트 링크
![](http://stockwars.duckdns.org:30080/)

## 팀원 소개

| 이름 | 역할 | GitHub |
|------|------|--------|
| 송민서 | Frontend | [@thdalseo](https://github.com/thdalseo) |
| 우서윤 | DevOps | [@gaejarae](https://github.com/gaejarae) |
| 이주혁 | AI Engineer | [@2weeksh](https://github.com/2weeksh) |
| 이현종 | Backend | [@leehyunjong12](https://github.com/leehyunjong12) |
| 정성우 | Engineer | [@Jeongseongwoo08](https://github.com/Jeongseongwoo08) |

## 프로젝트 개요

본 프로젝트는 단일 LLM 모델이 가질 수 있는 **확증 편향(Confirmation Bias)**과 정보의 단편성을 극복하기 위해 설계된 멀티 에이전트 기반 주식 분석 플랫폼입니다.

기존의 분석 도구들이 단순히 지표를 요약하는 수준에 머물렀다면, 본 시스템은 뉴스, 재무, 차트 분야의 가상 전문가들이 서로의 논리적 허점을 찌르는 '원형 토론(Round-table Debate)' 과정을 거칩니다. 이를 통해 시장의 광기(고평가)나 공포(저평가) 속에서 데이터에 기반한 냉철하고 객관적인 투자 등급을 도출합니다.

### 주요 기능

- 1. 전문가 에이전트 그룹 (Specialist Agents):
  - 뉴스 분석가 (News Agent): Tavily Search API를 활용해 실시간 시장 심리(Sentiment)와 최신 트렌드 분석.
  - 재무 분석가 (Finance Agent): yfinance 데이터를 바탕으로 PER, PBR 등 기업의 본질적 내재 가치(Valuation) 평가.
  - 차트 분석가 (Chart Agent):RSI, 이동평균선 등 기술적 지표를 통해 최적의 매수/매도 타이밍 포착
- 2. 에이전틱 토론 워크플로우 (Agentic Workflow):
  - 사회자 (Moderator): 토론 맥락을 실시간으로 추론(Reasoning)하여 다음 발언자를 지목하고 구체적인 반박 질문(Instruction)을 하달하는 동적 라우팅 수행.
  - 최종 판결 시스템 (Judge Agent): 치열한 토론 로그를 종합하여 0.0~10.0점 척도의 점수와 5단계 투자 등급 산출.
- 3. 설명 가능한 투자 리포트 (XAI Report):
  - 단순 결과(매수/매도)만 제공하는 것이 아니라, 토론 과정에서 도출된 **'핵심 승리 논리'**와 **'잠재적 리스크'**를 포함한 리포트 자동 생성. 

## 기술 스택

### Backend
- Python 3.11+
- FastAPI

### Frontend
- HTML
- JS / CSS

### AI/ML
- Upstage Solar LLM
- LangChain

### Infrastructure 
- Docker
- Kubernetes
- GitHub Actions
- Nginx Ingress Controller

## Data
- Finance/Chart Data: yfinance
- News Date: Tavily

## 프로젝트 구조

`app/` 디렉토리를 중심으로 각 계층의 관심사를 분리한 클린 아키텍처 구조입니다.

```
upstage-stock-agent/
├── .env                # API Key 관리 (Upstage, Tavily, OpenAI 등)
├── .gitignore          # Git 제외 파일 (.env, .venv, __pycache__ 등)
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
│   │   ├── judge_agnet.py     # 최종 투자 판단 에이전트 
│   │   ├── moderator_agnet.py # 토론 사회자 에이전트
│   │   ├── report_agent.py    # 토론 리포트 작성 에이전트
│   │   ├── ticker_agent.py    # 종목 티커 매팅 에이전트
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
│   │   └──stock_service.py #
│   └── utils/          # 공통 유틸리티
│
├── infra/              # 인프라 설정 파일
│   ├── frontend/       # Streamlit UI 코드
│   │   ├── css/
│   │   ├── html/
│   │   ├── img/
│   │   ├── js/
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

## 아키텍처

본 프로젝트는 각 분야에 특화된 에이전트들이 독립적으로 분석하고, 상호 검증(Debate) 과정을 통해 객관적인 투자 전략을 도출하도록 설계되었습니다.

![단락 텍스트 (2)](https://github.com/user-attachments/assets/2eba4d5b-3816-4440-ace3-3ee77d132223)


### 1. 에이전트 역할 (Roles)

| 에이전트 | 역할 요약 | 핵심 분석 범위 |
| :--- | :--- | :--- |
| **차트 분석가** | 시장 심리 해석 | 이평선, RSI, MACD, 거래량 기반 단기 심리 분석 |
| **재무 분석가** | 기업 본질 체력 평가 | 매출 성장, 수익성, 부채비율 등 중장기 안정성 평가 |
| **뉴스 감성 분석가** | 외부 리스크 감지 | 실시간 뉴스 감성 분석, 규제 및 리스크 탐지 |
| **사회자/전략가** | **최종 의사결정** | 토론 통제(다음 발언자 선택), 분석 일관성 검증 및 최종 투자 판단 |

### 2. 5단계 분석 프로세스

1. **개별 분석**: 각 분석 에이전트가 독립적으로 데이터를 수집하고 핵심 근거와 리스크를 도출합니다.
2. **반론 중심 토론**: 사회자의 주도하에 서로의 주장 중 취약한 지점을 지적하고 논리적 허점을 찾는 상호 검증을 진행합니다.
3. **사회자 판정**: 각 주장의 타당성과 반론 대응력을 평가하여 토론을 계속할지 다른 주제로 토론을 이어갈지 결정합니다.
4. **최종 투자 판단**: 전략가가 토론 결과를 바탕으로 단기/중기 관점을 조정하여 최종 투자 점수(`0.0~10.0`)을 명시합니다.
5. **설명 가능한 결과 제공**: 사용자에게 최종 판단 사유와 주의해야 할 리스크 요약을 함께 제공합니다.

---

## 설치 및 실행 방법

### 요구사항
- Python 3.11 이상

### 1. 환경 변수 설정
- `.env.example`을 복사하여 `.env` 생성
- `.env` 파일에서 API 키를 실제 값으로 변경

```env
UPSTAGE_API_KEY=up_xxxxxxxxxxxxxxxxx
SERPER_API_KEY=xxxxxxxxxxxxxxxxx
```

### 2. 의존성 설치 (uv)
본 프로젝트는 초고속 패키지 관리자 uv를 사용합니다.
```
uv sync
```

## 결과물 예시 (Explainable Output)

에이전트 토론 과정을 거쳐 사용자에게 전달되는 최종 리포트 예시입니다.

```
### 1. 최종 등급
| 최종 등급 기준표 |
|----------------|
| **8.0 ~ 10.0** | [강력 매수] - 압도적 호재와 상승 모멘텀 |
| **6.0 ~ 7.9**  | [매수] - 전반적 우상향 기대 및 긍정적 지표 |
| **4.0 ~ 5.9**  | **[중립]** - 방향성 불분명, 관망 필요 |
| **2.0 ~ 3.9**  | [매도] - 하방 압력 존재 및 리스크 관리 필요 |
| **0.0 ~ 1.9**  | [강력 매도] - 심각한 악재 또는 하락 추세 뚜렷 |

**[최종 점수]**
- **등급**: 중립
- **점수**: 5.0

---

### 2. 등급 선정 근거
- **긍정적 요인**:
  - ...
- **부정적 요인**:
  - ...
- **종합**: ...

---

### 3. 핵심 승리 논리 3가지
**[승리 논리 1]**
- ...
**[승리 논리 2]**
- ...
**[승리 논리 3]**
- ...

---

### 4. 주요 리스크
**[주요 리스크 1]**
- **규제 리스크**: ...
**[주요 리스크 2]**
- **고평가 논란**: ...
**[주요 리스크 3]**
- **경쟁사 압박**: ...

---

### 5. 구체적 트레이딩 시나리오
- **적정 진입 가격대**: ...
  - ...
- **1차 목표가**: ...
  - ...
- **2차 목표가**: ...
  - ...
- **손절가 (Stop Loss)**: ...
  - ...
```

## 주의사항

- **API 호출 제한**: 실시간 데이터 수집 시 API 호출 횟수 제한(Rate Limit)에 유의하세요.
- **보안**: `.env` 파일은 절대 GitHub에 올리지 마십시오.
- **투자 책임**: 본 시스템의 분석 결과는 참고용이며, 투자 판단과 그에 따른 결과는 전적으로 사용자 책임입니다.

---

## 라이센스

MIT License

---

## 문의

프로젝트 관련 문의사항은 Issue를 통해 남겨주세요.

