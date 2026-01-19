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
        const token = localStorage.getItem('accessToken');

        // 1. 비로그인 처리
        if (!token) {
            alert('로그인이 필요한 서비스입니다.');
            window.location.href = 'login.html';
            return;
        }

        // 2. API 호출 (로그에 200 OK 떴으니 무조건 데이터 옴)
        const response = await fetch('/api/history/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        // 3. 토큰 만료 처리
        if (response.status === 401) {
            alert('세션이 만료되었습니다. 다시 로그인해주세요.');
            window.location.href = 'login.html';
            return;
        }

        const data = await response.json();

        // 4. 화면 렌더링
        if (loadingEl) loadingEl.style.display = 'none';

        if (!data || data.length === 0) {
            if (emptyStateEl) emptyStateEl.style.display = 'block';
            return;
        }

        if (historyListEl) {
            historyListEl.style.display = 'block';
            renderHistoryList(groupByDate(data));
        }

    } catch (error) {
        console.error("히스토리 로드 실패:", error);
        if (loadingEl) loadingEl.innerHTML = '<div class="text-red-400">데이터를 불러오지 못했습니다.</div>';
    }
}

// 날짜별 그룹화
function groupByDate(data) {
    const grouped = {};
    data.forEach(item => {
        // created_at (YYYY-MM-DDTHH:mm:ss) -> 날짜만 추출
        let dateStr = item.created_at;
        if (dateStr && dateStr.includes('T')) {
            dateStr = dateStr.split('T')[0];
        } else if (dateStr && dateStr.includes(' ')) {
            dateStr = dateStr.split(' ')[0];
        }

        if (!grouped[dateStr]) {
            grouped[dateStr] = [];
        }
        grouped[dateStr].push(item);
    });
    return grouped;
}

// 리스트 그리기
// 리스트 그리기 함수 (수정됨)
// 리스트 그리기 함수 (질문만 표시되도록 수정됨)
function renderHistoryList(groupedData) {
    const listEl = document.getElementById('history-list');
    listEl.innerHTML = '';

    // 최신 날짜순 정렬
    const sortedDates = Object.keys(groupedData).sort((a, b) => new Date(b) - new Date(a));

    sortedDates.forEach(date => {
        // 1. 날짜 헤더 생성
        const header = document.createElement('div');
        header.className = 'flex justify-center mb-4 mt-8 first:mt-2';
        header.innerHTML = `<span class="bg-white text-slate-500 text-xs px-3 py-1 rounded-full border border-slate-200 font-mono shadow-sm">${date}</span>`;
        listEl.appendChild(header);

        // 2. 카드 아이템 생성
        groupedData[date].forEach(item => {
            const card = document.createElement('div');
            // 스타일: 깔끔한 박스 형태
            card.className = 'box cursor-pointer hover:border-[#6886b3] transition-all group mb-3 p-5 bg-white border border-[#6886b3] rounded-lg shadow-sm hover:shadow-md hover:bg-slate-50';

            // [수정] 오직 질문만 표시 (요약/의견 삭제됨)
            card.innerHTML = `
                <div class="flex justify-between items-center w-full">
                    <p class="text-slate-800 text-lg font-bold line-clamp-1 flex-1 pr-4">${item.question}</p>
                    <span class="text-gray-500 group-hover:text-blue-400 transition-colors transform group-hover:translate-x-1 duration-200">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    </span>
                </div>
            `;

            // 클릭 시 분석 페이지로 이동
            card.onclick = () => viewAnalysis(item);
            listEl.appendChild(card);
        });
    });
}
// 분석 페이지로 데이터 넘기기
function viewAnalysis(item) {
    localStorage.setItem('userQuestion', item.question);
    localStorage.setItem('analysis_summary', item.summary);
    localStorage.setItem('analysis_conclusion', item.conclusion);
    localStorage.setItem('analysis_chat_history', item.chat_logs); // DB JSON 문자열 그대로 저장

    // ★ 핵심: 다시보기 모드 ON
    localStorage.setItem('history_mode', 'true');
    
    window.location.href = 'analysis.html';
}