document.addEventListener('DOMContentLoaded', () => {

    const relativeDiv = document.querySelector('#discussionContent .relative');
    if (relativeDiv) {
        const parent = relativeDiv.parentNode;
        while (relativeDiv.firstChild) {
            parent.insertBefore(relativeDiv.firstChild, relativeDiv);
        }
        parent.removeChild(relativeDiv);
    }

    const chatBox = document.querySelector('#view-chat .bg-gray-800');

    if (chatBox) {
        const header = chatBox.querySelector('.flex.items-center.gap-3.mb-4');
        if (header) {
            header.remove();
        }

        const chatContainer = chatBox.querySelector('.chat-container');

        if (chatContainer) {
            const parent = chatBox.parentNode;
            chatContainer.classList.add('chat-container');

            // 카드보기와 동일한 높이로 설정 (헤더 + 콘텐츠 + 버튼 영역 포함)
            chatContainer.style.minHeight = '700px';
            chatContainer.style.maxHeight = '700px';

            parent.replaceChild(chatContainer, chatBox);
        }
    }
    const cardBox = document.querySelector('#view-slider .bg-blue-600\\/10');

    // 1. 날짜 및 질문 표시
    const dateElem = document.getElementById('report-date');
    if (dateElem) {
        dateElem.innerText = new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' });
    }
    const userQueryElement = document.getElementById('user-query-text');
    if (userQueryElement) {
        userQueryElement.innerText = localStorage.getItem('userQuestion') || "질문 없음";
    }

    // ============================================================
    // ★ [히스토리 모드 확인]
    // ============================================================
    const historyMode = localStorage.getItem('history_mode');
    if (historyMode === 'true') {
        console.log("히스토리 다시보기 모드 진입");
        // 다시보기 모드에서는 자동 저장을 하지 않고, 저장된 데이터만 보여줍니다.
        // 데이터 복원 로직은 initAnalysisData()와 initDiscussionSystem() 내부에서 처리됨
    }

    // 2. 분석 데이터 및 뷰어 초기화
    initAnalysisData();
    initDiscussionSystem();

    // 3. 차트 및 시장 요약
    renderKospiChart();
    renderRealMarketData();

    // ============================================================
    // ★ [핵심 수정] 라이브 분석 결과 자동 저장 로직 추가
    // ============================================================
    // 히스토리 모드가 아니고, 분석 결과(요약)가 존재할 때만 저장 시도
    const hasSummary = localStorage.getItem('analysis_summary');
    const currentQuestion = localStorage.getItem('userQuestion');

    // 중복 저장 방지: 세션 스토리지에 마지막으로 저장한 질문을 기록해둠
    const lastSavedQuestion = sessionStorage.getItem('last_saved_question');

    // 디버깅 로그
    console.log("=== DB 저장 조건 체크 ===");
    console.log("historyMode:", historyMode);
    console.log("hasSummary:", !!hasSummary);
    console.log("currentQuestion:", currentQuestion);
    console.log("lastSavedQuestion:", lastSavedQuestion);

    if (historyMode !== 'true' && hasSummary && currentQuestion) {
        if (currentQuestion !== lastSavedQuestion) {
            console.log("✅ 새로운 분석 결과 감지 -> DB 저장 시도");
            window.saveAnalysisToDB().then(() => {
                // 저장 성공 여부와 관계없이 시도했음을 표시하여 무한 루프 방지
                sessionStorage.setItem('last_saved_question', currentQuestion);
            });
        } else {
            console.log("⏭️ 이미 저장된 분석 결과입니다. (저장 건너뜀)");
        }
    } else {
        console.log("❌ 저장 조건 미충족 - historyMode가 true이거나 데이터 없음");
    }

    // PDF 다운로드 버튼 이벤트 연결
    const pdfBtn = document.getElementById('btn-download-pdf');
    if (pdfBtn) {
        pdfBtn.addEventListener('click', generatePDF);
    }
});
function generatePDF() {
    // 1. 데이터 가져오기
    const rawJson = localStorage.getItem('analysis_summary');
    if (!rawJson) {
        alert("리포트 데이터가 없습니다. 분석이 완료되었는지 확인해주세요.");
        return;
    }

    let data;
    try {
        data = JSON.parse(rawJson);
    } catch (e) {
        console.error("JSON Error:", e);
        alert("데이터 파싱 오류");
        return;
    }

    // --- 2. 데이터 매핑 시작 ---

    // [Header]
    const info = data.report_info || {};
    document.getElementById('pdf-title').innerText = info.title || "Investment Report";
    document.getElementById('pdf-symbol').innerText = info.symbol || "UNKNOWN";
    document.getElementById('pdf-date').innerText = info.date || new Date().toISOString().slice(0, 7);

    // [Summary]
    const summary = data.header_summary || {};
    const metrics = summary.key_metrics || {};

    // Rating Badge 처리
    const ratingEl = document.getElementById('pdf-rating-badge');
    ratingEl.innerText = summary.rating?.label || "N/A";
    const rColor = summary.rating?.color;
    if (rColor === 'red') ratingEl.className = "text-3xl font-black text-red-600";
    else if (rColor === 'blue') ratingEl.className = "text-3xl font-black text-blue-600";
    else ratingEl.className = "text-3xl font-black text-slate-400"; // gray

    document.getElementById('pdf-target').innerText = summary.target_price ? `${Number(summary.target_price).toLocaleString()}원` : "-";
    document.getElementById('pdf-current').innerText = summary.current_price ? `${Number(summary.current_price).toLocaleString()}원` : "-";
    document.getElementById('pdf-upside').innerText = summary.upside_ratio || "-";

    document.getElementById('pdf-per').innerText = metrics.PER || "-";
    document.getElementById('pdf-pbr').innerText = metrics.PBR || "-";
    document.getElementById('pdf-roe').innerText = metrics.ROE || "-";

    // [Investment Thesis] - Buy vs Sell
    const thesis = data.investment_thesis || {};

    // 1) Buy Side
    const buyList = document.getElementById('pdf-buy-points');
    buyList.innerHTML = "";
    if (thesis.buy_side) {
        thesis.buy_side.forEach(item => {
            buyList.innerHTML += `
                <li class="flex items-start gap-2">
                    <span class="text-blue-500 font-bold mt-0.5">✓</span>
                    <div>
                        <strong class="block text-slate-800">${item.point}</strong>
                        <span class="text-slate-600 text-xs leading-tight">${item.detail}</span>
                    </div>
                </li>`;
        });
    }

    // 2) Sell Side
    const sellList = document.getElementById('pdf-sell-points');
    sellList.innerHTML = "";
    if (thesis.sell_side) {
        thesis.sell_side.forEach(item => {
            sellList.innerHTML += `
                <li class="flex items-start gap-2">
                    <span class="text-red-500 font-bold mt-0.5">⚠</span>
                    <div>
                        <strong class="block text-slate-800">${item.point}</strong>
                        <span class="text-slate-600 text-xs leading-tight">${item.detail}</span>
                    </div>
                </li>`;
        });
    }

    // [Consensus Clash]
    const clash = thesis.consensus_clash || {};
    document.getElementById('pdf-market-view').innerText = clash.market_view || "-";
    document.getElementById('pdf-agent-view').innerText = clash.agent_view || "-";

    // [QnA Insights]
    const qnaList = document.getElementById('pdf-qna-list');
    qnaList.innerHTML = "";
    if (data.qna_insights) {
        data.qna_insights.forEach(qna => {
            // Debate Context를 문자열로 합치기
            const contextHtml = qna.debate_context.map(d =>
                `<span class="mr-2"><b class="${d.role === '재무 분석가' ? 'text-green-600' : 'text-blue-600'}">${d.role}</b>: ${d.content}</span>`
            ).join("<br>");

            qnaList.innerHTML += `
                <div class="bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <h4 class="font-bold text-slate-800 mb-2">Q. ${qna.question}</h4>
                    <div class="text-xs text-slate-600 mb-3 pl-2 border-l-2 border-slate-300">
                        ${contextHtml}
                    </div>
                    <div class="flex items-start gap-2 bg-yellow-50 p-2 rounded text-xs text-yellow-900 font-medium">
                        <span>💡 <strong>Insight:</strong> ${qna.strategic_importance}</span>
                    </div>
                </div>`;
        });
    }

    // [Valuation Logic & Peers]
    const valLogic = data.valuation_logic || {};
    document.getElementById('pdf-val-method').innerText = valLogic.method || "";

    const peerBody = document.getElementById('pdf-peer-body');
    peerBody.innerHTML = "";
    if (valLogic.peer_group) {
        valLogic.peer_group.forEach(peer => {
            peerBody.innerHTML += `
                <tr class="border-b border-slate-100 last:border-0">
                    <td class="p-2 font-bold">${peer.company}</td>
                    <td class="p-2">${peer.per}</td>
                    <td class="p-2">${peer.pbr}</td>
                </tr>`;
        });
    }

    // [Financial Estimates]
    const financials = data.financials || {};
    const finHead = document.getElementById('pdf-fin-head');
    const finBody = document.getElementById('pdf-fin-body');

    if (financials.columns) {
        let hHtml = "<th></th>"; // empty corner
        financials.columns.forEach(col => hHtml += `<th class="p-2">${col}</th>`);
        finHead.innerHTML = hHtml;
    }
    if (financials.rows) {
        finBody.innerHTML = "";
        financials.rows.forEach(row => {
            let rHtml = `<td class="p-2 font-bold bg-slate-50 text-left">${row.category}</td>`;
            row.values.forEach(v => rHtml += `<td class="p-2 border-l border-slate-100">${v}</td>`);
            finBody.innerHTML += `<tr class="border-b border-slate-200 last:border-0">${rHtml}</tr>`;
        });
    }
    document.getElementById('pdf-earnings-insight').innerText = financials.earnings_insight || "";

    // [Risk Scenarios]
    const riskBody = document.getElementById('pdf-risk-body');
    riskBody.innerHTML = "";
    if (data.risk_scenarios) {
        data.risk_scenarios.forEach(risk => {
            riskBody.innerHTML += `
                <tr>
                    <td class="p-2 font-bold text-red-700 align-top">${risk.event}</td>
                    <td class="p-2 text-slate-600 align-top">${risk.impact}</td>
                </tr>`;
        });
    }

    // [Final Verdict]
    const verdict = data.final_verdict || {};
    document.getElementById('pdf-short-term').innerText = verdict.short_term || "-";
    document.getElementById('pdf-long-term').innerText = verdict.long_term || "-";
    document.getElementById('pdf-action-plan').innerText = verdict.action_plan || "-";
    document.getElementById('pdf-closing-thought').innerText = verdict.closing_thought ? `"${verdict.closing_thought}"` : "";


    // --- 3. PDF 저장 실행 ---
    const element = document.getElementById('pdf-content');
    const btn = document.getElementById('btn-download-pdf');
    const originalText = btn.innerHTML;

    btn.innerHTML = "⏳ 생성 중...";
    btn.disabled = true;

    const opt = {
        margin: 0,
        filename: `${info.symbol}_Report.pdf`,
        image: { type: 'jpeg', quality: 1 },
        html2canvas: { scale: 2, useCORS: true, scrollY: 0 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().from(element).set(opt).save().then(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

// 줄바꿈 처리 헬퍼

function renderMarkdown(mdText) {
    if (!mdText) return "데이터 로딩 중...";
    const tempText = mdText.replace(/~/g, '@@TILDE@@');
    let html = marked.parse(tempText);
    html = html.replace(/@@TILDE@@/g, '~');
    return html;
}

function initAnalysisData() {
    const summaryData = localStorage.getItem('analysis_summary');
    const conclusionData = localStorage.getItem('analysis_conclusion');

    if (document.getElementById('res-summary')) {
        const el = document.getElementById('res-summary');
        el.classList.add('markdown-body');
        el.innerHTML = renderMarkdown(summaryData);
    }

    if (document.getElementById('res-conclusion')) {
        const el = document.getElementById('res-conclusion');
        el.classList.add('markdown-body');
        el.innerHTML = renderMarkdown(conclusionData);
    }
}

// ============================================================
// 토론 뷰어 시스템 (토글 + 탭)

let chatLogs = [];
let currentIndex = 0;

function initDiscussionSystem() {
    //토글 버튼 (전체 접기/펼치기) 기능 복구
    const toggleBtn = document.getElementById('toggleDiscussionBtn');
    const wrapper = document.getElementById('discussionWrapper'); // 탭+뷰어를 감싸는 div
    const toggleIcon = document.getElementById('toggleIcon');

    //토글
    if (toggleBtn && wrapper) {
        toggleBtn.addEventListener('click', () => {
            wrapper.classList.toggle('hidden');
        });
    }

    // 2. 데이터 로드
    if (!chatLogs.length) {
        const rawHistory = localStorage.getItem('analysis_chat_history');
        if (rawHistory) {
            try {
                chatLogs = JSON.parse(rawHistory);
            } catch (e) {
                console.error("채팅 기록 파싱 실패", e);
                chatLogs = [];
            }
        }
    }
    // 3. 채팅 보기 자동 렌더링
    if (chatLogs.length > 0) {
        renderChatView();
    } else {
        const msgEl = document.getElementById('chat-list');
        if (msgEl) msgEl.innerText = "대화 기록이 없습니다.";
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

    if (speakerEl) speakerEl.innerText = log.speaker;
    if (msgEl) {
        msgEl.classList.add('markdown-body');
        msgEl.innerHTML = renderMarkdown(log.message);
    }

    if (avatarEl) {
        const style = getAgentStyle(log.code);
        avatarEl.innerHTML = style.icon;
        avatarEl.className = style.color + " w-14 h-14 rounded-full flex items-center justify-center text-3xl shadow-lg border-2 border-gray-500";
        if (typeEl) typeEl.innerText = style.role;
    }

    if (counterEl) counterEl.innerText = `${index + 1} / ${chatLogs.length}`;

    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    if (btnPrev) {
        btnPrev.disabled = (index === 0);
        btnPrev.style.opacity = index === 0 ? 0.5 : 1;
    }
    if (btnNext) {
        btnNext.disabled = (index === chatLogs.length - 1);
        btnNext.style.opacity = index === chatLogs.length - 1 ? 0.5 : 1;
    }
}

// 채팅 리스트 렌더링 (아이콘 상단 고정 수정)
function renderChatView() {
    const list = document.getElementById('chat-list');
    if (!list) return;
    list.innerHTML = "";

    chatLogs.forEach(log => {
        const style = getAgentStyle(log.code);
        const isModerator = log.code === 'moderator';

        // 1. 레이아웃 방향 결정
        // 사회자: 왼쪽(정방향) / 전문가: 오른쪽(역방향)
        const rowClass = isModerator ? 'flex-row' : 'flex-row-reverse';

        // 2. 텍스트 정렬 결정 (말풍선 내부 정렬)
        // 사회자: 왼쪽 정렬 / 전문가: 오른쪽 정렬
        const colAlign = isModerator ? 'items-start' : 'items-end';

        const bubbleColor = isModerator
            ? 'bg-white text-gray-800 shadow-md border border-gray-200'
            : 'bg-white text-gray-800 border border-gray-200 shadow-md';

        // 3. Row 생성 (여기서 items-start를 줘서 아바타를 무조건 위로 올림)
        const row = document.createElement('div');
        row.className = `flex ${rowClass} items-start gap-3 w-full`;

        // 아바타
        const avatar = document.createElement('div');
        avatar.className = style.color;
        avatar.innerHTML = style.icon;

        // 내용물 Wrapper (이름 + 말풍선 정렬은 colAlign 사용)
        const content = document.createElement('div');
        content.className = `flex flex-col ${colAlign} max-w-[80%]`;

        // 이름
        const name = document.createElement('span');
        name.className = "text-xs text-gray-400 mb-1 font-bold";
        name.innerText = log.speaker;

        // 말풍선
        const bubble = document.createElement('div');
        bubble.className = `px-5 py-3 rounded-2xl text-base leading-relaxed whitespace-pre-wrap ${bubbleColor}`;

        // 꼬리 방향
        if (isModerator) bubble.style.borderTopLeftRadius = '0';
        else bubble.style.borderTopRightRadius = '0';

        bubble.classList.add('markdown-body');
        bubble.innerHTML = renderMarkdown(log.message);

        content.appendChild(name);
        content.appendChild(bubble);
        row.appendChild(avatar);
        row.appendChild(content);
        list.appendChild(row);
    });
}


function getAgentStyle(code) {
    switch (code) {
        case 'chart': return {
            icon: `<img src="img/chart.png" alt="차트 분석가" class="w-8 h-8 mr-1.5">`,
            role: 'Technical Analyst',
            color: 'text-red-300',
            border: 'border-red-500/30',
            bg: 'bg-red-500/10'
        };
        case 'finance': return {
            icon: `<img src="img/finance.png" alt="재무 분석가" class="w-8 h-8 mr-1.5">`,
            role: 'Financial Analyst',
            color: 'text-green-300',
            border: 'border-green-500/30',
            bg: 'bg-green-500/10'
        };
        case 'news': return {
            icon: `<img src="img/news.png" alt="뉴스 분석가" class="w-8 h-8 mr-1.5">`,
            role: 'News Analyst',
            color: 'text-blue-300',
            border: 'border-blue-500/30',
            bg: 'bg-blue-500/10'
        };
        case 'moderator': return {
            icon: `<svg class="w-8 h-8 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                    </svg>`,
            role: 'Moderator',
            color: 'text-gray-300',
            border: 'border-gray-500/30',
            bg: 'bg-gray-500/10'
        };
        default: return {
            icon: `<svg class="w-8 h-8 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>`,
            role: 'System',
            color: 'text-gray-300',
            border: 'border-gray-500/30',
            bg: 'bg-gray-500/10'
        };
    }
}

// ============================================================
// 기존 차트/시장 함수
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
    if (!grid) return;
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

// ============================================================
// ★ [저장 함수] DB 저장 로직 (필수)
// ============================================================
window.saveAnalysisToDB = async function () {
    const token = localStorage.getItem('accessToken');
    if (!token) {
        console.log("비로그인 상태 -> 저장 안 함");
        return;
    }

    try {
        const response = await fetch('/api/history/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                question: localStorage.getItem('userQuestion') || "",
                summary: localStorage.getItem('analysis_summary') || "",
                conclusion: localStorage.getItem('analysis_conclusion') || "",
                chat_logs: localStorage.getItem('analysis_chat_history') || "[]"
            })
        });

        if (response.ok) {
            console.log("✅ 히스토리 DB 저장 성공!");
        } else {
            console.error("❌ 저장 실패:", await response.text());
        }
    } catch (e) {
        console.error("DB 저장 중 통신 에러:", e);
    }
};
