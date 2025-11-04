from django.db import models
from django.contrib.auth.models import User

class Level(models.Model):
    number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Level {self.number} - {self.title}"


class LevelQuestion(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Q{self.id} - Level {self.level.number}"


class UserLevel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_level")
    current_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Level {self.current_level.number if self.current_level else 'N/A'}"


class UserProgressHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    questions_solved = models.IntegerField(default=0)
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Level {self.level.number} - {'Success' if self.success else 'Fail'}"
