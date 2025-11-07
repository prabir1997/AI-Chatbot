// Utility functions
function clearSession() {
  localStorage.removeItem("interviewSessionId");
  localStorage.removeItem("interviewEmail");
  window.sessionId = null;
  location.reload();
}
