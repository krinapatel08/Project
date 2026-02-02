from rest_framework import serializers
from .models import Job, Candidate, InterviewSession, Evaluation, CheatingLog, Question, Answer

class JobSerializer(serializers.ModelSerializer):
    candidates_count = serializers.IntegerField(source='candidates.count', read_only=True)
    completed_interviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = '__all__'
    
    def get_completed_interviews_count(self, obj):
        return obj.candidates.filter(session__status='COMPLETED').count()

class CandidateSerializer(serializers.ModelSerializer):
    resume_file = serializers.FileField(required=False, allow_null=True)
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'email', 'resume_file', 'resume_url', 'job']

class InterviewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'

class CheatingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheatingLog
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'response_text', 'response_file', 'marks', 'feedback']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'expected_skills', 'time_limit', 'order', 'answers']
