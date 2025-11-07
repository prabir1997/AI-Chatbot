// Question flow: load next question, submit answer
async function loadNextQuestion() {
  if (!window.sessionId) {
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

    const res = await fetch(`/interview/next-question/?session_id=${window.sessionId}&topic=${topicParam}`);
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

    window.currentQuestion = data;
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
        session_id: window.sessionId,
        question_id: window.currentQuestion.question_id,
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
