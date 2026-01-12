document.addEventListener('DOMContentLoaded', () => {
    // 배경 애니메이션
    const chartBg = document.getElementById('chartBg');
    if (chartBg) {
        for (let i = 0; i < 25; i++) { createCandle(chartBg); }
    }

    initUserInput();
    initBackButton();
    initLoadingPage();
});


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

// userInput 페이지
// 질문 입력 후 버튼 -> 로컬 저장
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

// 뒤로가기
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

// Loading 페이지
function initLoadingPage() {
    const displayElement = document.getElementById('displayQuestion');
    if (!displayElement) return; 

    // 저장된 질문 표시
    const savedQuestion = localStorage.getItem('userQuestion');
    displayElement.innerText = savedQuestion || "질문이 없습니다.";

    // 텍스트 애니메이션
    startTextAnimation();

    // 분석 중지 버튼
    const stopBtn = document.getElementById('stopBtn');
    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            if(confirm("분석을 중지하고 돌아가시겠습니까?")) {
                window.location.href = 'userInput.html';
            }
        });
    }

    // 데이터 요청 시작 
    if (savedQuestion) {
        fetchAnalysisResult(savedQuestion);
    }
}

// 텍스트 반복
function startTextAnimation() {
    const statusText = document.getElementById('agentStatusText');
    if (!statusText) return; 

    const messages = [
        "차트 분석가가 분석 중입니다... (1/4)",
        "재무 분석가가 분석 중입니다... (2/4)",
        "뉴스 감성 분석가가 분석 중입니다... (3/4)",
        "투자 전략가가 분석 중입니다... (4/4)"
    ];
    let msgIndex = 0;
    
    window.statusInterval = setInterval(() => {
        msgIndex = (msgIndex + 1) % messages.length;
        statusText.style.opacity = 0; 
        setTimeout(() => {
            statusText.innerText = messages[msgIndex];
            statusText.style.opacity = 1;
        }, 300);
    }, 1500);
}

// ------------------------------------------------
// 실제 데이터 받기
// infra/frontend/js/script.js

async function fetchAnalysisResult(question) {
    console.log("백엔드로 분석 요청 전송:", question);

    // 실제 백엔드 에이전트 주소 (prefix 확인 필수)
    const API_URL = '/api/v1/chat';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // 백엔드의 UserRequest 모델(user_question)과 이름을 맞춰야 합니다.
            body: JSON.stringify({ user_question: question })
        });

        if (!response.ok) {
            throw new Error(`서버 응답 오류: ${response.status}`);
        }

        const data = await response.json();
        console.log("백엔드로부터 받은 데이터:", data);

        // 데이터 저장 및 화면 전환 (이미 작성된 함수 호출)
        saveDataAndSwitchUI(data);

    } catch (error) {
        console.error("통신 에러 발생:", error);
        alert("서버와 연결할 수 없습니다. 백엔드가 켜져 있는지 확인하세요.");

        // 테스트를 위해 실패 시 시뮬레이션이라도 돌리고 싶다면 아래 주석 해제
        // runSimulation();
    }
}

// ------------------------------------------------
// 테스트: 5초 대기 후 UI 전환(임의)
function runSimulation() {

    setTimeout(() => {
        const mockData = {
            summary: "요약",
            conclusion: "결론",
            discussion: "분석 내용"
        };

        saveDataAndSwitchUI(mockData);

    }, 5000); 
}

// 데이터 저장 및 화면 전환 처리
function saveDataAndSwitchUI(data) {
    // 데이터 나눠서 저장
    localStorage.setItem('analysis_summary', data.summary || "내용 없음");
    localStorage.setItem('analysis_conclusion', data.conclusion || "내용 없음");
    localStorage.setItem('analysis_log', data.discussion || "내용 없음");

    // 로딩 애니메이션 중지
    if (window.statusInterval) clearInterval(window.statusInterval);

    // UI 전환 -> 완료
    const loadingContent = document.getElementById('loading-content');
    if (loadingContent) loadingContent.classList.add('hidden');

    const successContent = document.getElementById('success-content');
    if (successContent) {
        successContent.classList.remove('hidden');
        successContent.style.display = 'flex'; 
    }
}