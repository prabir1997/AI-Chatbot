from django.contrib import admin
from .models import Candidate, QuestionBank, InterviewSession, CandidateResponse

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ("short_text", "topic", "difficulty", "created_at")
    list_filter = ("difficulty", "topic")
    search_fields = ("question_text",)

    def short_text(self, obj):
        return obj.question_text[:60]
    short_text.short_description = "Question"

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "candidate", "started_at", "ended_at")
    list_filter = ("started_at",)
    search_fields = ("candidate__name", "candidate__email")

@admin.register(CandidateResponse)
class CandidateResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "question", "score", "created_at")
    search_fields = ("question__question_text", "session__candidate__name")
    list_filter = ("created_at",)
