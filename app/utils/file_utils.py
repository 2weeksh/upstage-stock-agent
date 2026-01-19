import os
from datetime import datetime

def save_debate_log(company_name, ticker, full_content):
    # 1. logs 폴더가 없으면 생성
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. 파일명 생성 (예: 20260114_삼성전자_AAPL_리포트.md)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_{company_name}_{ticker}_debate.md"
    file_path = os.path.join(log_dir, file_name)

    # 3. 파일 쓰기
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    print(f"\n💾 토론 로그가 저장되었습니다: {file_path}")
    return file_path