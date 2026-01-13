document.addEventListener('DOMContentLoaded', () => {
    // 배경 애니메이션 (유지)
    const chartBg = document.getElementById('chartBg');
    if (chartBg) {
        for (let i = 0; i < 25; i++) { createCandle(chartBg); }
    }

    initUserInput();
    initBackButton();
    initLoadingPage();
});

// ------------------------------------------------
// 1. UI 초기화 및 이벤트 핸들러
// ------------------------------------------------

// 캔들 애니메이션 생성
function createCandle(container) {
    const candle = document.createElement('div');
    candle.className = 'candle';
    const leftPos = Math.random() * 100;
    const candleHeight = Math.random() * 80 + 40;
    const animDuration = Math.random() * 5 + 7;
    const animDelay = Math.random() * 10;
    const color = Math.random() > 0.4 ? '#10b981' : '#ef4444';

    candle.style.left = `${leftPos}%`;
    candle.style.height = `${candleHeight}px`;
    candle.style.backgroundColor = color;
    candle.style.animationDuration = `${animDuration}s`;
    candle.style.animationDelay = `${animDelay}s`;
    container.appendChild(candle);
}

// 질문 입력 페이지 초기화
function initUserInput() {
    const form = document.getElementById('analysisForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const question = document.getElementById('userQuestion').value;
        if (!question.trim()) {
            alert("질문을 작성하세요.");
            document.getElementById('userQuestion').focus();
            return;
        }
        localStorage.setItem('userQuestion', question);
        window.location.href = "../loading.html";
    });
}

// 뒤로가기 버튼 초기화
function initBackButton() {
    const backBtn = document.getElementById('back-btn-container');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            if (window.location.pathname.includes('loading.html')) {
                if(confirm("분석을 취소하고 돌아가시겠습니까?")) {
                    window.location.href = 'userInput.html';
                }
            } else {
                window.location.href = '/';
            }
        });
    }
}

// ------------------------------------------------
// 2. 로딩 페이지 로직 (핵심 수정 부분)
// ------------------------------------------------

function initLoadingPage() {
    const displayElement = document.getElementById('displayQuestion');
    const statusText = document.getElementById('agentStatusText');
    if (!displayElement) return;

    // 저장된 질문 표시
    const savedQuestion = localStorage.getItem('userQuestion');
    displayElement.innerText = savedQuestion || "질문이 없습니다.";

    // [삭제됨] startTextAnimation() 호출 제거 -> 백엔드 메시지로 대체
    // 초기 대기 메시지 설정
    if (statusText) statusText.innerText = "분석 서버와 연결 중...";

    // 분석 중지 버튼
    const stopBtn = document.getElementById('stopBtn');
    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            if(confirm("분석을 중지하고 돌아가시겠습니까?")) {
                window.location.href = 'userInput.html';
            }
        });
    }

    // 실제 데이터 요청 시작
    if (savedQuestion) {
        fetchAnalysisResult(savedQuestion);
    }
}

// ------------------------------------------------
// 3. 스트리밍 데이터 처리 (fetchAnalysisResult)
// ------------------------------------------------

// ------------------------------------------------
// 3. 스트리밍 데이터 처리 (fetchAnalysisResult)
// ------------------------------------------------

// ------------------------------------------------
// 3. 스트리밍 데이터 처리 (fetchAnalysisResult)
// ------------------------------------------------
async function fetchAnalysisResult(question) {
    console.log("백엔드로 분석 요청 전송:", question);
    const API_URL = '/api/v1/chat';

    const chatContainer = document.getElementById('chatContainer');

    // [핵심] 채팅 말풍선 추가 함수
    const addChat = (message) => {
        if (!chatContainer) return;

        // 1. 화자 및 스타일 결정 (기본값: 시스템 알림)
        let speaker = { type: 'system' };

        // 키워드에 따라 캐릭터 부여
        if (message.includes('차트') || message.includes('Chart')) {
            speaker = { type: 'agent', name: '차트 분석가', icon: '📈', theme: 'theme-chart' };
        } else if (message.includes('재무') || message.includes('Finance')) {
            speaker = { type: 'agent', name: '재무 분석가', icon: '💰', theme: 'theme-finance' };
        } else if (message.includes('뉴스') || message.includes('News')) {
            speaker = { type: 'agent', name: '뉴스 분석가', icon: '📰', theme: 'theme-news' };
        }
        // 사회자나 일반 시스템 메시지는 그대로 'system' 타입 유지

        // 2. HTML 요소 생성 (분기 처리)

        if (speaker.type === 'system') {
            // [A] 시스템 알림 스타일 (중앙 정렬, 아이콘 없음)
            const sysDiv = document.createElement('div');
            sysDiv.className = 'chat-system-message';
            sysDiv.innerText = message; // 예: "서버와 연결되었습니다."
            chatContainer.appendChild(sysDiv);
        }
        else {
            // [B] 에이전트 말풍선 스타일 (오른쪽 정렬, 아이콘 있음)
            const row = document.createElement('div');
            // 에이전트는 무조건 오른쪽(agent) 배치
            row.className = `chat-row agent ${speaker.theme}`;

            row.innerHTML = `
                <div class="chat-profile-icon">${speaker.icon}</div>
                <div class="chat-content">
                    <span class="chat-name">${speaker.name}</span>
                    <div class="chat-bubble">${message}</div>
                </div>
            `;
            chatContainer.appendChild(row);
        }

        // 스크롤 맨 아래로 이동
        chatContainer.scrollTop = chatContainer.scrollHeight;
    };

    // 초기 시스템 메시지
    addChat("서버와 안전하게 연결되었습니다.");

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_question: question })
        });

        if (!response.body) throw new Error("ReadableStream 미지원");

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const parsed = JSON.parse(line);

                    if (parsed.type === 'status') {
                        addChat(parsed.message);
                    }
                    else if (parsed.type === 'result') {
                        addChat("✅ 모든 데이터 분석이 완료되었습니다!");
                        addChat("잠시 후 결과 페이지로 이동합니다...");

                        setTimeout(() => {
                            saveDataAndSwitchUI(parsed.data);
                        }, 1500);
                        return;
                    }
                    else if (parsed.type === 'error') {
                        addChat(`⛔ 오류: ${parsed.message}`);
                        return;
                    }
                } catch (e) {
                    console.error("JSON Error:", e);
                }
            }
        }
    } catch (error) {
        addChat("서버 연결에 실패했습니다.");
    }
}
// ------------------------------------------------
// 4. 데이터 저장 및 화면 전환
// ------------------------------------------------

function saveDataAndSwitchUI(data) {
    // 데이터 로컬 스토리지 저장
    localStorage.setItem('analysis_summary', data.summary || "내용 없음");
    localStorage.setItem('analysis_conclusion', data.conclusion || "내용 없음");
    localStorage.setItem('analysis_log', data.discussion || "내용 없음");

    // 로딩 UI 숨기기
    const loadingContent = document.getElementById('loading-content');
    if (loadingContent) loadingContent.classList.add('hidden');

    // 성공 UI 표시
    const successContent = document.getElementById('success-content');
    if (successContent) {
        successContent.classList.remove('hidden');
        successContent.style.display = 'flex'; 
    }
}