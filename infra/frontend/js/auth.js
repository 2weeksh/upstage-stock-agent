const AUTH_API_BASE = '/api/auth';

let isUsernameChecked = false;
let isNicknameChecked = false;

document.addEventListener('DOMContentLoaded', () => {
    renderAuthNav();
    const usernameInput = document.getElementById('username');
    const nicknameInput = document.getElementById('nickname');
    const usernameMsg = document.getElementById('username-msg');
    const nicknameMsg = document.getElementById('nickname-msg');
    if (usernameInput) {
        usernameInput.addEventListener('input', () => {
            isUsernameChecked = false;
            if(usernameMsg) usernameMsg.innerText = ""; // 메시지도 초기화
        });
    }

    if (nicknameInput) {
        nicknameInput.addEventListener('input', () => {
            isNicknameChecked = false;
            if(nicknameMsg) nicknameMsg.innerText = ""; // 메시지도 초기화
        });
    }
});

// 1. 우측 상단 네비게이션
function renderAuthNav() {
    let navContainer = document.getElementById('auth-nav');
    if (!navContainer) {
        navContainer = document.createElement('div');
        navContainer.id = 'auth-nav';
        document.body.appendChild(navContainer);
    }

    const token = localStorage.getItem('accessToken');
    const nickname = localStorage.getItem('userNickname');

    if (token && nickname) {
        navContainer.innerHTML = `
            <span class="user-nickname">${nickname}님</span>
            <a href="mypage.html">마이페이지</a>
            <a href="#" onclick="handleLogout(event)">로그아웃</a>
        `;
    } else {
        navContainer.innerHTML = `
            <a href="login.html">로그인</a>
            <a href="signup.html">회원가입</a>
        `;
    }
}

// 2. 로그아웃 처리
function handleLogout(e) {
    e.preventDefault();
    if(confirm('로그아웃 하시겠습니까?')) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('userNickname');
        localStorage.removeItem('userJoinDate');
        alert('로그아웃 되었습니다.');
        window.location.href = '/';
    }
}

// 3. 로그인 체크 유틸리티
function isLoggedIn() {
    return !!localStorage.getItem('accessToken');
}

// 4. 로그인 API 요청
async function apiLogin(username, password) {
    try {
        const response = await fetch(`${AUTH_API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            if(data.access_token && data.nickname) {
                localStorage.setItem('accessToken', data.access_token); // 여기도 수정
                localStorage.setItem('userNickname', data.nickname);

                if(data.created_at) localStorage.setItem('userJoinDate', data.created_at);

                return true;
            } else {
                console.log("받은 데이터:", data); // 디버깅용 로그
                alert('서버 응답 오류: 데이터가 불완전합니다.');
                return false;
            }
        } else {
            alert('로그인 실패: 아이디 또는 비밀번호를 확인하세요.');
            return false;
        }
    } catch (error) {
        console.error('Login Error:', error);
        alert('서버 연결 중 오류가 발생했습니다.');
        return false;
    }
}

// 5. 회원가입 API 요청
async function apiSignup(username, password, nickname) {
    try {
        const response = await fetch(`${AUTH_API_BASE}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, nickname })
        });

        if (response.ok) {
            return true;
        } else {
            const errorData = await response.json();
            alert(`회원가입 실패: ${errorData.detail || '오류가 발생했습니다.'}`);
            return false;
        }
    } catch (error) {
        console.error('Signup Error:', error);
        alert('서버 연결 중 오류가 발생했습니다.');
        return false;
    }
}

// 6. 아이디 중복 확인
async function handleCheckUsername() {
    const usernameInput = document.getElementById('username');
    const msgBox = document.getElementById('username-msg');
    const username = usernameInput.value.trim();

    const regex = /^[A-Za-z0-9]{4,10}$/;
    if (!regex.test(username)) {
        msgBox.innerText = "아이디 규칙(영문+숫자, 4~10자)에 맞지 않습니다.";
        msgBox.style.color = "#ef4444";
        isUsernameChecked = false;
        return;
    }

    try {
        const response = await fetch(`${AUTH_API_BASE}/check-username/${username}`);
        const data = await response.json();

        msgBox.innerText = data.message;

        if (data.available) {
            msgBox.style.color = "#4ade80";
            isUsernameChecked = true; // [수정 4] 사용 가능할 때만 true 설정
        } else {
            msgBox.style.color = "#ef4444";
            isUsernameChecked = false;
        }

    } catch (error) {
        console.error(error);
        alert("서버 오류가 발생했습니다.");
        isUsernameChecked = false;
    }
}
async function handleCheckNickname() {
    const nicknameInput = document.getElementById('nickname');
    const msgBox = document.getElementById('nickname-msg');
    const nickname = nicknameInput.value.trim();

    if (nickname.length < 2) {
        msgBox.innerText = "닉네임은 2글자 이상이어야 합니다.";
        msgBox.style.color = "#ef4444";
        isNicknameChecked = false; // [수정 5] 실패 시 확인 상태 false
        return;
    }

    try {
        const response = await fetch(`${AUTH_API_BASE}/check-nickname/${nickname}`);
        const data = await response.json();

        msgBox.innerText = data.message;

        if (data.available) {
            msgBox.style.color = "#4ade80";
            isNicknameChecked = true; // [수정 6] 사용 가능할 때만 true 설정
        } else {
            msgBox.style.color = "#ef4444";
            isNicknameChecked = false;
        }

    } catch (error) {
        console.error(error);
        alert("서버 오류가 발생했습니다.");
        isNicknameChecked = false;
    }
}