let sessionId = null;
let currentQuestion = null;

// ==================== INITIALIZATION ====================
window.addEventListener("DOMContentLoaded", function () {
  loadTopics();
  checkExistingSession();
});

// ==================== SESSION MANAGEMENT ====================
function clearSession() {
  localStorage.removeItem("interviewSessionId");
  localStorage.removeItem("interviewEmail");
  sessionId = null;
  location.reload();
}

function checkExistingSession() {
  const savedSessionId = localStorage.getItem("interviewSessionId");
  const savedEmail = localStorage.getItem("interviewEmail");

  if (savedSessionId && savedEmail) {
    sessionId = savedSessionId;
    document.getElementById("email").value = savedEmail;
    showDashboard(savedEmail);
    document.getElementById("dashboard-section").classList.add("hidden");
    document.getElementById("question-section").classList.remove("hidden");
    loadNextQuestion();
  }
}

// ==================== USER FLOW ====================
function handleLogin() {
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;

  if (!name || !email) {
    alert('Please enter name and email');
    return;
  }

  localStorage.setItem('userName', name);
  localStorage.setItem('userEmail', email);
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
    sessionId = savedSessionId;
    console.log("Resuming existing session:", sessionId);
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

    sessionId = data.session_id;
    localStorage.setItem("interviewSessionId", sessionId);
    localStorage.setItem("interviewEmail", email);
  }

  loadNextQuestion();
}

// ==================== QUESTION FLOW ====================
async function loadNextQuestion() {
  if (!sessionId) {
    alert("Session expired. Please start a new interview.");
    clearSession();
    return;
  }

  document.getElementById("loader").classList.remove("hidden");
  document.getElementById("next-btn").disabled = true;

  try {
    const topicSelect = document.getElementById("topic");
    const selectedTopics = Array.from(topicSelect.selectedOptions)
      .map(opt => opt.value)
      .filter(topic => topic !== "");
    const topicParam = selectedTopics.join(',');

    const res = await fetch(`/interview/next-question/?session_id=${sessionId}&topic=${topicParam}`);
    const data = await res.json();

    if (data.error) {
      alert("Error loading question: " + data.error);
      return;
    }

    if (data.interview_complete === true) {
      document.getElementById("question-section").classList.add("hidden");
      document.getElementById("summary-section").classList.remove("hidden");
      showSummary();
      return;
    }

    currentQuestion = data;
    document.getElementById("question-text").textContent = data.question_text;
    document.getElementById("feedback").textContent = "";
    document.getElementById("answer").value = "";
    
    document.getElementById("next-btn").classList.add("hidden");
    document.getElementById("submit-btn").classList.remove("hidden");
    document.getElementById("submit-btn").disabled = false;

    document.getElementById("progress").textContent = data.session_progress || "";
  } catch (error) {
    alert("Error loading question: " + error.message);
  } finally {
    document.getElementById("loader").classList.add("hidden");
    document.getElementById("next-btn").disabled = false;
  }
}

async function submitAnswer() {
  const answer = document.getElementById("answer").value.trim();
  const feedbackEl = document.getElementById("feedback");

  if (!answer) {
    alert("Please type your answer before submitting!");
    return;
  }

  document.getElementById("loader").classList.remove("hidden");
  document.getElementById("submit-btn").disabled = true;
  feedbackEl.textContent = "";
  feedbackEl.classList.remove("correct-glow", "wrong-glow");

  try {
    const res = await fetch("/interview/submit-answer/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        question_id: currentQuestion.question_id,
        user_answer: answer
      })
    });

    const data = await res.json();
    feedbackEl.textContent = data.feedback || "No feedback available.";
    feedbackEl.classList.add("feedback");

    if (data.is_correct) {
      feedbackEl.classList.add("correct-glow");
    } else {
      feedbackEl.classList.add("wrong-glow");
    }

    setTimeout(() => {
      feedbackEl.classList.remove("correct-glow", "wrong-glow");
    }, 2000);

    document.getElementById("submit-btn").classList.add("hidden");
    document.getElementById("next-btn").classList.remove("hidden");
  } catch (error) {
    alert("Error submitting answer: " + error.message);
    document.getElementById("submit-btn").disabled = false;
  } finally {
    document.getElementById("loader").classList.add("hidden");
  }
}

// ==================== DATA LOADING ====================
async function loadTopics() {
  try {
    const res = await fetch("/interview/get_topics/");
    const data = await res.json();
    const topicSelect = document.getElementById("topic");

    data.topics.forEach(topic => {
      const opt = document.createElement("option");
      opt.value = topic;
      opt.textContent = topic;
      topicSelect.appendChild(opt);
    });
  } catch (error) {
    console.error("Error loading topics:", error);
  }
}

// ==================== USER HISTORY ====================
async function loadUserHistory(email) {
  try {
    const res = await fetch(`/interview/history/?email=${encodeURIComponent(email)}`);
    const data = await res.json();
    
    if (data.error) {
      document.getElementById("history-list").innerHTML = `<p>${data.error}</p>`;
      return;
    }

    displayHistory(data);
  } catch (error) {
    console.error("Error loading history:", error);
    document.getElementById("history-list").innerHTML = `<p>Error loading history</p>`;
  }
}

function displayHistory(historyData) {
  const historyList = document.getElementById("history-list");
  
  if (!historyData.sessions || historyData.sessions.length === 0) {
    historyList.innerHTML = `<p>No previous interviews found. Start your first one!</p>`;
    return;
  }

  historyList.innerHTML = `
    <div class="history-header">
      <strong>Welcome back, ${historyData.candidate.name}!</strong>
      <p>Email: ${historyData.candidate.email}</p>
    </div>
    <table class="history-table">
      <thead>
        <tr>
          <th>Date & Time</th>
          <th>Session No</th>
          <th>Questions</th>
        </tr>
      </thead>
      <tbody>
        ${historyData.sessions.map(session => `
          <tr class="session-row" data-session-id="${session.session_id}">
            <td>${new Date(session.started_at).toLocaleString()}</td>
            <td>${session.session_id}</td>
            <td>
              <div class="questions-list">
                ${session.questions.map(question => 
                  `<div class="question-item">"${question}"</div>`
                ).join('')}
              </div>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  // Add click event to table rows
  document.querySelectorAll('.session-row').forEach(row => {
    row.addEventListener('click', function() {
      const sessionId = this.getAttribute('data-session-id');
      viewSessionDetails(sessionId);
    });
  });
}




async function showSummary() {
  const res = await fetch(`/interview/summary/?session_id=${sessionId}`);
  const data = await res.json();

  document.getElementById("summary").innerHTML = `
    <strong>Candidate:</strong> ${data.candidate}<br>
    <strong>Email:</strong> ${data.email}<br>
    <strong>Total Questions:</strong> ${data.total_questions}<br>
    <strong>Average Score:</strong> ${data.average_score}<br>
    <strong>Weak Topics:</strong> ${data.weak_topics.join(", ")}<br><br>

    <h3>Details:</h3>
    ${data.details.map(d => `
      <div style="margin-bottom: 15px; border-bottom: 1px solid #ddd; padding-bottom: 10px;">
        <strong>Question:</strong> ${d.question}<br>
        <strong>Your Answer:</strong> ${d.answer}<br>
        <strong>Feedback:</strong> ${d.feedback}<br>
        <strong>Score:</strong> ${d.score}<br>
        <strong>Topic:</strong> ${d.topic}
      </div>
    `).join("")}
  `;
}


// ==================== EVENT LISTENERS SETUP ====================
window.addEventListener("DOMContentLoaded", function () {
  // Set up all event listeners
  document.getElementById("login-btn").addEventListener("click", handleLogin);
  document.getElementById("start-interview-btn").addEventListener("click", startInterview);
  document.getElementById("submit-btn").addEventListener("click", submitAnswer);
  document.getElementById("next-btn").addEventListener("click", loadNextQuestion);
  document.getElementById("clear-session-btn").addEventListener("click", clearSession);
  document.getElementById("new-interview-btn").addEventListener("click", clearSession);

  // Initialize the app
  loadTopics();
  checkExistingSession();
});