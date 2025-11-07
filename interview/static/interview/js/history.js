// History display and helpers
function displayHistory(historyData) {
  const historyList = document.getElementById("history-list");

  if (!historyData.sessions || historyData.sessions.length === 0) {
    historyList.innerHTML = `<p>No previous interviews found. Start your first one!</p>`;
    return;
  }

  // Populate the welcome header in the main template (so we only pass data, not markup)
  const welcomeNameEl = document.getElementById('welcome-name');
  const welcomeEmailEl = document.getElementById('welcome-email');
  if (welcomeNameEl) welcomeNameEl.textContent = historyData.candidate.name || '';
  if (welcomeEmailEl) welcomeEmailEl.textContent = historyData.candidate.email || '';

  // Render only the sessions table into the history list
  historyList.innerHTML = `
    <table class="history-table">
      <thead>
        <tr>
          <th>Date & Time</th>
          <th>Questions</th>
        </tr>
      </thead>
      <tbody>
        ${historyData.sessions.map(session => `
          <tr class="session-row" data-session-id="${session.session_id}">
            <td>${new Date(session.started_at).toLocaleString()}</td>
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
    row.addEventListener('click', function () {
      const sessionId = this.getAttribute('data-session-id');
      viewSessionDetails(sessionId);
    });
  });
}

// Basic stub for viewing session details (endpoint may vary)
async function viewSessionDetails(sessionId) {
  try {
    const res = await fetch(`/interview/session-details/?session_id=${encodeURIComponent(sessionId)}`);
    if (!res.ok) {
      console.log('No session-details endpoint or error retrieving details');
      return;
    }
    const data = await res.json();
    // For now just log or you could show a modal
    console.log('Session details for', sessionId, data);
    alert(`Session ${sessionId} details logged to console.`);
  } catch (error) {
    console.error('Error fetching session details:', error);
  }
}
