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
from rest_framework.views import APIView
from rest_framework.response import Response



genai.configure(api_key="AIzaSyDJ6TxQW9viXxpqXhvEmLSKUDrD3X76XX0")  # ⬅️ replace with your API key
model = genai.GenerativeModel("gemini-2.5-flash")


class SubmitAnswerAPI(APIView):
    def post(self, request):
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
                
            # Calculate is_correct based on score
            is_correct = score >= 7  # Consider 7+ as passing

            # Save to DB
            response_obj, created = CandidateResponse.objects.get_or_create(
                session=session,
                question=question,
                defaults={
                    "user_answer": user_answer,
                    "ai_feedback": feedback,
                    "score": score,
                    "is_correct": is_correct,
                }
            )
            if not created:
                response_obj.user_answer = user_answer
                response_obj.ai_feedback = feedback
                response_obj.score = score
                response_obj.is_correct = is_correct
                response_obj.save()

            return JsonResponse({
                "message": "Answer evaluated successfully",
                "feedback": feedback,
                "score": score,
                "is_correct": is_correct,
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


