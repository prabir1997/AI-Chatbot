from rest_framework.response import Response
from rest_framework.views import APIView
from interview.models import Candidate, InterviewSession, CandidateResponse
import sys

class HistoryAPI(APIView):
    def get(self, request):
        try:
            email = request.GET.get("email")
            if not email:
                return Response({"error": "Email is required"}, status=400)
            
            try:
                candidate = Candidate.objects.get(email=email)
            except Candidate.DoesNotExist:
                return Response({"error": "Candidate not found"}, status=404)
            
            # Get all sessions for this candidate with response count
            sessions = InterviewSession.objects.filter(candidate=candidate).prefetch_related('responses')
            
            session_history = []
            for session in sessions:
                # Get all questions from this session
                questions = []
                for response in session.responses.all():
                    questions.append(response.question.question_text)
                    
                if session.responses.count() == 0:
                    continue  # Skip sessions with no responses
                    
                session_history.append({
                    "session_id": session.id,
                    "started_at": session.started_at,
                    "ended_at": session.ended_at,
                    "difficulty": session.difficulty_level,
                    "questions": questions
                })
                
            return Response({
                "candidate": {
                    "name": candidate.name,
                    "email": candidate.email
                },
                "sessions": session_history
            })
        except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                # logger.error("Error at %s %s : " % (exc_traceback.tb_lineno, e))
                print("Error at %s %s : " % (exc_traceback.tb_lineno, e))
                return Response({'error': str(e)}, status=500)