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



genai.configure(api_key="AIzaSyDJ6TxQW9viXxpqXhvEmLSKUDrD3X76XX0")  # ⬅️ replace with your API key
model = genai.GenerativeModel("gemini-2.5-flash")

@csrf_exempt
def submit_answer(request):
    """
    Handles a candidate's submitted answer and gets AI feedback.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        session_id = data.get("session_id")
        question_id = data.get("question_id")
        user_answer = data.get("user_answer", "").strip()

        if not (session_id and question_id and user_answer):
            return JsonResponse({"error": "Missing fields"}, status=400)

        session = get_object_or_404(InterviewSession, id=session_id)
        question = get_object_or_404(QuestionBank, id=question_id)

        # ✅ Gemini prompt (matches your script logic)
        prompt = f"""
        You are a friendly AI interviewer conducting a Python interview.

        The question was:
        "{question.question_text}"

        The candidate's answer:
        "{user_answer}"

        Your task:
        1. If the answer is wrong, incomplete, or 'I don't know',
           respond kindly with a short, encouraging tone.
        2. Then, explain the correct answer clearly in 3–4 lines.
        3. End with a positive note like “Let's try another one!”.
        4. Finally, provide a **numeric score (0–10)** based on how correct the answer is.

        Return JSON only in this format:
        {{
          "feedback": "your short explanation and encouragement",
          "score": number_between_0_and_10
        }}
        """

        # Generate AI response
        ai_response = model.generate_content(prompt)
        ai_text = ai_response.text.strip()

        # Parse Gemini output safely
        try:
            clean_text = ai_text
            # Remove code block markers if present
            if clean_text.startswith("```"):
                clean_text = clean_text.strip("`")  # remove all backticks
                clean_text = clean_text.replace("json", "", 1).strip()
            ai_data = json.loads(clean_text)
            feedback = ai_data.get("feedback", "")
            score = float(ai_data.get("score", 0))
        except Exception:
            # If Gemini doesn’t return pure JSON, fallback
            feedback = ai_text
            score = 0

        # Save to DB
        response_obj, created = CandidateResponse.objects.get_or_create(
            session=session,
            question=question,
            defaults={
                "user_answer": user_answer,
                "ai_feedback": feedback,
                "score": score,
            }
        )
        if not created:
            response_obj.user_answer = user_answer
            response_obj.ai_feedback = feedback
            response_obj.score = score
            response_obj.save()

        InterviewSession.objects.filter(id=session.id).update(question=question)
        return JsonResponse({
            "message": "Answer evaluated successfully",
            "feedback": feedback,
            "score": score,
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




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