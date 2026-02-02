from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import HRUser, Job, Candidate, InterviewSession, Question, Answer, Evaluation, CheatingLog, EmailLog, CodingQuestionBank

admin.site.register(HRUser, UserAdmin)
admin.site.register(Job)
admin.site.register(Candidate)
admin.site.register(InterviewSession)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Evaluation)
admin.site.register(CheatingLog)
admin.site.register(EmailLog)
admin.site.register(CodingQuestionBank)
