from rest_framework.response import Response
from rest_framework.views import APIView
from interview.models import Candidate, InterviewSession, CandidateResponse

class HistoryAPI(APIView):
    def get(self, request):
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
            session_history.append({
                "session_id": session.id,
                "started_at": session.started_at,
                "ended_at": session.ended_at,
                "difficulty": session.difficulty_level,
                "target_questions": session.target_question_count,
                "completed_questions": session.responses.count(),
                "status": "Completed" if session.ended_at else "In Progress"
            })
            
        return Response({
            "candidate": {
                "name": candidate.name,
                "email": candidate.email
            },
            "sessions": session_history
        })