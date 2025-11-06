from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from interview.models import InterviewSession, CandidateResponse, QuestionBank, Candidate
# from .utils.gemini_helper import evaluate_answer


from django.db.models import Avg

from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Subquery
import json, random
import google.generativeai as genai
# from .models import CandidateResponse, InterviewSession, QuestionBank
from .start_session import start_session
from .next_question import NextQuestionAPI
from .question_bank import QuestionBankView
from .submit_answer import SubmitAnswerAPI
from .history import HistoryAPI


genai.configure(api_key="AIzaSyDJ6TxQW9viXxpqXhvEmLSKUDrD3X76XX0")  # ⬅️ replace with your API key
model = genai.GenerativeModel("gemini-2.5-flash")


def get_topics(request):
    topics = (
        QuestionBank.objects
        .exclude(topic__isnull=True)
        .exclude(topic__exact="")
        .order_by("topic")
        .values_list("topic", flat=True)
        .distinct()
    )
    return JsonResponse({"topics": sorted(set(topics))})



def interview_summary(request):
    """
    Returns interview summary for a given session.
    URL: /interview/summary/?session_id=1
    """
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse({"error": "session_id is required"}, status=400)

    try:
        session = InterviewSession.objects.get(id=session_id)
    except InterviewSession.DoesNotExist:
        return JsonResponse({"error": "Invalid session_id"}, status=404)

    responses = CandidateResponse.objects.filter(session=session).select_related("question")
    if not responses.exists():
        return JsonResponse({"message": "No responses found for this session."})

    total_questions = responses.count()
    avg_score = responses.aggregate(avg=Avg("score"))["avg"] or 0

    # Prepare detailed feedback per question
    details = [
        {
            "question": r.question.question_text,
            "answer": r.user_answer,
            "feedback": r.ai_feedback,
            "score": r.score,
            "topic": r.question.topic,
        }
        for r in responses
    ]

    # Find weak topics (average score < 7)
    weak_topics = (
        responses.values("question__topic")
        .annotate(avg=Avg("score"))
        .filter(avg__lt=7)
    )

    return JsonResponse({
        "candidate": session.candidate.name,
        "email": session.candidate.email,
        "total_questions": total_questions,
        "average_score": round(avg_score, 2),
        "weak_topics": [w["question__topic"] for w in weak_topics if w["question__topic"]],
        "details": details,
    }, json_dumps_params={"ensure_ascii": False})




def interview_ui(request):
    return render(request, "interview/interview.html")