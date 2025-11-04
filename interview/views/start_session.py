
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










@csrf_exempt
def start_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        question_count = data.get("question_count", 10)  # Default to 10
        difficulty = data.get("difficulty", "medium")    # Default to medium

        if not name or not email:
            return JsonResponse({"error": "Name and email required"}, status=400)

        # Validate inputs
        if question_count not in [5, 10]:
            return JsonResponse({"error": "Question count must be 5 or 10"}, status=400)
        if difficulty not in ["easy", "medium", "hard"]:
            return JsonResponse({"error": "Invalid difficulty level"}, status=400)

        # Create or get candidate        
        candidate, _ = Candidate.objects.get_or_create(
            email=email,
            defaults={"name": name}
        )

        # Create new session with settings
        session = InterviewSession.objects.create(
            candidate=candidate,
            target_question_count=question_count,
            difficulty_level=difficulty
        )

        return JsonResponse({
            "message": "Session started",
            "session_id": session.id,
            "candidate": candidate.name,
            "question_count": question_count,
            "difficulty": difficulty
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

