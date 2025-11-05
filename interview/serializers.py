from interview.models import QuestionBank
from rest_framework import serializers


class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = ['id', 'question_text', 'difficulty', 'topic', 'created_at']