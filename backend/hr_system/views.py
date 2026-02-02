from rest_framework import viewsets, status, views
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Job, Candidate, InterviewSession, Evaluation, CheatingLog, Question, HRUser
from rest_framework.authtoken.models import Token
from .serializers import JobSerializer, CandidateSerializer, InterviewSessionSerializer, EvaluationSerializer, CheatingLogSerializer, QuestionSerializer
from .tasks import process_candidate_task
from django.conf import settings
import csv
import io

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer

    @action(detail=True, methods=['post'])
    def upload_candidates(self, request, pk=None):
        job = get_object_or_404(Job, pk=pk)
        
        # Determine if it's a bulk upload or manual add
        file = request.FILES.get('file')
        
        if file and file.name.endswith('.csv'):
            # Bulk Upload (CSV)
            try:
                decoded_file = file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                results = {"success": [], "errors": []}
                
                for row in reader:
                    # Clean and normalize headers
                    clean_row = {k.strip().lower(): v for k, v in row.items()}
                    
                    name = clean_row.get('candidate name') or clean_row.get('name')
                    email = clean_row.get('candidate email') or clean_row.get('email')
                    resume_url = clean_row.get('resume link') or clean_row.get('resume url') or clean_row.get('link') or clean_row.get('resume_url')
                    
                    if not email:
                        results["errors"].append({"row": row, "error": "Missing email column"})
                        continue
                    
                    if Candidate.objects.filter(job=job, email=email).exists():
                        results["errors"].append({"row": row, "error": f"Duplicate email: {email}"})
                        continue
                    
                    candidate_data = {
                        'name': name or 'Unknown',
                        'email': email,
                        'resume_url': resume_url,
                        'job': job.id
                    }
                    
                    serializer = CandidateSerializer(data=candidate_data)
                    if serializer.is_valid():
                        candidate = serializer.save(job=job)
                        process_candidate_task(candidate.id)
                        results["success"].append(email)
                    else:
                        results["errors"].append({"row": row, "error": serializer.errors})
                
                return Response(results, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Manual Add
        data = request.data.dict() if hasattr(request.data, 'dict') else request.data.copy()
        data['job'] = job.id
        serializer = CandidateSerializer(data=data)
        if serializer.is_valid():
            candidate = serializer.save()
            process_candidate_task(candidate.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        job = get_object_or_404(Job, pk=pk)
        candidates = job.candidates.all()
        data = []
        for c in candidates:
            session = getattr(c, 'session', None)
            data.append({
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "link": f"{settings.FRONTEND_URL}/interview/{c.session.link.token}" if session and hasattr(session, 'link') else "Generating...",
                "status": session.status if session else "Processing",
                "resume_file": c.resume_file.url if c.resume_file else None,
                "resume_url": c.resume_url
            })
        return Response(data)

    @action(detail=True, methods=['get'])
    def ranking(self, request, pk=None):
        job = get_object_or_404(Job, pk=pk)
        evaluations = Evaluation.objects.filter(session__candidate__job=job).order_by('-overall_score')
        data = []
        for i, ev in enumerate(evaluations):
            data.append({
                "rank": i + 1,
                "name": ev.session.candidate.name,
                "email": ev.session.candidate.email,
                "score": ev.overall_score,
                "cheating": ev.cheating_flag
            })
        return Response(data)

class CandidateDetailView(views.APIView):
    def get(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id)
        session = getattr(candidate, 'session', None)
        resume = getattr(candidate, 'resume_data', None)
        evaluation = getattr(session, 'evaluation', None) if session else None
        
        data = {
            "name": candidate.name,
            "email": candidate.email,
            "resume_text": resume.raw_text if resume else "Not parsed yet",
            "questions": QuestionSerializer(session.questions.all(), many=True).data if session else [],
            "evaluation": EvaluationSerializer(evaluation).data if evaluation else None,
            "cheating_logs": CheatingLogSerializer(session.cheating_logs.all(), many=True).data if session else []
        }
        return Response(data)

class LoginView(views.APIView):
    permission_classes = []
    def post(self, request):
        from django.contrib.auth import authenticate, login
        username_or_email = request.data.get('username')
        password = request.data.get('password')
        
        # Try as username
        user = authenticate(username=username_or_email, password=password)
        
        # If failed, try as email
        if not user:
            try:
                from .models import HRUser
                user_obj = HRUser.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except HRUser.DoesNotExist:
                pass
        
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "token": token.key,
                "user": {
                    "username": user.username,
                    "email": user.email
                }
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
