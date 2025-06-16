from rest_framework import serializers 
from .models import Resume, SavedJob, MatchedJob

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ['user']
        
class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedJob
        fields = '__all__'


class MatchedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchedJob
        fields = '__all__'
