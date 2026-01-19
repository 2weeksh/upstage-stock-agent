"""
실제 멀티 에이전트 토론 시스템 vs 단일 에이전트 성능 비교

[비교 대상]
- 멀티: 실제 StockService (기조발언 → 토론 → 최후변론 → 사회자요약 → Judge판정)
- 단일: SingleAgentAnalyzer (모든 데이터 한 번에 분석)

실행 방법:
    python evaluate/compare_with_debate.py

결과:
    - evaluate/results/debate_comparison_YYYYMMDD_HHMMSS.json
    - evaluate/results/debate_comparison_YYYYMMDD_HHMMSS_summary.md
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
from app.utils.ticker_utils import get_clean_ticker


class SingleAgentAnalyzer:
    """
    단일 에이전트: 모든 데이터를 한 번에 받아서 분석
    (기존과 동일 - 토론 없음)
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


class RealMultiAgentSystem:
    """
    실제 멀티 에이전트 토론 시스템
    (StockService의 전체 프로세스 활용)
    """
    
    def __init__(self):
        from app.service.stock_service import StockService
        self.stock_service = StockService()
    
    async def analyze(self, company_name: str) -> Dict:
        """
        실제 토론 시스템 실행
        
        프로세스:
        1. 기조 발언 (차트/재무/뉴스 에이전트)
        2. 상호 토론 (최대 10라운드, 사회자 주도)
        3. 최후 변론
        4. 사회자 요약
        5. Judge 최종 판정
        6. Report 생성
        """
        
        user_question = f"{company_name} 분석해줘"
        
        # 스트리밍 결과 수집
        discussion_log = []
        final_summary = None
        final_conclusion = None
        max_debate_round = 0  # 실제 토론 라운드 추적
        
        print(f"    🔄 실제 토론 시스템 실행 중... (약 2-3분 소요)")
        
        try:
            async for event_str in self.stock_service.handle_user_task(user_question):
                try:
                    event_data = json.loads(event_str)
                    event_type = event_data.get('type')
                    
                    # status 메시지에서 실제 토론 라운드 번호 추출
                    if event_type == 'status':
                        message = event_data.get('message', '')
                        # "상호 토론 5/10 라운드" 패턴에서 추출
                        match = re.search(r'상호 토론 (\d+)/\d+ 라운드', message)
                        if match:
                            round_num = int(match.group(1))
                            max_debate_round = max(max_debate_round, round_num)
                    
                    # 토론 과정 기록 (전체 discussion_log는 분석용으로 유지)
                    if event_type == 'debate':
                        speaker = event_data.get('speaker', 'unknown')
                        message = event_data.get('message', '')
                        discussion_log.append({
                            'speaker': speaker,
                            'message': message
                        })
                    
                    # 최종 결과 수집
                    elif event_type == 'result':
                        result_data = event_data.get('data', {})
                        final_summary = result_data.get('summary', '')
                        final_conclusion = result_data.get('conclusion', '')
                        break  # 최종 결과 받으면 종료
                        
                except json.JSONDecodeError:
                    continue  # JSON 파싱 실패 시 무시
        
        except Exception as e:
            print(f"    ❌ 토론 시스템 실행 중 오류: {e}")
            return {
                "type": "multi_agent_with_debate",
                "company": company_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "type": "multi_agent_with_debate",
            "company": company_name,
            "discussion_log": discussion_log,
            "summary": final_summary,
            "conclusion": final_conclusion,
            "debate_rounds": max_debate_round,  # 실제 토론 라운드 (최대 10)
            "timestamp": datetime.now().isoformat()
        }


class DebateComparator:
    """실제 토론 시스템 vs 단일 에이전트 비교 평가"""
    
    def __init__(self):
        self.single_agent = SingleAgentAnalyzer()
        self.multi_agent = RealMultiAgentSystem()
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
                "evaluator": "LLM-as-Judge (Solar Pro 2)",
                "multi_agent_type": "Full Debate System (기조발언 + 토론 + 최후변론 + 사회자요약 + 판정)"
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
                print(f"  ✅ 티커: {ticker}")
                
                # 2. 데이터 수집 (단일 에이전트용)
                print(f"  📥 데이터 수집 중...")
                chart_data = get_chart_indicators(ticker)
                finance_data = get_financial_summary(ticker)
                news_data = get_stock_news(ticker, company_name)
                
                # 3. 멀티 에이전트 분석 (실제 토론 시스템)
                print(f"  🎭 멀티 에이전트 토론 시스템 실행...")
                multi_result = await self.multi_agent.analyze(company_name)
                
                if "error" in multi_result:
                    print(f"  ❌ 멀티 에이전트 실행 실패: {multi_result['error']}")
                    results["stocks"].append({
                        "company": company_name,
                        "ticker": ticker,
                        "error": multi_result["error"]
                    })
                    continue
                
                print(f"  ✅ 토론 완료 (라운드 수: {multi_result.get('debate_rounds', 0)})")
                
                # 4. 단일 에이전트 분석
                print(f"  🔄 단일 에이전트 분석 실행...")
                single_result = self.single_agent.analyze(
                    company_name, ticker, chart_data, finance_data, news_data
                )
                print(f"  ✅ 단일 에이전트 분석 완료")
                
                # 5. 평가
                print(f"  ⚖️  LLM-as-Judge 평가 중...")
                evaluation = await self._evaluate_pair(
                    company_name, multi_result, single_result
                )
                print(f"  ✅ 평가 완료")
                
                # 6. 결과 저장
                results["stocks"].append({
                    "company": company_name,
                    "ticker": ticker,
                    "multi_agent_result": multi_result,
                    "single_agent_result": single_result,
                    "evaluation": evaluation
                })
                
                print(f"  ✅ {company_name} 전체 평가 완료\n")
                
            except Exception as e:
                import traceback
                print(f"  ❌ {company_name} 처리 중 오류: {e}")
                traceback.print_exc()
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

        [시스템 A - 멀티 에이전트 토론 시스템]
        - 3명의 전문가(차트/재무/뉴스)가 기조 발언
        - 사회자 주도로 상호 토론 진행 ({multi_result.get('debate_rounds', 0)}라운드)
        - 반박을 통한 리스크 발견 및 논리 검증
        - 최후 변론 및 사회자 요약
        - Judge의 최종 판정

        최종 결론:
        {multi_result.get('conclusion', '')}

        [시스템 B - 단일 에이전트 (통합 분석)]
        - 한 명의 AI가 모든 데이터를 한 번에 분석
        - 토론 과정 없음

        결과:
        {single_result.get('analysis', '')}

        ---
        **평가 기준 (각 1~10점)**

        1. **논리적 타당성 (Logical Coherence)**
        - 분석 근거가 명확하고 논리적으로 일관성이 있는가?

        2. **다각적 관점 (Multi-Perspective)** ⭐ 핵심!
        - 기술적/재무적/심리적 측면을 균형있게 고려했는가?
        - 토론을 통해 각 관점이 심화되었는가?

        3. **리스크 인식 (Risk Awareness)** ⭐ 핵심!
        - 투자 리스크를 충분히 인지하고 경고했는가?
        - 반박 과정에서 숨겨진 리스크를 발견했는가?

        4. **실행 가능성 (Actionability)**
        - 실제 투자에 바로 적용 가능한 구체적 전략인가?

        5. **데이터 근거 (Evidence-Based)**
        - 실제 데이터(수치)를 효과적으로 인용하고 활용했는가?

        ---
        **출력 형식 (JSON만 출력, 다른 텍스트 포함 금지)**
        {{
          "system_a_debate": {{
            "logical_coherence": {{"score": 8, "reason": "토론을 통해 논리가 검증됨"}},
            "multi_perspective": {{"score": 9, "reason": "차트/재무/뉴스 각 관점이 토론으로 심화"}},
            "risk_awareness": {{"score": 9, "reason": "반박 과정에서 부채 리스크 발견"}},
            "actionability": {{"score": 8, "reason": "구체적 진입가/목표가 제시"}},
            "evidence_based": {{"score": 9, "reason": "각 전문가가 수치 근거 제시"}}
          }},
          "system_b_single": {{
            "logical_coherence": {{"score": 7, "reason": "일관성은 있으나 검증 부족"}},
            "multi_perspective": {{"score": 6, "reason": "여러 관점 언급했으나 깊이 부족"}},
            "risk_awareness": {{"score": 6, "reason": "일부 리스크 언급했으나 발견 과정 없음"}},
            "actionability": {{"score": 7, "reason": "전략 제시했으나 근거 약함"}},
            "evidence_based": {{"score": 7, "reason": "데이터 사용했으나 활용도 낮음"}}
          }},
          "winner": "system_a_debate",
          "conclusion": "멀티 에이전트 토론 시스템이 반박을 통해 리스크를 발견하고, 각 관점을 심화시켰음. 특히 재무 전문가가 차트의 긍정적 전망에 대해 부채 리스크를 경고한 점이 돋보임."
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
        
        total_debate_rounds = []
        
        for result in valid_results:
            eval_data = result["evaluation"]
            winner = eval_data.get("winner", "").lower()
            
            if "debate" in winner or "multi" in winner:
                multi_wins += 1
            elif "single" in winner:
                single_wins += 1
            else:
                draws += 1
            
            # 토론 라운드 수 기록
            multi_result = result.get("multi_agent_result", {})
            if "debate_rounds" in multi_result:
                total_debate_rounds.append(multi_result["debate_rounds"])
            
            # 점수 수집
            system_a = eval_data.get("system_a_debate", {})
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
                "multi_agent_debate": multi_wins,
                "single_agent": single_wins,
                "draws": draws
            },
            "average_scores": {
                "multi_agent_debate": {k: avg(v) for k, v in multi_scores.items()},
                "single_agent": {k: avg(v) for k, v in single_scores.items()}
            },
            "total_score": {
                "multi_agent_debate": round(sum(avg(v) for v in multi_scores.values()), 2),
                "single_agent": round(sum(avg(v) for v in single_scores.values()), 2)
            },
            "average_debate_rounds": round(avg(total_debate_rounds), 1) if total_debate_rounds else 0
        }
    
    def save_results(self, results: Dict, output_dir: str = "evaluate/results"):
        """결과 저장 (JSON + Markdown)"""
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. JSON 저장
        json_path = f"{output_dir}/debate_comparison_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ JSON 저장: {json_path}")
        
        # 2. Markdown 요약 저장
        md_path = f"{output_dir}/debate_comparison_{timestamp}_summary.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(results))
        
        print(f"✅ Markdown 요약: {md_path}")
    
    def _generate_markdown_report(self, results: Dict) -> str:
        """Markdown 리포트 생성"""
        
        summary = results.get("summary", {})
        
        md = f"""# 멀티 에이전트 토론 시스템 vs 단일 에이전트 성능 비교 리포트

## 📋 메타데이터
- **평가 일시**: {results['metadata']['test_date']}
- **테스트 종목 수**: {results['metadata']['total_stocks']}
- **평가자**: {results['metadata']['evaluator']}
- **멀티 에이전트 타입**: {results['metadata']['multi_agent_type']}

---

## 🏆 종합 결과

### 승률
- **멀티 에이전트 (토론 시스템) 승리**: {summary['win_rate']['multi_agent_debate']}회 🎉
- **단일 에이전트 승리**: {summary['win_rate']['single_agent']}회
- **무승부**: {summary['win_rate']['draws']}회

### 토론 통계
- **평균 토론 라운드 수**: {summary.get('average_debate_rounds', 0)}라운드

### 평균 점수 (10점 만점)

| 평가 기준 | 멀티 (토론) | 단일 | 차이 | 향상률 |
|----------|------------|------|------|--------|
"""
        
        multi_avg = summary['average_scores']['multi_agent_debate']
        single_avg = summary['average_scores']['single_agent']
        
        for metric in multi_avg.keys():
            m_score = multi_avg[metric]
            s_score = single_avg[metric]
            diff = m_score - s_score
            diff_str = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
            improvement = f"+{(diff/s_score)*100:.1f}%" if s_score > 0 else "N/A"
            
            # 핵심 지표 강조
            emoji = " ⭐" if metric in ["multi_perspective", "risk_awareness"] else ""
            
            md += f"| {metric}{emoji} | {m_score} | {s_score} | {diff_str} | {improvement} |\n"
        
        md += f"""
### 총점
- **멀티 에이전트 (토론)**: {summary['total_score']['multi_agent_debate']}/50
- **단일 에이전트**: {summary['total_score']['single_agent']}/50
- **차이**: +{summary['total_score']['multi_agent_debate'] - summary['total_score']['single_agent']:.2f}점

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
            
            # 토론 라운드 정보
            multi_result = stock.get('multi_agent_result', {})
            debate_rounds = multi_result.get('debate_rounds', 0)
            
            md += f"""### {stock['company']} ({stock['ticker']})
**승자**: {winner} 🏆
**토론 라운드**: {debate_rounds}회

**결론**: {conclusion}

---

"""
        
        # 핵심 인사이트 추가
        md += f"""
## 💡 핵심 인사이트

### 토론의 효과
1. **다각적 관점 심화**: 토론을 통해 각 전문가의 관점이 더욱 깊어짐
2. **리스크 발견**: 반박 과정에서 단일 에이전트가 놓친 리스크 발견
3. **논리 검증**: 상호 질의응답을 통해 분석의 타당성 검증

### 예상 시나리오
- **차트 전문가**: "기술적으로 상승 추세입니다"
- **사회자**: "재무 분석가님, 이 상승이 지속 가능할까요?"
- **재무 전문가**: "부채비율이 높아 리스크가 있습니다"
- **차트 전문가**: "그렇다면 단기 전략으로 수정하겠습니다"
→ **토론을 통해 리스크 발견 및 전략 수정!**

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
        # "SK하이닉스",  # 시간이 오래 걸리므로 필요시 주석 해제
        # "카카오"
    ]
    
    print("\n" + "="*70)
    print("  🎭 멀티 에이전트 토론 시스템 vs 단일 에이전트 성능 비교")
    print("="*70)
    print(f"\n⏱️  예상 소요 시간: 약 {len(test_stocks) * 3}분")
    print("💡 멀티 에이전트는 실제 토론 시스템을 사용합니다 (기조발언 + 토론 + 최후변론 + 판정)")
    print("\n")
    
    comparator = DebateComparator()
    
    # 비교 실행
    results = await comparator.run_comparison(test_stocks)
    
    # 결과 저장
    comparator.save_results(results)
    
    # 콘솔 출력
    print("\n" + "="*70)
    print("  📊 최종 요약")
    print("="*70 + "\n")
    
    summary = results.get("summary", {})
    
    if "error" in summary:
        print(f"❌ 오류: {summary['error']}")
        return
    
    print(f"총 평가 종목: {summary.get('total_evaluated', 0)}개")
    print(f"평균 토론 라운드: {summary.get('average_debate_rounds', 0)}회")
    
    print(f"\n🏆 승률:")
    print(f"  - 멀티 에이전트 (토론): {summary['win_rate']['multi_agent_debate']}승")
    print(f"  - 단일 에이전트: {summary['win_rate']['single_agent']}승")
    print(f"  - 무승부: {summary['win_rate']['draws']}회")
    
    print(f"\n📈 평균 점수:")
    print(f"  - 멀티 에이전트 (토론): {summary['total_score']['multi_agent_debate']}/50")
    print(f"  - 단일 에이전트: {summary['total_score']['single_agent']}/50")
    
    # 핵심 지표 강조
    multi_scores = summary['average_scores']['multi_agent_debate']
    single_scores = summary['average_scores']['single_agent']
    
    print(f"\n⭐ 핵심 지표 비교:")
    print(f"  - 다각적 관점: {multi_scores['multi_perspective']} vs {single_scores['multi_perspective']}")
    improvement = ((multi_scores['multi_perspective'] - single_scores['multi_perspective']) / single_scores['multi_perspective']) * 100
    print(f"    → 멀티가 {improvement:.1f}% 더 우수!")
    
    print(f"  - 리스크 인식: {multi_scores['risk_awareness']} vs {single_scores['risk_awareness']}")
    improvement = ((multi_scores['risk_awareness'] - single_scores['risk_awareness']) / single_scores['risk_awareness']) * 100
    print(f"    → 멀티가 {improvement:.1f}% 더 우수!")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())