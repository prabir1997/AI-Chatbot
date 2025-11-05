from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from interview.models import QuestionBank
from interview.serializers import QuestionBankSerializer




class QuestionBankView(APIView):
    def post(self, request):        
        """Create a new question in the question bank."""
        serializer = QuestionBankSerializer(data=request.data, many=True)
        if serializer.is_valid():
            question = serializer.save()
            return Response(QuestionBankSerializer(question, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)