document.addEventListener('DOMContentLoaded', () => {
    // 1. 날짜 및 사용자 질문 표시
    const dateElem = document.getElementById('report-date');
    if (dateElem) {
        const today = new Date();
        dateElem.innerText = today.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' });
    }

    const userQueryElement = document.getElementById('user-query-text');
    const savedQuestion = localStorage.getItem('userQuestion');
    if (userQueryElement) userQueryElement.innerText = savedQuestion || "질문 없음";

    // 2. 분석 데이터(요약, 결론) 및 토론 뷰어 초기화
    initAnalysisData();
    initDiscussionViewer();

    // 3. 시장 요약 및 차트 렌더링 (기존 기능 유지)
    renderKospiChart();
    renderRealMarketData();
});

// 텍스트 줄바꿈 처리 헬퍼 함수
function formatText(text) {
    if (!text) return "데이터 로딩 중...";
    // 줄바꿈 문자를 <br>로 변환
    return text.replace(/\n/g, '<br>');
}

function initAnalysisData() {
    // 로컬 스토리지에서 데이터 가져오기
    const summaryData = localStorage.getItem('analysis_summary');
    const conclusionData = localStorage.getItem('analysis_conclusion');

    // 요약 및 결론 표시 (줄바꿈 적용)
    if(document.getElementById('res-summary')) {
        document.getElementById('res-summary').innerHTML = formatText(summaryData);
    }
    if(document.getElementById('res-conclusion')) {
        document.getElementById('res-conclusion').innerHTML = formatText(conclusionData);
    }
}

// ============================================================
// 🤖 [NEW] 토론 뷰어 기능 (버튼으로 넘겨보기)
// ============================================================
let chatLogs = [];
let currentIndex = 0;

function initDiscussionViewer() {
    // 1. 토글 버튼 로직
    const toggleBtn = document.getElementById('toggleDiscussionBtn');
    const content = document.getElementById('discussionContent');
    const icon = document.getElementById('toggleIcon'); // HTML 수정시 svg에 id="toggleIcon" 추가 필요

    if (toggleBtn && content) {
        toggleBtn.addEventListener('click', () => {
            content.classList.toggle('hidden');
            // 아이콘 회전 처리 (옵션)
            if (icon) {
                icon.classList.toggle('rotate-180');
            }
        });
    }

    // 2. 대화 로그 데이터 로드
    const rawHistory = localStorage.getItem('analysis_chat_history');
    if (rawHistory) {
        try {
            chatLogs = JSON.parse(rawHistory);
        } catch (e) {
            console.error("채팅 기록 파싱 실패:", e);
            chatLogs = [];
        }
    }

    // 데이터가 없을 경우 처리
    if (!chatLogs || chatLogs.length === 0) {
        const msgEl = document.getElementById('viewer-message');
        if (msgEl) msgEl.innerText = "저장된 토론 기록이 없습니다.";
        return;
    }

    // 3. 버튼 이벤트 리스너
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    if (btnPrev) {
        btnPrev.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                renderLog(currentIndex);
            }
        });
    }

    if (btnNext) {
        btnNext.addEventListener('click', () => {
            if (currentIndex < chatLogs.length - 1) {
                currentIndex++;
                renderLog(currentIndex);
            }
        });
    }

    // 4. 첫 화면 렌더링
    renderLog(0);
}

// 현재 인덱스의 대화를 화면에 그리는 함수
function renderLog(index) {
    const log = chatLogs[index];
    if (!log) return;

    // DOM 요소 가져오기
    const speakerEl = document.getElementById('viewer-speaker');
    const typeEl = document.getElementById('viewer-type');
    const avatarEl = document.getElementById('viewer-avatar');
    const msgEl = document.getElementById('viewer-message');
    const counterEl = document.getElementById('viewer-counter');

    if (!speakerEl || !msgEl) return;

    // 1. 텍스트 업데이트
    speakerEl.innerText = log.speaker;
    msgEl.innerHTML = formatText(log.message);

    // 2. 화자별 스타일 설정
    let icon = '🎤';
    let roleText = 'System';
    let bgClass = 'bg-gray-600'; // 기본 배경

    // 백엔드의 code 값에 따라 스타일 분기
    switch (log.code) {
        case 'chart':
            icon = '📈';
            roleText = 'Technical Analyst';
            bgClass = 'bg-blue-600'; // 차트: 파랑
            break;
        case 'finance':
            icon = '💰';
            roleText = 'Financial Analyst';
            bgClass = 'bg-green-600'; // 재무: 초록
            break;
        case 'news':
            icon = '📰';
            roleText = 'News & Sentiment';
            bgClass = 'bg-purple-600'; // 뉴스: 보라
            break;
        case 'moderator':
            icon = '🎙️';
            roleText = 'Moderator';
            bgClass = 'bg-gray-700'; // 사회자: 회색
            break;
        default:
            icon = '🤖';
            roleText = 'System Info';
            bgClass = 'bg-gray-600';
    }

    // 아바타 스타일 적용
    if (avatarEl) {
        avatarEl.innerText = icon;
        // 기존 클래스 유지하면서 배경색만 변경하기 위해 className 재설정
        avatarEl.className = `w-12 h-12 rounded-full flex items-center justify-center text-2xl mr-4 shadow-lg text-white transition-colors duration-300 ${bgClass}`;
    }

    if (typeEl) typeEl.innerText = roleText;

    // 3. 카운터 업데이트
    if (counterEl) {
        counterEl.innerText = `${index + 1} / ${chatLogs.length}`;
    }

    // 4. 버튼 활성화/비활성화 상태 업데이트
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    if (btnPrev) {
        btnPrev.disabled = (index === 0);
        btnPrev.style.opacity = index === 0 ? "0.5" : "1";
        btnPrev.style.cursor = index === 0 ? "not-allowed" : "pointer";
    }

    if (btnNext) {
        btnNext.disabled = (index === chatLogs.length - 1);
        btnNext.style.opacity = index === chatLogs.length - 1 ? "0.5" : "1";
        btnNext.style.cursor = index === chatLogs.length - 1 ? "not-allowed" : "pointer";
    }
}


// ============================================================
// 기존 기능 유지 (코스피 차트)
// ============================================================
async function renderKospiChart() {
    const KOSPI_API_URL = 'http://127.0.0.1:8000/kospi-data';

    try {
        const response = await fetch(KOSPI_API_URL);
        const data = await response.json();

        if (data.error) throw new Error(data.error);

        // 텍스트 정보 업데이트
        document.getElementById('kospi-price').innerText = data.price;
        const changeElem = document.getElementById('kospi-change');
        changeElem.innerText = `${data.change} (${data.diff})`;

        // 색상
        changeElem.className = data.isUp ? "kospi-change up" : "kospi-change down";

        // 차트 그리기
        const ctx = document.getElementById('kospiChart').getContext('2d');

        // 그라디언트
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        const color = data.isUp ? 'rgba(74, 222, 128, ' : 'rgba(239, 68, 68, ';
        gradient.addColorStop(0, color + '0.5)');
        gradient.addColorStop(1, color + '0.0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.chart_labels,
                datasets: [{
                    label: 'KOSPI',
                    data: data.chart_data,
                    borderColor: data.isUp ? '#4ade80' : '#ef4444',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        grid: { display: false, drawBorder: false },
                        ticks: { color: '#64748b', maxTicksLimit: 6 }
                    },
                    y: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#64748b' }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index',
                }
            }
        });

    } catch (error) {
        console.error("KOSPI Chart Error:", error);
        const wrapper = document.getElementById('kospi-wrapper');
        if(wrapper) wrapper.innerHTML = "<p style='color:gray; text-align:center; padding:2rem;'>코스피 데이터를 불러올 수 없습니다.</p>";
    }
}

// ============================================================
// 기존 기능 유지 (시장 요약 카드)
// ============================================================
async function renderRealMarketData() {
    const grid = document.getElementById('market-grid');
    const timeElem = document.getElementById('market-time');
    if(timeElem) timeElem.innerText = new Date().toLocaleString();

    const MARKET_API_URL = 'http://127.0.0.1:8000/market-summary';

    try {
        const response = await fetch(MARKET_API_URL);
        const marketData = await response.json();

        if (grid) grid.innerHTML = "";

        marketData.forEach(item => {
            const card = document.createElement('div');
            card.className = 'market-card';
            const changeClass = item.isUp ? 'up' : 'down';
            const changeIcon = item.isUp ? '▲' : '▼';

            card.innerHTML = `
                <div class="market-name"><span>${item.icon}</span> ${item.name}</div>
                <div class="market-price">${item.price}</div>
                <div class="market-change ${changeClass}">${changeIcon} ${item.change}</div>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        console.error("Market Grid Error:", error);
        if (grid) grid.innerHTML = `<p style="color:#94a3b8; text-align:center; width:100%;">데이터 로딩 실패 (서버 연결 확인)</p>`;
    }
}