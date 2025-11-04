from django.db import models
from django.utils import timezone

# Difficulty choices
DIFFICULTY_CHOICES = [
    ("easy", "Easy"),
    ("medium", "Medium"),
    ("hard", "Hard"),
]

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"

class QuestionBank(models.Model):
    question_text = models.TextField()
    topic = models.CharField(max_length=50, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="medium")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        # Keep preview short in admin lists
        return (self.question_text[:80] + "...") if len(self.question_text) > 80 else self.question_text

class InterviewSession(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="sessions")
    target_question_count = models.IntegerField(default=10)
    difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="medium")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)  # optional: store human notes about session
    question = models.ForeignKey(QuestionBank, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Session {self.id} — {self.candidate.name} @ {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def end(self):
        """Mark this session ended now."""
        self.ended_at = timezone.now()
        self.save(update_fields=["ended_at"])

class CandidateResponse(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(QuestionBank, on_delete=models.PROTECT)
    user_answer = models.TextField()
    ai_feedback = models.TextField(blank=True)   # may be filled after Gemini call
    score = models.FloatField(default=0)         # score computed by AI or rubric
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["session", "created_at"]),
            models.Index(fields=["question"]),
        ]
        # optional: prevent duplicate storage of same question in same session
        unique_together = ("session", "question")

    def __str__(self):
        return f"Resp {self.id} — Session {self.session.id} — Q{self.question.id}"

    def as_dict(self):
        """Lightweight helper to serialize for UI/JSON if needed."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "question_id": self.question_id,
            "question_text": self.question.question_text,
            "user_answer": self.user_answer,
            "ai_feedback": self.ai_feedback,
            "score": self.score,
            "created_at": self.created_at.isoformat(),
        }




class Evaluation(models.Model):
    question_text = models.TextField()
    user_answer = models.TextField()
    ai_feedback = models.TextField()
    ai_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question_text[:50]}... | Score: {self.ai_score}"




