// User flow: login, dashboard, start interview
function handleLogin() {
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;

  if (!name || !email) {
    alert('Please enter name and email');
    return;
  }

  localStorage.setItem('userName', name);
  localStorage.setItem('userEmail', email);
  localStorage.setItem('isLoggedIn', 'true');
  showDashboard(email);
}

function showDashboard(email) {
  document.getElementById('login-section').classList.add('hidden');
  document.getElementById('dashboard-section').classList.remove('hidden');
  loadUserHistory(email);
}

async function startInterview() {
  document.getElementById('dashboard-section').classList.add('hidden');
  document.getElementById('question-section').classList.remove('hidden');

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const questionCount = document.getElementById("question-count").value;
  const difficulty = document.getElementById("difficulty").value;

  if (!name || !email) {
    alert("Please enter your name and email!");
    return;
  }

  const savedSessionId = localStorage.getItem("interviewSessionId");
  const savedEmail = localStorage.getItem("interviewEmail");

  if (savedSessionId && savedEmail && savedEmail.toLowerCase() === email.toLowerCase()) {
    window.sessionId = savedSessionId;
    console.log("Resuming existing session:", window.sessionId);
  } else {
    const res = await fetch("/interview/start_session/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        email,
        question_count: parseInt(questionCount),
        difficulty: difficulty
      })
    });

    const data = await res.json();
    if (!data.session_id) {
      alert("Error starting session!");
      return;
    }

    window.sessionId = data.session_id;
    localStorage.setItem("interviewSessionId", window.sessionId);
    localStorage.setItem("interviewEmail", email);
  }

  loadNextQuestion();
}
