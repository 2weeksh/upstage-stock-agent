document.addEventListener('DOMContentLoaded', async () => {
    console.log('history.html 페이지 로드됨');
    await loadHistory();
});

// 질문 기록 로드
async function loadHistory() {
    const loadingEl = document.getElementById('loading');
    const historyListEl = document.getElementById('history-list');
    const emptyStateEl = document.getElementById('empty-state');

    try {
        // ============================================================
        // DB 연동 ?
        /*
        const token = localStorage.getItem('accessToken');
        
        // 토큰이 없으면 로그인 페이지로 (필요시 사용)
        // if (!token) {
        //     window.location.href = 'login.html';
        //     return;
        // }

        // const response = await fetch(`${AUTH_API_BASE}/history`, { 
        const response = await fetch('/api/chat/history', { 
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // JWT 토큰 인증
            }
        });

        if (!response.ok) {
            // 401 Unauthorized 등 에러 처리
            if (response.status === 401) {
                alert('세션이 만료되었습니다. 다시 로그인해주세요.');
                window.location.href = 'login.html';
                return;
            }
            throw new Error('서버에서 기록을 불러오는데 실패했습니다.');
        }

        // 서버 데이터로 교체 (변수명 data 재선언 주의: 아래 더미 데이터 const data 주석 처리 필요)
        const data = await response.json();
        */
        // ============================================================


        // ============================================================
        
        const data = [
            {
                id: 1,
                question: "(테스트)삼성전자 주식 전망은 어떤가요?",
                summary: "삼성전자는 반도체 업황 회복으로 긍정적 전망",
                conclusion: "매수 추천",
                log: "분석 실행 완료",
                created_at: "2024-01-15T10:00:00Z"
            },
            {
                id: 2,
                question: "(테스트)LG에너지솔루션 투자 가치가 있을까요?",
                summary: "LG에너지솔루션은 2차전지 산업 성장으로 수혜 예상",
                conclusion: "관망 필요",
                log: "상세 분석 완료",
                created_at: "2024-01-16T14:30:00Z"
            },
            {
                id: 3,
                question: "최근 질문 테스트 (같은 날짜)",
                summary: "테스트 데이터",
                conclusion: "확인",
                log: "로그",
                created_at: "2024-01-16T10:00:00Z"
            },
            {
                id: 1,
                question: "(테스트)삼성전자 주식 전망은 어떤가요?",
                summary: "삼성전자는 반도체 업황 회복으로 긍정적 전망",
                conclusion: "매수 추천",
                log: "분석 실행 완료",
                created_at: "2024-01-15T10:00:00Z"
            },
            {
                id: 2,
                question: "(테스트)LG에너지솔루션 투자 가치가 있을까요?",
                summary: "LG에너지솔루션은 2차전지 산업 성장으로 수혜 예상",
                conclusion: "관망 필요",
                log: "상세 분석 완료",
                created_at: "2024-01-16T14:30:00Z"
            },
            {
                id: 3,
                question: "최근 질문 테스트 (같은 날짜)",
                summary: "테스트 데이터",
                conclusion: "확인",
                log: "로그",
                created_at: "2024-01-16T10:00:00Z"
            }
        ];
        // ============================================================

        // 3. 최신순으로 정렬
        data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        // 로딩 숨기기
        loadingEl.style.display = 'none';

        if (data.length === 0) {
            emptyStateEl.style.display = 'block';
            return;
        }

        historyListEl.style.display = 'block';

        // 4. 날짜별로 그룹화하여 렌더링
        const groupedData = groupByDate(data);
        renderHistoryList(groupedData);

    } catch (error) {
        console.error(error);
        loadingEl.innerHTML = '<div class="text-red-400">데이터를 불러오는 중 오류가 발생했습니다.</div>';
    }
}

// 날짜별로 그룹화
function groupByDate(data) {
    const grouped = {};
    
    data.forEach(item => {
        const date = new Date(item.created_at).toLocaleDateString('ko-KR');
        if (!grouped[date]) {
            grouped[date] = [];
        }
        grouped[date].push(item);
    });
    
    return grouped;
}

// 질문 기록 목록 렌더링
function renderHistoryList(groupedData) {
    const historyListEl = document.getElementById('history-list');
    historyListEl.innerHTML = '';

    // 날짜 키 내림차순 정렬 (최신 날짜가 위로)
    const sortedDates = Object.keys(groupedData).sort((a, b) => {
        return new Date(b.replace(/\./g, '-')) - new Date(a.replace(/\./g, '-'));
    });

    sortedDates.forEach(date => {
        // 1. 날짜 배지 (중앙 배치)
        const dateHeaderContainer = document.createElement('div');
        dateHeaderContainer.className = 'flex justify-center mb-4 mt-8 first:mt-2';
        
        const dateBadge = document.createElement('span');
        dateBadge.className = 'bg-gray-800 text-gray-400 text-xs px-3 py-1 rounded-full border border-gray-700 font-mono';
        dateBadge.textContent = date;
        
        dateHeaderContainer.appendChild(dateBadge);
        historyListEl.appendChild(dateHeaderContainer);

        // 2. 해당 날짜의 질문
        groupedData[date].forEach(item => {
            const card = document.createElement('div');
            card.className = 'box cursor-pointer hover:border-blue-500 transition-all group mb-3';
            
            card.innerHTML = `
                <p class="text-white text-lg font-medium line-clamp-2">${item.question}</p>
            `;

            // 클릭 시 분석 페이지로 이동
            card.onclick = () => viewAnalysis(item.question, item.summary, item.conclusion, item.log);
            
            historyListEl.appendChild(card);
        });
    });
}

// 분석 페이지로 이동
function viewAnalysis(question, summary, conclusion, log) {
    localStorage.setItem('userQuestion', question);
    localStorage.setItem('analysis_summary', summary || '');
    localStorage.setItem('analysis_conclusion', conclusion || '');
    localStorage.setItem('analysis_log', log || '');
    
    window.location.href = 'analysis.html';
}