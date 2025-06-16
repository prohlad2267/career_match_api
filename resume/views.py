import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Resume, SavedJob, MatchedJob
from .serializers import ResumeSerializer, SavedJobSerializer, MatchedJobSerializer
from .utils import parse_resume
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

class ResumeUploadView(APIView):
    
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        if 'resume' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        resume_file = request.FILES['resume']

        try:
            parsed_data = parse_resume(resume_file)

            def safe(value, fallback):
                return value.strip() if value and isinstance(value, str) and value.strip() else fallback

            parsed_data['name'] = safe(parsed_data.get('name'), 'Unknown')
            parsed_data['email'] = safe(parsed_data.get('email'), 'unknown@example.com')
            parsed_data['skills'] = parsed_data.get('skills') or []  # should be a list
            parsed_data['experience'] = parsed_data.get('experience') or ''
            parsed_data['education'] = parsed_data.get('education') or ''
            parsed_data['projects'] = parsed_data.get('projects') or ''

            # Save as string, return as list
            serializer = ResumeSerializer(data={
                **parsed_data,
                'skills': ', '.join(parsed_data['skills'])  # Save to DB as comma-separated string
            })

            if serializer.is_valid():
                resume = serializer.save(user=request.user)
                return Response({
                    'id': resume.id,
                    'name': resume.name,
                    'skills': parsed_data['skills']  # Return as list
                }, status=status.HTTP_201_CREATED)
            else:
                print("Serializer errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Parsing failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobMatchView(APIView):
    def get(self, request):
        try:
            from .models import MatchedJob
            from .serializers import MatchedJobSerializer

            resume = Resume.objects.filter(user=request.user).latest('uploaded_at')
            skills = [s.strip().lower() for s in resume.skills.split(',') if s.strip()]
            description_blob = f"{resume.skills} {resume.experience} {resume.education} {resume.projects}".lower()

            def infer_field(text):
                mapping = {
                    "software developer": ['python', 'django', 'react', 'html', 'css', 'javascript', 'api', 'node', 'vue', 'flask'],
                    "frontend developer": ['react', 'vue', 'html', 'css', 'tailwind', 'bootstrap'],
                    "backend developer": ['django', 'flask', 'node', 'express', 'api', 'sql'],
                    "full stack developer": ['django', 'react', 'node', 'html', 'css', 'express'],
                    "data analyst": ['pandas', 'numpy', 'excel', 'tableau', 'sql', 'power bi', 'matplotlib'],
                    "data scientist": ['ml', 'tensorflow', 'scikit', 'pytorch', 'statistics'],
                    "cybersecurity": ['nmap', 'burpsuite', 'kali', 'penetration', 'ctf', 'owasp'],
                    "electrical engineer": ['proteus', 'arduino', 'circuit', 'microcontroller', 'power', 'ltspice', 'electrical'],
                    "civil engineer": ['autocad', 'construction', 'structural', 'surveying'],
                    "mechanical engineer": ['solidworks', 'fea', 'thermodynamics', 'mechanical', 'catia']
                }

                for role, keywords in mapping.items():
                    for keyword in keywords:
                        if keyword in text:
                            return role
                return "engineer"

            job_category = infer_field(description_blob)

            matched_jobs = []

            remotive_resp = requests.get(f"https://remotive.io/api/remote-jobs?search={job_category}")
            if remotive_resp.ok:
                for job in remotive_resp.json().get('jobs', []):
                    title = job['title'].lower()
                    desc = job['description'].lower()
                    score = sum(1 for s in skills if s in title or s in desc)
                    if score > 0 or job_category in title:
                        job_id = f"remotive-{job['id']}"
                        matched_jobs.append({
                            'id': job_id,
                            'source': 'Remotive',
                            'title': job['title'],
                            'company': job['company_name'],
                            'location': job['candidate_required_location'],
                            'url': job['url'],
                            'description': job['description'],
                            'score': score + 1
                        })

                        if not MatchedJob.objects.filter(job_id=job_id).exists():
                            MatchedJob.objects.create(
                                job_id=job_id,
                                source='Remotive',
                                title=job['title'],
                                company=job['company_name'],
                                location=job['candidate_required_location'],
                                url=job['url'],
                                description=job['description'],
                                score=score + 1
                            )

            headers = {
                "X-RapidAPI-Key": "66ade11726mshe107734a3ff747fp1c3813jsnbc04ecd6d960",
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            jsearch_url = f"https://jsearch.p.rapidapi.com/search?query={job_category}&num_pages=1"
            jsearch_resp = requests.get(jsearch_url, headers=headers)
            if jsearch_resp.ok:
                for job in jsearch_resp.json().get('data', []):
                    title = job['job_title'].lower()
                    desc = job['job_description'].lower()
                    score = sum(1 for s in skills if s in title or s in desc)
                    if score > 0 or job_category in title:
                        job_id = f"jsearch-{job['job_id']}"
                        matched_jobs.append({
                            'id': job_id,
                            'source': 'JSearch',
                            'title': job['job_title'],
                            'company': job['employer_name'],
                            'location': job.get('job_city') or 'N/A',
                            'url': job.get('job_apply_link'),
                            'description': job.get('job_description'),
                            'score': score + 1
                        })

                        if not MatchedJob.objects.filter(job_id=job_id).exists():
                            MatchedJob.objects.create(
                                job_id=job_id,
                                source='JSearch',
                                title=job['job_title'],
                                company=job['employer_name'],
                                location=job.get('job_city') or 'N/A',
                                url=job.get('job_apply_link'),
                                description=job.get('job_description'),
                                score=score + 1
                            )

            matched_jobs = sorted(matched_jobs, key=lambda x: x['score'], reverse=True)
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 5))
            start, end = (page - 1) * size, page * size
            paginated = matched_jobs[start:end]

            return Response({
                'results': paginated,
                'total': len(matched_jobs),
                'page': page,
                'pages': (len(matched_jobs) + size - 1) // size,
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SaveJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        
        print("Incoming job save request:", data) 

        serializer = SavedJobSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Job saved'})
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=400)


class GetSavedJobs(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        jobs = SavedJob.objects.filter(user=request.user).order_by('-saved_at')
        serializer = SavedJobSerializer(jobs, many=True)
        return Response(serializer.data)


class JobDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, job_id):
        try:
            job = MatchedJob.objects.get(job_id=job_id)
            serializer = MatchedJobSerializer(job)
            return Response(serializer.data)
        except MatchedJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=404)


# class RemoveSavedJobView(APIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, job_id):
#         jobs = SavedJob.objects.filter(user=request.user, job_id=job_id)
#         if jobs.exists():
#             count, _ = jobs.delete()
#             return Response({'message': f'{count} job(s) removed successfully'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'error': 'Job not found or not saved by user'}, status=status.HTTP_404_NOT_FOUND)
        
# class RemoveSavedJobView(APIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, job_id):
#         try:
#             saved_job = SavedJob.objects.get(user=request.user, job_id=job_id)
#             saved_job.delete()
#             return Response({'message': 'Saved job removed successfully'})
#         except SavedJob.DoesNotExist:
#             return Response({'error': 'Saved job not found'}, status=404)


class RemoveSavedJobView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, job_id):
        try:
            job = SavedJob.objects.get(user=request.user, job_id=job_id)
            job.delete()
            return Response({'message': 'Saved job removed successfully'})
        except SavedJob.DoesNotExist:
            return Response({'error': 'Saved job not found'}, status=404)
