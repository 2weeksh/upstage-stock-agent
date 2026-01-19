# app/services/dart_collector.py

import OpenDartReader
import os
import re
import warnings

from datetime import datetime
from dotenv import load_dotenv
from langchain_core.documents import Document
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning


class DartCollector:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("DART_API_KEY")
        self.dart = OpenDartReader(api_key)


    def _clean_text(self, html_or_xml: str) -> str:
        """
        XML/HTML 태그를 제거하고 깨끗한 텍스트만 추출합니다.
        """
        if not html_or_xml:
            return ""
        
        # 1. XML 파싱 경고 무시 및 'xml' 파서 사용
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(html_or_xml, 'xml') # 'lxml' 대신 'xml' 사용

        # 2. 택스트 추출 (줄바꿈 유지)
        text = soup.get_text(separator="") # 줄바꿈을 유지하며 텍스트 추출
        
        # 2. 정규표현식으로 '노이즈' 제거
        # 연속된 공백(스페이스, 탭 등)을 하나의 스페이스로 합침
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 3. 문서 내에 너무 많이 발생하는 공백 줄바꿈 정리
        # (표 구조 때문에 발생하는 파편화된 줄바꿈 제거)
        lines = text.split('\n')
        clean_lines = [line.strip() for line in lines if line.strip()]
        text = " ".join(clean_lines) # 모든 파편을 일단 한 문장처럼 붙임

        # 4. 너무 긴 문장을 에이전트가 읽기 좋게 적당히 다듬기
        # (필요에 따라 마침표 뒤에 줄바꿈을 강제로 넣는 등의 처리가 가능합니다)
        text = text.replace(". ", ".\n")
            
        return text.strip()


    def get_latest_report_text(self, ticker: str, company_name: str) -> list[Document]:
        """
        가장 최신의 정기공시(사업, 반기, 분기)를 찾아 주요 섹션 텍스트를 통합하여 반환합니다.
        """
        # 1. 최신 정기공시 목록 가져오기 (A: 정기공시)
        # 2024년부터 현재까지의 공시 중 가장 최근 것 하나를 선택
        row = self.dart.list(ticker, start='20240101', kind='A').iloc[0]
        rcept_no = row['rcept_no']
        report_nm = row['report_nm']
        
        # 기업명이 인자로 안 들어왔을 경우 DART 리스트에서 가져온 이름 사용
        display_name = company_name if company_name else row['corp_name']

        print(f"📄 {display_name}({ticker}) 분석 보고서 탐색: {report_nm}")

        # 2. 핵심 섹션 리스트 (RAG에 가장 도움되는 섹션들)
        # '사업의 내용'이 가장 중요하며, '이사의 경영진단'은 기업의 향후 전망을 담고 있습니다.
        sections = ['사업의 내용', '이사의 경영진단 및 분석의견', '투자위험요소']
        combined_text = ""

        for section in sections:
            try:
                raw_content = self.dart.document(rcept_no, section)
                if raw_content:
                    clean_section_text = self._clean_text(raw_content)
                    combined_text += f"\n\n[섹션: {section}]\n"
                    combined_text += clean_section_text
            except Exception as e:
                # 특정 섹션이 없는 보고서(분기보고서 등)일 경우 건너뜀
                continue

        if not combined_text:
            # 섹션별 추출 실패 시 전체 원문 시도 (단, 전체는 매우 큼)
            combined_text = self.dart.document(rcept_no)

        return combined_text, report_nm