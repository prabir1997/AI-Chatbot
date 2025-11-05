from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from interview.models import (
    InterviewSession,
    CandidateResponse,
    QuestionBank,
    Candidate,
)

# from .utils.gemini_helper import evaluate_answer


from django.db.models import Avg

from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Subquery
import json, random
import google.generativeai as genai


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

genai.configure(api_key="AIzaSyDJ6TxQW9viXxpqXhvEmLSKUDrD3X76XX0")
model = genai.GenerativeModel("gemini-2.5-flash")




class NextQuestionAPI(APIView):
    def get(self, request):
        session_id = request.GET.get("session_id")
        if not session_id:
            return Response(
                {"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = InterviewSession.objects.get(id=session_id)
        except InterviewSession.DoesNotExist:
            return Response(
                {"error": "Invalid session_id"}, status=status.HTTP_404_NOT_FOUND
            )

        session_answered_count = CandidateResponse.objects.filter(
            session=session
        ).count()
        target_count = session.target_question_count

        if session_answered_count >= target_count:
            return Response(
                {
                    "interview_complete": True,
                    "message": "Interview completed! Please proceed to evaluation.",
                    "session_progress": f"Session Complete: {session_answered_count}/{target_count} answered",
                }
            )

        # Get already answered question IDs in this session
        answered_question_ids = CandidateResponse.objects.filter(
            session=session
        ).values_list('question_id', flat=True)
        
        # Find unanswered questions
        unanswered = QuestionBank.objects.filter(
            difficulty=session.difficulty_level
        ).exclude(id__in=answered_question_ids)
        
        if not unanswered.exists():
            # Generate new question if none left
            generation_prompt = f"""Generate a {session.difficulty_level} Python interview question.
                        STRICT RULES:
                        - ONLY the question text
                        - NO examples, explanations, or code
                        - MAXIMUM 15 words
                        - Format: Just the question ending with '?'

                        Example: "How do you reverse a string in Python?"
                        Example: "What is the difference between list and tuple?"

                        Question:"""
            try:
                generated_response = model.generate_content(generation_prompt)
                new_question_text = generated_response.text.strip()
                
                question = QuestionBank.objects.create(
                    question_text=new_question_text,
                    topic="Python Programming",
                    difficulty=session.difficulty_level,
                )
            except Exception as e:
                return Response(
                    {"error": f"Failed to generate question: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            question = random.choice(list(unanswered))

        return Response(
            {
                "question_id": question.id,
                "question_text": question.question_text,
                "topic": question.topic,
                "difficulty": question.difficulty,
                "session_progress": f"{session_answered_count + 1}/{target_count}",
            }
        )










