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
window.addEventListener("DOMContentLoaded", function() {
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

  const res = await fetch(`/interview/next-question/?session_id=${sessionId}`);
  const data = await res.json();

  if (data.error) {
    console.error("Error loading question:", data.error);
    alert("Error loading question: " + data.error);
    return;
  }

  // Check if interview is complete - UPDATED LOGIC
  if (data.interview_complete || (data.message && data.message.includes("completed"))) {
    // Show completion message and evaluation button
    document.getElementById("question-text").textContent = "🎉 Interview Completed!";
    document.getElementById("feedback").textContent = data.message || "You've answered all questions for this session.";
    document.getElementById("answer").value = "";
    document.getElementById("answer").style.display = "none";
    
    // Hide submit button, show evaluation button
    document.getElementById("submit-btn").classList.add("hidden");
    document.getElementById("next-btn").classList.add("hidden");
    
    // Create or show evaluation button
    let evalBtn = document.getElementById("eval-btn");
    if (!evalBtn) {
      evalBtn = document.createElement("button");
      evalBtn.id = "eval-btn";
      evalBtn.textContent = "View Evaluation Summary";
      evalBtn.className = "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded";
      evalBtn.onclick = showSummary;
      document.querySelector(".container").appendChild(evalBtn);
    } else {
      evalBtn.classList.remove("hidden");
    }
    
    // Update progress display
    if (data.session_progress) {
      document.getElementById("progress").textContent = data.session_progress;
    }
    
    return;
  }

  // Normal question flow
  currentQuestion = data;
  document.getElementById("question-text").textContent = data.question_text;
  document.getElementById("feedback").textContent = "";
  document.getElementById("answer").value = "";
  document.getElementById("answer").style.display = "block"; // Make sure answer box is visible
  
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
}


async function submitAnswer() {
  const answer = document.getElementById("answer").value.trim();

  if (!answer) {
    alert("Please type your answer before submitting!");
    return;
  }

  // Show loader and disable submit button
  document.getElementById("loader").classList.remove("hidden");
  document.getElementById("submit-btn").disabled = true;
  document.getElementById("feedback").textContent = "";
  
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
  document.getElementById("question-section").classList.add("hidden");
  document.getElementById("summary-section").classList.remove("hidden");

  const res = await fetch(`/interview/summary/?session_id=${sessionId}`);
  const data = await res.json();

  document.getElementById("summary").textContent = JSON.stringify(data, null, 2);
  
  // Clear localStorage after completing interview
  localStorage.removeItem("interviewSessionId");
  localStorage.removeItem("interviewEmail");
}
