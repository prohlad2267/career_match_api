from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from resume.models import SavedJob

class JobTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='jobuser', password='test123')
        self.client.force_authenticate(user=self.user)
        self.job = SavedJob.objects.create(
            user=self.user,
            job_id='abc123',
            title='Backend Developer',
            company='TestCo',
            location='Remote',
            url='https://example.com/job/abc123'
        )

    def test_get_saved_jobs(self):
        response = self.client.get('/api/resume/saved-jobs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_remove_saved_job(self):
        response = self.client.delete(f'/api/resume/save-job/{self.job.job_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Saved job removed successfully')
