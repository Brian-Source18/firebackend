from rest_framework import serializers
from django.contrib.auth.models import User
from .models import News, FirePrevention, FireStation, HeroicAct, Announcement, EmergencyReport, QuizResult, FireStatistics, FAQ, UserProfile, StationPersonnel, IncidentResponseLog, AuditLog, Feedback

class NewsSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return f'http://localhost:8000{obj.image.url}'
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = self.get_image_url(instance)
        return rep

    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'image', 'image_url', 'created_by_name', 'created_at', 'updated_at']

class FirePreventionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return f'http://localhost:8000{obj.image.url}'
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = self.get_image_url(instance)
        return rep

    class Meta:
        model = FirePrevention
        fields = ['id', 'title', 'description', 'image', 'image_url', 'created_by_name', 'created_at', 'updated_at']

class FireStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FireStation
        fields = ['id', 'name', 'address', 'contact_number', 'email', 'station_type', 'latitude', 'longitude']

class HeroicActSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return f'http://localhost:8000{obj.image.url}'
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = self.get_image_url(instance)
        return rep

    class Meta:
        model = HeroicAct
        fields = ['id', 'title', 'story', 'date_of_incident', 'location', 'image', 'image_url', 'created_by_name', 'created_at']

class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'priority', 'created_by_name', 'created_at', 'updated_at']

class EmergencyReportSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.CharField(source='reported_by.username', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return f'http://localhost:8000{obj.image.url}'
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = self.get_image_url(instance)
        return rep

    class Meta:
        model = EmergencyReport
        fields = ['id', 'title', 'description', 'location', 'latitude', 'longitude', 'priority', 'status', 'alarm_level', 'resolution_notes', 'image', 'image_url', 'contact_number', 'reported_by', 'reported_by_name', 'created_at', 'updated_at']
        read_only_fields = ['reported_by']

class QuizResultSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    percentage = serializers.SerializerMethodField()
    
    def get_percentage(self, obj):
        return round((obj.score / obj.total_questions) * 100)
    
    class Meta:
        model = QuizResult
        fields = ['id', 'user', 'username', 'score', 'total_questions', 'percentage', 'passed', 'completed_at']
        read_only_fields = ['user']

class FireStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FireStatistics
        fields = ['id', 'year', 'total_incidents', 'lives_saved', 'properties_protected', 'avg_response_time', 'electrical_fires', 'cooking_fires', 'smoking_fires', 'other_fires', 'updated_at']

class FeedbackSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'username', 'name', 'rating', 'message', 'created_at']
        read_only_fields = ['user']


class FAQSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'order', 'created_by_name', 'created_at', 'updated_at', 'is_active']

class StationPersonnelSerializer(serializers.ModelSerializer):
    fire_station_name = serializers.CharField(source='fire_station.name', read_only=True)
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StationPersonnel
        fields = ['id', 'fire_station', 'fire_station_name', 'first_name', 'middle_initial', 'last_name', 'rank', 'rank_display', 'contact_number', 'status', 'status_display', 'created_at']

class IncidentResponseLogSerializer(serializers.ModelSerializer):
    personnel_deployed = StationPersonnelSerializer(many=True, read_only=True)
    personnel_deployed_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=StationPersonnel.objects.all(), source='personnel_deployed'
    )
    logged_by_name = serializers.CharField(source='logged_by.username', read_only=True)
    logged_by_station = serializers.SerializerMethodField()

    def get_logged_by_station(self, obj):
        if obj.logged_by and hasattr(obj.logged_by, 'profile') and obj.logged_by.profile.fire_station:
            return obj.logged_by.profile.fire_station.name
        return None

    class Meta:
        model = IncidentResponseLog
        fields = ['id', 'report', 'time_dispatched', 'time_arrived', 'personnel_deployed', 'personnel_deployed_ids', 'equipment_used', 'notes', 'logged_by_name', 'logged_by_station', 'created_at', 'updated_at']
        read_only_fields = ['report', 'logged_by_name', 'logged_by_station']

class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'username', 'action', 'target', 'timestamp']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    fire_station = serializers.PrimaryKeyRelatedField(source='profile.fire_station', queryset=FireStation.objects.all(), required=False, allow_null=True)
    fire_station_name = serializers.CharField(source='profile.fire_station.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'fire_station', 'fire_station_name', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile fields
        if profile_data:
            profile = instance.profile
            if 'fire_station' in profile_data:
                profile.fire_station = profile_data['fire_station']
            profile.save()
        
        return instance

class CreateStationUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    fire_station = serializers.PrimaryKeyRelatedField(queryset=FireStation.objects.all(), required=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'email', 'first_name', 'last_name', 'fire_station']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        fire_station = validated_data.pop('fire_station')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Update profile
        user.profile.role = 'station'
        user.profile.fire_station = fire_station
        user.profile.save()
        
        return user
    
    def to_representation(self, instance):
        # Use UserSerializer for the response to avoid fire_station field error
        return UserSerializer(instance).data
