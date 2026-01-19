"""
멀티 에이전트 vs 단일 에이전트 성능 비교 평가

실행 방법:
    python evaluate/compare_agent.py

결과:
    - evaluate/results/comparison_YYYYMMDD_HHMMSS.json
    - evaluate/results/comparison_YYYYMMDD_HHMMSS_summary.md
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import asyncio
import re
from typing import Dict, List
from datetime import datetime
from pathlib import Path

from app.utils.llm import get_solar_model
from app.tools.chart_tools import get_chart_indicators
from app.tools.finance_tools import get_financial_summary
from app.tools.search_tools import get_stock_news
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker


class SingleAgentAnalyzer:
    """
    단일 에이전트: 모든 데이터를 한 번에 받아서 분석
    (토론 없이 통합 판단)
    """
    
    def __init__(self):
        self.llm = get_solar_model(temperature=0.2)
    
    def analyze(self, company_name: str, ticker: str, 
                chart_data: str, finance_data: str, news_data: str) -> Dict:
        
        prompt = f"""
        당신은 종합 투자 분석 전문가입니다.
        제공된 데이터를 바탕으로 {company_name}({ticker})에 대한 투자 전략을 수립하세요.

        [차트 분석 데이터]
        {chart_data}

        [재무 분석 데이터]
        {finance_data}

        [뉴스 및 시장 심리 데이터]
        {news_data}

        ---
        아래 형식으로 답변하세요:

        ### 1. 최종 투자 등급
        [강력 매수 / 매수 / 중립 / 매도 / 강력 매도]

        ### 2. 점수
        [0.0 ~ 10.0 사이의 점수]

        ### 3. 핵심 투자 논리 (3가지)
        1. [논리 1]
        2. [논리 2]
        3. [논리 3]

        ### 4. 주요 리스크 (3가지)
        1. [리스크 1]
        2. [리스크 2]
        3. [리스크 3]

        ### 5. 트레이딩 전략
        - 적정 진입가: [구체적 가격]
        - 1차 목표가: [가격]
        - 손절가: [가격]
        """
        
        response = self.llm.invoke(prompt).content
        
        return {
            "type": "single_agent",
            "company": company_name,
            "ticker": ticker,
            "analysis": response,
            "timestamp": datetime.now().isoformat()
        }


class MultiAgentSimulator:
    """
    멀티 에이전트 간소화 버전
    (실제 토론 대신 각 에이전트의 개별 분석만 수집)
    """
    
    def __init__(self):
        from app.agents.chart_agent import ChartAgent
        from app.agents.finance_agent import FinanceAgent
        from app.agents.news_agent import NewsAgent
        from app.agents.judge_agent import JudgeAgent
        
        self.chart_agent = ChartAgent(get_solar_model(temperature=0.1))
        self.finance_agent = FinanceAgent(get_solar_model(temperature=0.1))
        self.news_agent = NewsAgent(get_solar_model(temperature=0.3))
        self.judge_agent = JudgeAgent(get_solar_model(temperature=0.1))
    
    def analyze(self, company_name: str, ticker: str,
                chart_data: str, finance_data: str, news_data: str) -> Dict:
        
        # 각 에이전트 기조 발언
        chart_analysis = self.chart_agent.analyze(company_name, ticker, chart_data)
        finance_analysis = self.finance_agent.analyze(company_name, ticker, finance_data)
        news_analysis = self.news_agent.analyze(company_name, ticker, news_data)
        
        # 통합 컨텍스트
        combined_context = f"""
        [차트 분석가 의견]
        {chart_analysis}
        
        [재무 분석가 의견]
        {finance_analysis}
        
        [뉴스 분석가 의견]
        {news_analysis}
        """
        
        # Judge 최종 판단
        final_decision = self.judge_agent.adjudicate(company_name, combined_context)
        
        return {
            "type": "multi_agent",
            "company": company_name,
            "ticker": ticker,
            "chart_analysis": chart_analysis,
            "finance_analysis": finance_analysis,
            "news_analysis": news_analysis,
            "final_decision": final_decision,
            "timestamp": datetime.now().isoformat()
        }


class AgentComparator:
    """멀티 vs 단일 에이전트 비교 평가"""
    
    def __init__(self):
        self.single_agent = SingleAgentAnalyzer()
        self.multi_agent = MultiAgentSimulator()
        self.judge_llm = get_solar_model(temperature=0.0)  # 평가는 일관성 중요
    
    async def run_comparison(self, test_stocks: List[str]) -> Dict:
        """
        비교 평가 메인 함수
        
        Args:
            test_stocks: ["삼성전자", "SK하이닉스", ...] (한글 기업명)
        """
        results = {
            "metadata": {
                "test_date": datetime.now().isoformat(),
                "total_stocks": len(test_stocks),
                "evaluator": "LLM-as-Judge (Solar Pro 2)"
            },
            "stocks": []
        }
        
        for company_name in test_stocks:
            print(f"\n{'='*70}")
            print(f"📊 테스트 종목: {company_name}")
            print(f"{'='*70}\n")
            
            try:
                # 1. 티커 추출
                ticker = get_clean_ticker(company_name)
                print(f"✅ 티커: {ticker}")
                
                # 2. 데이터 수집 (공통)
                print("📥 데이터 수집 중...")
                chart_data = get_chart_indicators(ticker)
                finance_data = get_financial_summary(ticker)
                news_data = get_stock_news(ticker, company_name)
                
                # 3. 멀티 에이전트 분석
                print("🔄 멀티 에이전트 분석 실행...")
                multi_result = self.multi_agent.analyze(
                    company_name, ticker, chart_data, finance_data, news_data
                )
                
                # 4. 단일 에이전트 분석
                print("🔄 단일 에이전트 분석 실행...")
                single_result = self.single_agent.analyze(
                    company_name, ticker, chart_data, finance_data, news_data
                )
                
                # 5. 평가
                print("⚖️ LLM-as-Judge 평가 중...")
                evaluation = await self._evaluate_pair(
                    company_name, multi_result, single_result
                )
                
                # 6. 결과 저장
                results["stocks"].append({
                    "company": company_name,
                    "ticker": ticker,
                    "multi_agent_result": multi_result,
                    "single_agent_result": single_result,
                    "evaluation": evaluation
                })
                
                print(f"✅ {company_name} 평가 완료\n")
                
            except Exception as e:
                print(f"❌ {company_name} 처리 중 오류: {e}\n")
                results["stocks"].append({
                    "company": company_name,
                    "error": str(e)
                })
        
        # 7. 종합 요약
        results["summary"] = self._generate_summary(results["stocks"])
        
        return results
    
    async def _evaluate_pair(self, company_name: str, 
                            multi_result: Dict, single_result: Dict) -> Dict:
        """LLM-as-Judge 평가"""
        
        evaluation_prompt = f"""
        당신은 객관적인 투자 분석 평가자입니다.
        두 AI 시스템이 {company_name}를 분석한 결과를 비교하여 5가지 기준으로 평가하세요.

        [시스템 A - 멀티 에이전트 (토론 기반)]
        {multi_result.get('final_decision', multi_result.get('analysis', ''))}

        [시스템 B - 단일 에이전트 (통합 분석)]
        {single_result.get('analysis', '')}

        ---
        **평가 기준 (각 1~10점)**

        1. **논리적 타당성 (Logical Coherence)**
        - 분석 근거가 명확하고 논리적으로 일관성이 있는가?

        2. **다각적 관점 (Multi-Perspective)**
        - 기술적/재무적/심리적 측면을 균형있게 고려했는가?

        3. **리스크 인식 (Risk Awareness)**
        - 투자 리스크를 충분히 인지하고 경고했는가?

        4. **실행 가능성 (Actionability)**
        - 실제 투자에 바로 적용 가능한 구체적 전략인가?

        5. **데이터 근거 (Evidence-Based)**
        - 실제 데이터(수치)를 효과적으로 인용하고 활용했는가?

        ---
        **출력 형식 (JSON만 출력)**
        {{
          "system_a_multi": {{
            "logical_coherence": {{"score": 8, "reason": "..."}},
            "multi_perspective": {{"score": 9, "reason": "..."}},
            "risk_awareness": {{"score": 7, "reason": "..."}},
            "actionability": {{"score": 8, "reason": "..."}},
            "evidence_based": {{"score": 9, "reason": "..."}}
          }},
          "system_b_single": {{
            "logical_coherence": {{"score": 7, "reason": "..."}},
            "multi_perspective": {{"score": 6, "reason": "..."}},
            "risk_awareness": {{"score": 6, "reason": "..."}},
            "actionability": {{"score": 7, "reason": "..."}},
            "evidence_based": {{"score": 7, "reason": "..."}}
          }},
          "winner": "system_a_multi",
          "conclusion": "멀티 에이전트가 차트/재무/뉴스 각 관점을 명확히 구분하여..."
        }}
        """
        
        response = self.judge_llm.invoke(evaluation_prompt).content
        
        # JSON 추출
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return {"error": "JSON 파싱 실패", "raw_response": response[:500]}
        except Exception as e:
            return {"error": str(e), "raw_response": response[:500]}
    
    def _generate_summary(self, stock_results: List[Dict]) -> Dict:
        """종합 요약 통계"""
        
        valid_results = [r for r in stock_results if "evaluation" in r and "error" not in r["evaluation"]]
        
        if not valid_results:
            return {"error": "유효한 평가 결과 없음"}
        
        multi_wins = 0
        single_wins = 0
        draws = 0
        
        multi_scores = {
            "logical_coherence": [],
            "multi_perspective": [],
            "risk_awareness": [],
            "actionability": [],
            "evidence_based": []
        }
        
        single_scores = {
            "logical_coherence": [],
            "multi_perspective": [],
            "risk_awareness": [],
            "actionability": [],
            "evidence_based": []
        }
        
        for result in valid_results:
            eval_data = result["evaluation"]
            winner = eval_data.get("winner", "").lower()
            
            if "multi" in winner:
                multi_wins += 1
            elif "single" in winner:
                single_wins += 1
            else:
                draws += 1
            
            # 점수 수집
            system_a = eval_data.get("system_a_multi", {})
            system_b = eval_data.get("system_b_single", {})
            
            for metric in multi_scores.keys():
                if metric in system_a:
                    multi_scores[metric].append(system_a[metric].get("score", 0))
                if metric in system_b:
                    single_scores[metric].append(system_b[metric].get("score", 0))
        
        # 평균 계산
        def avg(lst):
            return round(sum(lst) / len(lst), 2) if lst else 0
        
        return {
            "total_evaluated": len(valid_results),
            "win_rate": {
                "multi_agent": multi_wins,
                "single_agent": single_wins,
                "draws": draws
            },
            "average_scores": {
                "multi_agent": {k: avg(v) for k, v in multi_scores.items()},
                "single_agent": {k: avg(v) for k, v in single_scores.items()}
            },
            "total_score": {
                "multi_agent": round(sum(avg(v) for v in multi_scores.values()), 2),
                "single_agent": round(sum(avg(v) for v in single_scores.values()), 2)
            }
        }
    
    def save_results(self, results: Dict, output_dir: str = "evaluate/results"):
        """결과 저장 (JSON + Markdown)"""
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. JSON 저장
        json_path = f"{output_dir}/comparison_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON 저장: {json_path}")
        
        # 2. Markdown 요약 저장
        md_path = f"{output_dir}/comparison_{timestamp}_summary.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(results))
        
        print(f"✅ Markdown 요약: {md_path}")
    
    def _generate_markdown_report(self, results: Dict) -> str:
        """Markdown 리포트 생성"""
        
        summary = results.get("summary", {})
        
        md = f"""# 멀티 에이전트 vs 단일 에이전트 성능 비교 리포트

## 📋 메타데이터
- **평가 일시**: {results['metadata']['test_date']}
- **테스트 종목 수**: {results['metadata']['total_stocks']}
- **평가자**: {results['metadata']['evaluator']}

---

## 🏆 종합 결과

### 승률
- **멀티 에이전트 승리**: {summary['win_rate']['multi_agent']}회
- **단일 에이전트 승리**: {summary['win_rate']['single_agent']}회
- **무승부**: {summary['win_rate']['draws']}회

### 평균 점수 (10점 만점)

| 평가 기준 | 멀티 에이전트 | 단일 에이전트 | 차이 |
|----------|-------------|-------------|-----|
"""
        
        multi_avg = summary['average_scores']['multi_agent']
        single_avg = summary['average_scores']['single_agent']
        
        for metric in multi_avg.keys():
            m_score = multi_avg[metric]
            s_score = single_avg[metric]
            diff = m_score - s_score
            diff_str = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
            
            md += f"| {metric} | {m_score} | {s_score} | {diff_str} |\n"
        
        md += f"""
### 총점
- **멀티 에이전트**: {summary['total_score']['multi_agent']}/50
- **단일 에이전트**: {summary['total_score']['single_agent']}/50

---

## 📊 개별 종목 평가

"""
        
        for stock in results['stocks']:
            if 'error' in stock:
                md += f"### {stock['company']}\n❌ 평가 실패: {stock['error']}\n\n"
                continue
            
            eval_data = stock.get('evaluation', {})
            if 'error' in eval_data:
                md += f"### {stock['company']}\n⚠️ 평가 오류\n\n"
                continue
            
            winner = eval_data.get('winner', 'unknown')
            conclusion = eval_data.get('conclusion', '')
            
            md += f"""### {stock['company']} ({stock['ticker']})
**승자**: {winner}

**결론**: {conclusion}

---

"""
        
        return md


# ============================================================
# 실행
# ============================================================

async def main():
    """메인 실행 함수"""
    
    # 테스트할 종목 (한글 기업명)
    test_stocks = [
        "삼성전자",
        "SK하이닉스",
        "카카오"
        # "NVIDIA",
        # "Apple"
    ]
    
    print("\n" + "="*70)
    print("  🔬 멀티 에이전트 vs 단일 에이전트 성능 비교 평가")
    print("="*70 + "\n")
    
    comparator = AgentComparator()
    
    # 비교 실행
    results = await comparator.run_comparison(test_stocks)
    
    # 결과 저장
    comparator.save_results(results)
    
    # 콘솔 출력
    print("\n" + "="*70)
    print("  📊 최종 요약")
    print("="*70 + "\n")
    
    summary = results.get("summary", {})
    
    print(f"총 평가 종목: {summary.get('total_evaluated', 0)}개")
    print(f"\n승률:")
    print(f"  - 멀티 에이전트: {summary['win_rate']['multi_agent']}승")
    print(f"  - 단일 에이전트: {summary['win_rate']['single_agent']}승")
    print(f"  - 무승부: {summary['win_rate']['draws']}회")
    
    print(f"\n평균 점수:")
    print(f"  - 멀티 에이전트: {summary['total_score']['multi_agent']}/50")
    print(f"  - 단일 에이전트: {summary['total_score']['single_agent']}/50")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
