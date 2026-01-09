async function askAgent() {
    const userInput = document.getElementById('userInput');
    const query = userInput.value.trim();
    const resultContainer = document.getElementById('resultContainer');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const sendBtn = document.getElementById('sendBtn');

    if (!query) return;

    // 1. UI 초기화 및 로딩 시작
    loadingDiv.style.display = 'flex';
    resultContainer.style.display = 'none'; // 일단 숨김
    resultDiv.innerText = '';
    sendBtn.disabled = true;

    try {
        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });

        const result = await response.json();
        console.log("백엔드 응답 데이터:", result); // 브라우저 콘솔에서 확인용

        // 2. 결과 표시 (container를 보이게 설정)
        resultContainer.style.display = 'block';
        
        // 데이터가 'data' 키에 들어있는지 확인 후 출력
        if (result && result.data) {
            resultDiv.innerText = result.data;
        } else {
            resultDiv.innerText = "응답 성공했으나 데이터 형식이 다릅니다: " + JSON.stringify(result);
        }

    } catch (error) {
        resultContainer.style.display = 'block';
        resultDiv.innerHTML = '<span style="color:red;">오류 발생: ' + error.message + '</span>';
    } finally {
        loadingDiv.style.display = 'none';
        sendBtn.disabled = false;
        userInput.value = ''; // 입력창 비우기
    }
}

// 엔터키 지원
document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') askAgent();
});
