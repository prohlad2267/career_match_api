from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from io import BytesIO

class ResumeUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='resumeuser', password='test123')
        self.client.force_authenticate(user=self.user)

    def test_resume_upload_pdf(self):
        content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<<>>\n%%EOF"
        dummy_pdf = BytesIO(content)
        dummy_pdf.name = 'resume.pdf'
        response = self.client.post('/api/resume/upload/', {'resume': dummy_pdf})
        print("UPLOAD RESPONSE:", response.data)
        self.assertEqual(response.status_code, 201)
