// Data loading: topics, history, summary
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

async function showSummary() {
  const res = await fetch(`/interview/summary/?session_id=${window.sessionId}`);
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
