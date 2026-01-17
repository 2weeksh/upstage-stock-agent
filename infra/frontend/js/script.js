document.addEventListener('DOMContentLoaded', () => {
    // 배경 애니메이션
    const chartBg = document.getElementById('chartBg');
    if (chartBg) {
        for (let i = 0; i < 25; i++) { createCandle(chartBg); }
    }

    initUserInput();
    initLoadingPage();
});

//  UI 초기화 및 이벤트 핸들러

// 캔들 애니메이션
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

const textarea = document.getElementById('userQuestion');
const form = document.getElementById('analysisForm');

textarea.addEventListener('keydown', (e) => {
    // 엔터키이고, 쉬프트키가 눌리지 않았을 때만 제출
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // 줄바꿈 방지
        form.dispatchEvent(new Event('submit')); // 폼 제출 이벤트 발생
    }
});


// 로딩 페이지
function initLoadingPage() {
    const displayElement = document.getElementById('displayQuestion');
    const statusText = document.getElementById('agentStatusText');
    if (!displayElement) return;

    // 저장된 질문 표시
    const savedQuestion = localStorage.getItem('userQuestion');
    displayElement.innerText = savedQuestion || "질문이 없습니다.";

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

async function fetchAnalysisResult(question) {
    console.log("백엔드로 분석 요청 전송:", question);
    const API_URL = '/api/v1/chat';

    const chatContainer = document.getElementById('chatContainer');

    // [핵심] speaker 정보를 받아 스타일을 결정하는 함수
    const addChat = (message, speakerCode = 'system') => {
        if (!chatContainer) return;

        // 1. 화자 설정 (기본값: 시스템)
        let config = { type: 'system' };

        // 백엔드에서 보낸 speaker 코드에 따라 매핑
        if (speakerCode === 'chart') {
            config = { type: 'agent', name: '차트 분석가', icon: '<img src="img/chart.png" class="agent-icon" alt="차트">', theme: 'theme-chart' };
        } else if (speakerCode === 'finance') {
            config = { type: 'agent', name: '재무 분석가', icon: '<img src="img/finance.png" class="agent-icon" alt="재무">', theme: 'theme-finance' };
        } else if (speakerCode === 'news') {
            config = { type: 'agent', name: '뉴스 분석가', icon: '<img src="img/news.png" class="agent-icon" alt="뉴스">', theme: 'theme-news' };
        }
        // system인 경우는 기본값 유지

        // 2. HTML 생성
        if (config.type === 'system') {
            const sysDiv = document.createElement('div');
            sysDiv.className = 'chat-system-message';
            sysDiv.innerText = message;
            chatContainer.appendChild(sysDiv);
        } else {
            const row = document.createElement('div');
            // 에이전트는 무조건 오른쪽(agent)
            row.className = `chat-row agent ${config.theme}`;
            row.innerHTML = `
                <div class="chat-profile-icon">${config.icon}</div>
                <div class="chat-content">
                    <span class="chat-name">${config.name}</span>
                    <div class="chat-bubble">${message}</div>
                </div>
            `;
            chatContainer.appendChild(row);
        }

        chatContainer.scrollTop = chatContainer.scrollHeight;
    };

    addChat("서버와 안전하게 연결되었습니다.", "system");

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

                    // parsed.speaker 값을 addChat에 전달 (핵심!)
                    if (parsed.type === 'status') {
                        addChat(parsed.message, parsed.speaker);
                    }
                    else if (parsed.type === 'result') {
                        addChat("✅ 모든 데이터 분석이 완료되었습니다!", "system");
                        addChat("결과 리포트로 이동합니다...", "system");

                        setTimeout(() => {
                            saveDataAndSwitchUI(parsed.data);
                        }, 1500);
                        return;
                    }
                    else if (parsed.type === 'error') {
                        addChat(`⛔ 오류: ${parsed.message}`, "system");
                        return;
                    }
                } catch (e) {
                    console.error("JSON Error:", e);
                }
            }
        }
    } catch (error) {
        addChat("서버 연결에 실패했습니다.", "system");
    }
}
// ------------------------------------------------
// 4. 데이터 저장 및 화면 전환
// ------------------------------------------------

function saveDataAndSwitchUI(data) {
    // 1. 텍스트 데이터 저장
    localStorage.setItem('analysis_summary', data.summary || "내용 없음");
    localStorage.setItem('analysis_conclusion', data.conclusion || "내용 없음");

    // [중요] discussion_log 배열을 JSON 문자열로 저장 (없으면 빈 배열)
    const chatHistory = data.discussion_log || [];
    localStorage.setItem('analysis_chat_history', JSON.stringify(chatHistory));

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