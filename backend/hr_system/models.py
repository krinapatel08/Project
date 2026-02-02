from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone

class HRUser(AbstractUser):
    """
    HR User model. HR accounts are created by Super Admin.
    """
    pass

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.TextField()
    experience_level = models.CharField(max_length=100)
    
    # Interview Configuration
    oral_question_count = models.IntegerField(default=5)
    coding_question_count = models.IntegerField(default=2)
    thinking_time = models.IntegerField(help_text="Minutes per oral question", default=1)
    recording_time = models.IntegerField(help_text="Minutes per oral question", default=3)
    coding_time = models.IntegerField(help_text="Minutes for coding task", default=60)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Candidate(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    resume_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'email')

    def __str__(self):
        return f"{self.name} - {self.job.title}"

class Resume(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='resume_data')
    raw_text = models.TextField()
    extracted_metadata = models.JSONField(default=dict)
    parsed_at = models.DateTimeField(auto_now_add=True)

class InterviewSession(models.Model):
    STATUS_CHOICES = [
        ('NOT_ATTEMPTED', 'Not Attempted'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('EXPIRED', 'Expired'),
    ]
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='session')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_ATTEMPTED')
    
    # Config Snapshot (Immutable even if Job configuration changes)
    oral_question_count = models.IntegerField()
    coding_question_count = models.IntegerField()
    thinking_time = models.IntegerField()
    recording_time = models.IntegerField()
    coding_time = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class InterviewLink(models.Model):
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='link')
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at or self.is_used

class CodingQuestionBank(models.Model):
    text = models.TextField()
    difficulty = models.CharField(max_length=50)
    skills = models.TextField() # CSV or JSON
    role_type = models.CharField(max_length=100)

class Question(models.Model):
    TYPE_CHOICES = [('ORAL', 'Oral'), ('CODING', 'Coding')]
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    expected_skills = models.TextField()
    time_limit = models.IntegerField(help_text="Seconds or Minutes depending on type")
    order = models.IntegerField(default=0)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    response_text = models.TextField(null=True, blank=True)
    response_file = models.FileField(upload_to='responses/', null=True, blank=True)
    marks = models.FloatField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

class Evaluation(models.Model):
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='evaluation')
    overall_score = models.FloatField(default=0.0)
    summary = models.TextField()
    cheating_flag = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True)

class CheatingLog(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='cheating_logs')
    event_type = models.CharField(max_length=100) # e.g., 'tab_switch', 'camera_disabled'
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

class EmailLog(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('SENT', 'Sent'), ('FAILED', 'Failed')]
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='email_logs')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
