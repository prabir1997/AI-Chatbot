// Session-related functions
function checkExistingSession() {
  const savedSessionId = localStorage.getItem("interviewSessionId");
  const savedEmail = localStorage.getItem("interviewEmail");
  const isLoggedIn = localStorage.getItem("isLoggedIn");

  // If user is logged in but no active interview, show dashboard
  if (isLoggedIn === 'true' && savedEmail) {
    showDashboard(savedEmail);
    return;
  }

  // If user has active interview session
  if (savedSessionId && savedEmail) {
    window.sessionId = savedSessionId;
    document.getElementById("email").value = savedEmail;
    showDashboard(savedEmail);
    document.getElementById("dashboard-section").classList.add("hidden");
    document.getElementById("question-section").classList.remove("hidden");
    loadNextQuestion();
  }
}
