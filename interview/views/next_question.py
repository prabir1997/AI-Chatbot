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
        # Input validation
        validation_error = self._validate_request(request)
        if validation_error:
            return validation_error

        session_id = request.GET.get("session_id")
        topic = request.GET.get("topic", None)
        
        # Get session
        session_result = self._get_session(session_id)
        if isinstance(session_result, Response):
            return session_result
        session = session_result

        # Check if interview is complete
        completion_check = self._check_interview_completion(session)
        if completion_check:
            return completion_check

        # Get next question
        next_question_result = self._get_next_question(session, topic)
        if isinstance(next_question_result, Response):
            return next_question_result
        
        question, session_answered_count = next_question_result

        return self._build_success_response(question, session, session_answered_count)

    def _validate_request(self, request):
        """Validate required parameters"""
        session_id = request.GET.get("session_id")
        if not session_id:
            return Response(
                {"error": "session_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return None

    def _get_session(self, session_id):
        """Retrieve session by ID"""
        try:
            return InterviewSession.objects.get(id=session_id)
        except InterviewSession.DoesNotExist:
            return Response(
                {"error": "Invalid session_id"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def _check_interview_completion(self, session):
        """Check if interview session is complete"""
        session_answered_count = CandidateResponse.objects.filter(
            session=session
        ).count()
        target_count = session.target_question_count

        if session_answered_count >= target_count:
            return Response(
                {
                    "interview_complete": True,
                    "message": "Interview completed. Please proceed to evaluation.",
                    "session_progress": f"Session Complete: {session_answered_count}/{target_count} answered",
                }
            )
        return None

    def _get_answered_question_ids(self, session):
        """Get all answered question IDs for this candidate"""
        # Current session answered questions
        current_answered_ids = CandidateResponse.objects.filter(
            session=session
        ).values_list('question_id', flat=True)
        
        # Previous sessions correctly answered questions
        previous_sessions = InterviewSession.objects.filter(
            candidate=session.candidate
        ).exclude(id=session.id)
        
        previous_answered_ids = CandidateResponse.objects.filter(
            session_id__in=previous_sessions,
            is_correct=True
        ).values_list('question_id', flat=True)
        
        return list(current_answered_ids) + list(previous_answered_ids)

    def _find_unanswered_question(self, session, topic, answered_question_ids):
        """Find an unanswered question from the database"""
        filters = {"difficulty": session.difficulty_level}
        if topic:
            filters["topic"] = topic
            
        unanswered = QuestionBank.objects.filter(**filters).exclude(
            id__in=answered_question_ids
        )
        
        if unanswered.exists():
            return random.choice(list(unanswered))
        return None

    def _generate_new_question(self, session, topic):
        """Generate a new question when none are available"""
        generation_prompt = f"""Generate a {session.difficulty_level} , topic: {topic} of Python interview question.
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
            
            return QuestionBank.objects.create(
                question_text=new_question_text,                    
                difficulty=session.difficulty_level,
            )
        except Exception as e:
            raise Exception(f"Failed to generate question: {str(e)}")

    def _get_next_question(self, session, topic):
        """Main logic to get the next question"""
        session_answered_count = CandidateResponse.objects.filter(
            session=session
        ).count()
        
        # Get all answered question IDs
        answered_question_ids = self._get_answered_question_ids(session)
        
        # Try to find an unanswered question
        question = self._find_unanswered_question(session, topic, answered_question_ids)
        
        # Generate new question if none found
        if not question:
            try:
                question = self._generate_new_question(session, topic)
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        
        return question, session_answered_count

    def _build_success_response(self, question, session, session_answered_count):
        """Build the success response"""
        return Response({
            "question_id": question.id,
            "question_text": question.question_text,
            "topic": question.topic,
            "difficulty": question.difficulty,
            "session_progress": f"{session_answered_count + 1}/{session.target_question_count}",
        })








