let sessionId = null;
let currentQuestion = null;

// Clear session helper function
function clearSession() {
  localStorage.removeItem("interviewSessionId");
  localStorage.removeItem("interviewEmail");
  sessionId = null;
  location.reload();
}

// Check for existing session on page load
window.addEventListener("DOMContentLoaded", function () {
  const savedSessionId = localStorage.getItem("interviewSessionId");
  const savedEmail = localStorage.getItem("interviewEmail");

  if (savedSessionId && savedEmail) {
    // Restore session data
    sessionId = savedSessionId;
    document.getElementById("email").value = savedEmail;

    // Hide start section and show question section
    document.getElementById("start-section").classList.add("hidden");
    document.getElementById("question-section").classList.remove("hidden");

    // Load next question to continue the interview
    loadNextQuestion();
  }
});

async function loadTopics() {
  try {
    const res = await fetch("/interview/get_topics/");
    const data = await res.json();
    const topicSelect = document.getElementById("topic");

    // Populate dropdown
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

// Load topics on page load
window.addEventListener("DOMContentLoaded", loadTopics);



async function startInterview() {
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const questionCount = document.getElementById("question-count").value; // Get selected value
  const difficulty = document.getElementById("difficulty").value; // Get selected value

  if (!name || !email) {
    alert("Please enter your name and email!");
    return;
  }

  // Check if we have an existing session for this email
  const savedSessionId = localStorage.getItem("interviewSessionId");
  const savedEmail = localStorage.getItem("interviewEmail");

  if (savedSessionId && savedEmail && savedEmail.toLowerCase() === email.toLowerCase()) {
    // Resume existing session
    sessionId = savedSessionId;
    console.log("Resuming existing session:", sessionId);
  } else {
    // Start new session
    const res = await fetch("/interview/start_session/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        email,
        question_count: parseInt(questionCount), // Send selected count
        difficulty: difficulty // Send selected difficulty
      })
    });

    const data = await res.json();

    if (!data.session_id) {
      alert("Error starting session!");
      console.log(data);
      return;
    }

    sessionId = data.session_id;
    // Save session to localStorage
    localStorage.setItem("interviewSessionId", sessionId);
    localStorage.setItem("interviewEmail", email);
  }

  document.getElementById("start-section").classList.add("hidden");
  document.getElementById("question-section").classList.remove("hidden");

  loadNextQuestion();
}

async function loadNextQuestion() {
  if (!sessionId) {
    console.error("No session ID available");
    alert("Session expired. Please start a new interview.");
    clearSession();
    return;
  }

  // Show loader and disable next button
  document.getElementById("loader").classList.remove("hidden");
  document.getElementById("next-btn").disabled = true;

  try {
    const topicSelect = document.getElementById("topic");
    const selectedTopics = Array.from(topicSelect.selectedOptions)
      .map(opt => opt.value)
      .filter(topic => topic !== ""); // Remove empty "All Topics"
    const topicParam = selectedTopics.join(',');

    const res = await fetch(`/interview/next-question/?session_id=${sessionId}&topic=${topicParam}`);
    const data = await res.json();

    if (data.error) {
      console.error("Error loading question:", data.error);
      alert("Error loading question: " + data.error);
      return;
    }



    // Check if interview is complete
    if (data.interview_complete === true) {
      // Redirect to Django summary page
      document.getElementById("question-section").classList.add("hidden");
      document.getElementById("summary-section").classList.remove("hidden");
      showSummary();
    }

    // Normal question flow
    currentQuestion = data;
    document.getElementById("question-text").textContent = data.question_text;
    document.getElementById("feedback").textContent = "";
    document.getElementById("answer").value = "";
    document.getElementById("answer").style.display = "block";

    // Hide next button and show submit button
    document.getElementById("next-btn").classList.add("hidden");
    document.getElementById("submit-btn").classList.remove("hidden");
    document.getElementById("submit-btn").disabled = false;

    // Display progress if available
    if (data.session_progress) {
      document.getElementById("progress").textContent = data.session_progress;
    } else {
      document.getElementById("progress").textContent = "";
    }
  } catch (error) {
    alert("Error loading question: " + error.message);
  } finally {
    // Hide loader and re-enable next button
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

  // Show loader and disable submit button
  document.getElementById("loader").classList.remove("hidden");
  document.getElementById("submit-btn").disabled = true;
  feedbackEl.textContent = "";
  feedbackEl.classList.remove("correct-glow", "wrong-glow"); // 🔹 clear previous glow

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

    document.getElementById("feedback").textContent = data.feedback || "No feedback available.";
    feedbackEl.classList.add("feedback"); // 🔹 ensure base style

    // 🔹 Add glow effect based on result
    if (data.is_correct) {
      feedbackEl.classList.add("correct-glow");
    } else {
      feedbackEl.classList.add("wrong-glow");
    }

    // 🔹 Optional: remove glow after 2 seconds
    setTimeout(() => {
      feedbackEl.classList.remove("correct-glow", "wrong-glow");
    }, 2000);

    // Hide submit button and show next button
    document.getElementById("submit-btn").classList.add("hidden");
    document.getElementById("next-btn").classList.remove("hidden");
  } catch (error) {
    alert("Error submitting answer: " + error.message);
    document.getElementById("submit-btn").disabled = false;
  } finally {
    // Hide loader regardless of success or failure
    document.getElementById("loader").classList.add("hidden");
  }
}

async function showSummary() {
  const res = await fetch(`/interview/summary/?session_id=${sessionId}`);
  const data = await res.json();

  document.getElementById("question-section").classList.add("hidden");
  document.getElementById("summary-section").classList.remove("hidden");

  // 🟢 Build formatted summary
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

