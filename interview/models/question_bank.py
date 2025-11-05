from django.db import models





# Difficulty choices
DIFFICULTY_CHOICES = [
    ("easy", "Easy"),
    ("medium", "Medium"),
    ("hard", "Hard"),
]


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

