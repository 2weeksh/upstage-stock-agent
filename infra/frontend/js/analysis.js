document.addEventListener('DOMContentLoaded', () => {
    // 1. 기본 정보 로드
    const dateElem = document.getElementById('report-date');
    if (dateElem) {
        dateElem.innerText = new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' });
    }

    const userQueryElement = document.getElementById('user-query-text');
    if (userQueryElement) {
        userQueryElement.innerText = localStorage.getItem('userQuestion') || "질문 없음";
    }

    // 2. 데이터 초기화 및 뷰어 실행
    initAnalysisData();
    initDiscussionSystem(); // 통합 뷰어 시스템

    // 3. 차트 및 시장 데이터
    renderKospiChart();
    renderRealMarketData();
});

// 줄바꿈 처리 헬퍼
function formatText(text) {
    if (!text) return "";
    return text.replace(/\n/g, '<br>');
}

function initAnalysisData() {
    const summaryData = localStorage.getItem('analysis_summary');
    const conclusionData = localStorage.getItem('analysis_conclusion');

    if(document.getElementById('res-summary')) document.getElementById('res-summary').innerHTML = formatText(summaryData);
    if(document.getElementById('res-conclusion')) document.getElementById('res-conclusion').innerHTML = formatText(conclusionData);
}

// ============================================================
// 🤖 [통합] 토론 뷰어 시스템 (슬라이드 & 채팅)
// ============================================================
let chatLogs = [];
let currentIndex = 0;

function initDiscussionSystem() {
    // 1. 데이터 로드

    const rawHistory = localStorage.getItem('analysis_chat_history');
    if (rawHistory) {
        try {
            chatLogs = JSON.parse(rawHistory);
        } catch (e) {
            console.error("채팅 기록 파싱 실패", e);
            chatLogs = [];
        }
    }

    // 2. 탭 전환 로직
    const tabSlider = document.getElementById('tab-slider');
    const tabChat = document.getElementById('tab-chat');
    const viewSlider = document.getElementById('view-slider');
    const viewChat = document.getElementById('view-chat');

    const activeClass = "px-6 py-3 text-base font-bold text-white bg-blue-600 rounded-xl transition-all shadow-lg";
    const inactiveClass = "px-6 py-3 text-base font-bold text-gray-400 bg-gray-800 rounded-xl transition-all hover:bg-gray-700 hover:text-white";
    const activeChatClass = "px-6 py-3 text-base font-bold text-white bg-green-600 rounded-xl transition-all shadow-lg";

    if (tabSlider && tabChat) {
        tabSlider.addEventListener('click', () => {
            // 탭 스타일 변경
            tabSlider.className = activeClass;
            tabChat.className = inactiveClass;

            // 뷰 전환
            viewSlider.classList.remove('hidden');
            viewChat.classList.add('hidden');
        });

        tabChat.addEventListener('click', () => {
            // 탭 스타일 변경
            tabChat.className = activeChatClass;
            tabSlider.className = inactiveClass;

            // 뷰 전환
            viewChat.classList.remove('hidden');
            viewSlider.classList.add('hidden');

            // 채팅 렌더링 (최초 1회)
            if (document.getElementById('chat-list').children.length === 0) {
                renderChatView();
            }
        });
    }

    // 3. 슬라이드 뷰어 초기화
    if (chatLogs.length > 0) {
        renderSliderLog(0);

        document.getElementById('btn-prev').addEventListener('click', () => {
            if (currentIndex > 0) { currentIndex--; renderSliderLog(currentIndex); }
        });
        document.getElementById('btn-next').addEventListener('click', () => {
            if (currentIndex < chatLogs.length - 1) { currentIndex++; renderSliderLog(currentIndex); }
        });
    } else {
        document.getElementById('viewer-message').innerText = "대화 기록이 없습니다.";
    }
}

// [모드 1] 슬라이드(카드) 렌더링
function renderSliderLog(index) {
    const log = chatLogs[index];
    if (!log) return;

    const speakerEl = document.getElementById('viewer-speaker');
    const typeEl = document.getElementById('viewer-type');
    const avatarEl = document.getElementById('viewer-avatar');
    const msgEl = document.getElementById('viewer-message');
    const counterEl = document.getElementById('viewer-counter');

    speakerEl.innerText = log.speaker;
    msgEl.innerHTML = formatText(log.message);

    const style = getAgentStyle(log.code);

    avatarEl.innerText = style.icon;
    avatarEl.className = `w-12 h-12 rounded-full flex items-center justify-center text-2xl mr-4 shadow-lg text-white ${style.bg}`;
    typeEl.innerText = style.role;
    counterEl.innerText = `${index + 1} / ${chatLogs.length}`;

    // 버튼 상태
    document.getElementById('btn-prev').disabled = (index === 0);
    document.getElementById('btn-prev').style.opacity = index === 0 ? 0.5 : 1;
    document.getElementById('btn-next').disabled = (index === chatLogs.length - 1);
    document.getElementById('btn-next').style.opacity = index === chatLogs.length - 1 ? 0.5 : 1;
}

// [모드 2] 채팅 리스트 렌더링 (좌우 배치)
function renderChatView() {
    const list = document.getElementById('chat-list');
    list.innerHTML = ""; // 초기화

    chatLogs.forEach(log => {
        const style = getAgentStyle(log.code);
        const isModerator = log.code === 'moderator';

        // Flex 방향 결정 (사회자는 오른쪽, 나머지는 왼쪽)
        const rowClass = isModerator ? 'flex-row-reverse' : 'flex-row';
        const alignClass = isModerator ? 'items-end' : 'items-start';
        const bubbleColor = isModerator ? 'bg-gray-700 text-gray-200' : 'bg-gray-800 text-white border border-gray-700';
        const marginClass = isModerator ? 'ml-auto' : 'mr-auto';

        // HTML 조립
        const row = document.createElement('div');
        row.className = `flex ${rowClass} ${alignClass} gap-3 w-full`;

        // 1. 아바타 (사회자는 아바타 생략하거나 작게 표시 가능, 여기선 통일성 있게 표시)
        const avatar = document.createElement('div');
        avatar.className = `flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-lg text-white shadow-md ${style.bg}`;
        avatar.innerText = style.icon;

        // 2. 내용물 (이름 + 말풍선)
        const content = document.createElement('div');
        content.className = `flex flex-col ${alignClass} max-w-[80%]`;

        const name = document.createElement('span');
        name.className = "text-xs text-gray-400 mb-1 font-bold";
        name.innerText = log.speaker;

        const bubble = document.createElement('div');
        bubble.className = `px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm whitespace-pre-wrap ${bubbleColor}`;
        // 사회자는 말풍선 꼬리 방향 다르게 (선택사항)
        if (isModerator) {
            bubble.style.borderTopRightRadius = '0';
        } else {
            bubble.style.borderTopLeftRadius = '0';
        }
        bubble.innerHTML = formatText(log.message);

        content.appendChild(name);
        content.appendChild(bubble);

        row.appendChild(avatar);
        row.appendChild(content);
        list.appendChild(row);
    });
}

// [공통] 에이전트 스타일 매핑
function getAgentStyle(code) {
    switch (code) {
        case 'chart': return { icon: '📈', role: 'Technical Analyst', bg: 'bg-blue-600' };
        case 'finance': return { icon: '💰', role: 'Financial Analyst', bg: 'bg-green-600' };
        case 'news': return { icon: '📰', role: 'News & Sentiment', bg: 'bg-purple-600' };
        case 'moderator': return { icon: '🎙️', role: 'Moderator', bg: 'bg-gray-600' };
        default: return { icon: '🤖', role: 'System', bg: 'bg-gray-500' };
    }
}

// ============================================================
// 기존 차트/시장 함수 유지
// ============================================================
async function renderKospiChart() {
    const KOSPI_API_URL = 'http://127.0.0.1:8000/kospi-data';
    try {
        const response = await fetch(KOSPI_API_URL);
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        document.getElementById('kospi-price').innerText = data.price;
        const changeElem = document.getElementById('kospi-change');
        changeElem.innerText = `${data.change} (${data.diff})`;
        changeElem.className = data.isUp ? "kospi-change up" : "kospi-change down";

        const ctx = document.getElementById('kospiChart').getContext('2d');
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
                    tension: 0.3, pointRadius: 0, pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { display: false }, y: { display: false } },
                interaction: { intersect: false, mode: 'index' }
            }
        });
    } catch (error) { console.error("KOSPI Error:", error); }
}

async function renderRealMarketData() {
    const grid = document.getElementById('market-grid');
    if(!grid) return;
    try {
        const response = await fetch('http://127.0.0.1:8000/market-summary');
        const marketData = await response.json();
        grid.innerHTML = "";
        marketData.forEach(item => {
            const card = document.createElement('div');
            card.className = 'market-card';
            card.innerHTML = `
                <div class="market-name"><span>${item.icon}</span> ${item.name}</div>
                <div class="market-price">${item.price}</div>
                <div class="market-change ${item.isUp ? 'up' : 'down'}">${item.isUp ? '▲' : '▼'} ${item.change}</div>
            `;
            grid.appendChild(card);
        });
        document.getElementById('market-time').innerText = new Date().toLocaleString();
    } catch (error) { console.error("Market Error:", error); }
}