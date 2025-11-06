from django.urls import path
from .views import NextQuestionAPI, QuestionBankView, SubmitAnswerAPI, HistoryAPI
from . import views

urlpatterns = [
    path('start_session/', views.start_session, name='start_session'),
    path("submit-answer/", SubmitAnswerAPI.as_view(), name="submit-answer"),
    path("get_topics/", views.get_topics, name="get-topics"),
    path("next-question/", NextQuestionAPI.as_view(), name="next-question"),
    path("summary/", views.interview_summary, name="interview-summary"),
    
    path("ui/", views.interview_ui, name="interview-ui"),  # 👈 New
    
    path("question_bank/", QuestionBankView.as_view(), name="question-bank"),  # 👈 New
    
    path('history/', HistoryAPI.as_view(), name='history'),
]
