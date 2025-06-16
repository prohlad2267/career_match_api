from django.urls import path
from .views import (
    ResumeUploadView,
    JobMatchView,
    SaveJobView,
    GetSavedJobs,
    JobDetailView,
    RemoveSavedJobView
)
from .auth_views import SignupView, SigninView, ValidateTokenView
from .profile_views import CurrentUserProfileView

urlpatterns = [
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('match-jobs/', JobMatchView.as_view(), name='job-match'),
    path('save-job/', SaveJobView.as_view(), name='job-save'),
    path('saved-jobs/', GetSavedJobs.as_view(), name='job-saved-list'),
     path('save-job/<str:job_id>/', RemoveSavedJobView.as_view(), name='remove-saved-job'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/signin/', SigninView.as_view(), name='signin'),
    path('profile/', CurrentUserProfileView.as_view(), name='user-profile'),
    path('auth/validate-token/', ValidateTokenView.as_view(), name='validate-token'),
    path('job/<str:job_id>/', JobDetailView.as_view(), name='job-detail'),
    path('remove-job/<str:job_id>/', RemoveSavedJobView.as_view(), name='job-remove'),

    
]
