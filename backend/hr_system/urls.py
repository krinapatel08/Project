from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, CandidateDetailView, LoginView

router = DefaultRouter()
router.register(r'jobs', JobViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('candidates/<int:candidate_id>/detail/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('auth/login/', LoginView.as_view(), name='login'),
]
