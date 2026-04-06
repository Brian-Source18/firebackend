from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from .models import News, FirePrevention, FireStation, HeroicAct, Announcement, EmergencyReport, QuizResult, FireStatistics, FAQ, StationPersonnel, IncidentResponseLog, AuditLog, Feedback, UserProfile
from .serializers import (
    NewsSerializer, FirePreventionSerializer, FireStationSerializer,
    HeroicActSerializer, AnnouncementSerializer, EmergencyReportSerializer,
    QuizResultSerializer, FireStatisticsSerializer, FAQSerializer,
    UserSerializer, CreateStationUserSerializer, StationPersonnelSerializer, IncidentResponseLogSerializer, AuditLogSerializer, FeedbackSerializer
)
from .permissions import IsAdminUser

def log_action(user, action, target):
    AuditLog.objects.create(user=user, action=action, target=str(target))

class AdminNewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        print(f"\n=== ADMIN NEWS CREATE ===")
        print(f"FILES: {request.FILES}")
        print(f"DATA: {request.data}")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        log_action(self.request.user, 'Added News', obj.title)

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request.user, 'Updated News', obj.title)

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Deleted News', instance.title)
        instance.delete()

class AdminFirePreventionViewSet(viewsets.ModelViewSet):
    queryset = FirePrevention.objects.all()
    serializer_class = FirePreventionSerializer
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        log_action(self.request.user, 'Added Fire Prevention Tip', obj.title)

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request.user, 'Updated Fire Prevention Tip', obj.title)

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Deleted Fire Prevention Tip', instance.title)
        instance.delete()

class AdminFireStationViewSet(viewsets.ModelViewSet):
    queryset = FireStation.objects.all()
    serializer_class = FireStationSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        log_action(self.request.user, 'Added Fire Station', obj.name)

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request.user, 'Updated Fire Station', obj.name)

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Deleted Fire Station', instance.name)
        instance.delete()

class AdminHeroicActViewSet(viewsets.ModelViewSet):
    queryset = HeroicAct.objects.all()
    serializer_class = HeroicActSerializer
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        log_action(self.request.user, 'Added Heroic Act', obj.title)

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request.user, 'Updated Heroic Act', obj.title)

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Deleted Heroic Act', instance.title)
        instance.delete()

class AdminAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        log_action(self.request.user, 'Added Announcement', obj.title)

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request.user, 'Updated Announcement', obj.title)

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Deleted Announcement', instance.title)
        instance.delete()

class AdminFeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        return Response({'count': Feedback.objects.filter(is_read=False).count()})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Feedback.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'ok'})


class AdminFAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
        log_action(self.request.user, 'Added FAQ', obj.question[:60])

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Deleted FAQ', instance.question[:60])
        instance.delete()

class AdminFireStatisticsViewSet(viewsets.ModelViewSet):
    """Admin CRUD for Fire Statistics"""
    queryset = FireStatistics.objects.all()
    serializer_class = FireStatisticsSerializer
    permission_classes = [IsAdminUser]
    
    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class AdminEmergencyReportViewSet(viewsets.ModelViewSet):
    queryset = EmergencyReport.objects.all()
    serializer_class = EmergencyReportSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'put', 'patch', 'delete']

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        return Response({'count': EmergencyReport.objects.filter(is_read=False).count()})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        EmergencyReport.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'ok'})

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request.user, f'Updated Report status to {obj.status}', f'Report #{obj.id} — {obj.title}')

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Deleted Emergency Report', f'Report #{instance.id} — {instance.title}')
        instance.delete()

class AdminQuizResultViewSet(viewsets.ModelViewSet):
    """Admin view and delete Quiz Results"""
    queryset = QuizResult.objects.all()
    serializer_class = QuizResultSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'delete']

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        return Response({'count': QuizResult.objects.filter(is_read=False).count()})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        QuizResult.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'ok'})

class AdminUserViewSet(viewsets.ModelViewSet):
    """Admin manage users"""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return User.objects.filter(profile__role='public').order_by('-date_joined')

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        return Response({'count': UserProfile.objects.filter(is_read=False, role='public').count()})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        UserProfile.objects.filter(is_read=False, role='public').update(is_read=True)
        return Response({'status': 'ok'})

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        if response.status_code == 200:
            user = self.get_object()
            action_label = 'Deactivated User' if not user.is_active else 'Reactivated User'
            log_action(request.user, action_label, user.username)
        return response

class AdminStationAccountViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(profile__role='station')
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateStationUserSerializer
        return UserSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        log_action(self.request.user, 'Created Station Account', obj.username)

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request.user, 'Updated Station Account', obj.username)

    def perform_destroy(self, instance):
        log_action(self.request.user, 'Deleted Station Account', instance.username)
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def available_stations(self, request):
        """Get list of fire stations that don't have assigned users yet"""
        assigned_station_ids = User.objects.filter(
            profile__role='station',
            profile__fire_station__isnull=False
        ).values_list('profile__fire_station_id', flat=True)
        
        available_stations = FireStation.objects.exclude(
            id__in=assigned_station_ids
        ).filter(is_active=True)
        
        serializer = FireStationSerializer(available_stations, many=True)
        return Response(serializer.data)

class AdminPersonnelViewSet(viewsets.ModelViewSet):
    """Admin full CRUD for Station Personnel"""
    queryset = StationPersonnel.objects.all()
    serializer_class = StationPersonnelSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = StationPersonnel.objects.all()
        station_id = self.request.query_params.get('station')
        if station_id:
            qs = qs.filter(fire_station_id=station_id)
        return qs

class AdminResponseLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IncidentResponseLog.objects.all()
    serializer_class = IncidentResponseLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = IncidentResponseLog.objects.all()
        report_id = self.request.query_params.get('report')
        if report_id:
            qs = qs.filter(report_id=report_id)
        return qs

class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]

class AdminDashboardViewSet(viewsets.ViewSet):
    """Admin dashboard statistics"""
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics"""
        total_users = User.objects.filter(profile__role='public').count()
        total_stations = FireStation.objects.filter(is_active=True).count()
        total_station_accounts = User.objects.filter(profile__role='station').count()
        total_news = News.objects.filter(is_active=True).count()
        total_prevention_tips = FirePrevention.objects.filter(is_active=True).count()
        pending_reports = EmergencyReport.objects.filter(status='pending').count()
        total_reports = EmergencyReport.objects.count()
        total_quiz_results = QuizResult.objects.count()
        
        recent_reports = EmergencyReport.objects.order_by('-created_at')[:5]
        recent_quiz_results = QuizResult.objects.order_by('-completed_at')[:5]
        
        return Response({
            'total_users': total_users,
            'total_stations': total_stations,
            'total_station_accounts': total_station_accounts,
            'total_news': total_news,
            'total_prevention_tips': total_prevention_tips,
            'pending_reports': pending_reports,
            'total_reports': total_reports,
            'total_quiz_results': total_quiz_results,
            'recent_reports': EmergencyReportSerializer(recent_reports, many=True).data,
            'recent_quiz_results': QuizResultSerializer(recent_quiz_results, many=True).data,
        })
