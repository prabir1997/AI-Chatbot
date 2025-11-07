// Main initialization and event listeners
window.addEventListener("DOMContentLoaded", function () {
  // Set up all event listeners
  document.getElementById("login-btn").addEventListener("click", handleLogin);
  document.getElementById("start-interview-btn").addEventListener("click", startInterview);
  document.getElementById("submit-btn").addEventListener("click", submitAnswer);
  document.getElementById("next-btn").addEventListener("click", loadNextQuestion);
  document.getElementById("clear-session-btn").addEventListener("click", clearSession);
  document.getElementById("new-interview-btn").addEventListener("click", clearSession);
  document.getElementById("logout").addEventListener("click", function() {
    localStorage.setItem("isLoggedIn", "false");
    clearSession();
  });

  // Initialize the app
  loadTopics();

  // Check if user is already logged in
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const savedEmail = localStorage.getItem("userEmail");

  if (isLoggedIn === 'true' && savedEmail) {
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
    document.getElementById('name').value = localStorage.getItem('userName') || '';
    document.getElementById('email').value = savedEmail;
    loadUserHistory(savedEmail);
  }

  checkExistingSession();
});
