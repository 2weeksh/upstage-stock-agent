document.addEventListener('DOMContentLoaded', () => {
    // 날짜 및 질문 표시
    const dateElem = document.getElementById('report-date');
    if (dateElem) {
        const today = new Date();
        dateElem.innerText = today.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' });
    }
    const userQueryElement = document.getElementById('user-query-text');
    const savedQuestion = localStorage.getItem('userQuestion');
    if (userQueryElement) userQueryElement.innerText = savedQuestion || "질문 없음";

    // 분석 데이터 표시
    initAnalysisData();

    // 시장 요약
    renderKospiChart();     // 코스피 그래프
    renderRealMarketData(); // 8개 카드
});

function initAnalysisData() { 
    const summaryData = localStorage.getItem('analysis_summary');
    const conclusionData = localStorage.getItem('analysis_conclusion');
    const logData = localStorage.getItem('analysis_log');
    if(document.getElementById('res-summary')) document.getElementById('res-summary').innerText = summaryData || "로딩 중...";
    if(document.getElementById('res-conclusion')) document.getElementById('res-conclusion').innerText = conclusionData || "로딩 중...";
    if(document.getElementById('res-discussion')) document.getElementById('res-discussion').innerText = logData || "로딩 중...";
    
    const toggleBtn = document.getElementById('toggleDiscussionBtn');
    const discussionContent = document.getElementById('discussionContent');
    if (toggleBtn && discussionContent) {
        toggleBtn.addEventListener('click', () => {
            discussionContent.classList.toggle('hidden');
            const icon = toggleBtn.querySelector('svg');
            icon.style.transform = discussionContent.classList.contains('hidden') ? "rotate(0deg)" : "rotate(180deg)";
        });
    }
}

// ============================================================
// 코스피 차트
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
        if (data.isUp) {
            changeElem.className = "kospi-change up";
        } else {
            changeElem.className = "kospi-change down";
        }

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
        document.getElementById('kospi-wrapper').innerHTML = "<p style='color:gray; text-align:center; padding:2rem;'>코스피 데이터를 불러올 수 없습니다.</p>";
    }
}

// ============================================================
// 시장 요약 렌더링

async function renderRealMarketData() {
    const grid = document.getElementById('market-grid');
    const timeElem = document.getElementById('market-time');
    if(timeElem) timeElem.innerText = new Date().toLocaleString();

    const MARKET_API_URL = 'http://127.0.0.1:8000/market-summary';

    try {
        const response = await fetch(MARKET_API_URL);
        const marketData = await response.json();

        grid.innerHTML = ""; 

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
        grid.innerHTML = `<p style="color:#94a3b8; text-align:center; width:100%;">데이터 로딩 실패 (서버 연결 확인)</p>`;
    }
}