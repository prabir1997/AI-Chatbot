from django.urls import path
from .views import NextQuestionAPI
from . import views

urlpatterns = [
    path('start_session/', views.start_session, name='start_session'),
    path("submit-answer/", views.submit_answer, name="submit-answer"),
    path("next-question/", NextQuestionAPI.as_view(), name="next-question"),
    path("summary/", views.interview_summary, name="interview-summary"),
    
    path("ui/", views.interview_ui, name="interview-ui"),  # 👈 New
]
