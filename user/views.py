from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import News, FirePrevention, FireStation, HeroicAct, Announcement, EmergencyReport, QuizResult, FireStatistics, FAQ, Feedback, IncidentResponseLog, StationEquipment, UserStory
from .serializers import NewsSerializer, FirePreventionSerializer, FireStationSerializer, HeroicActSerializer, AnnouncementSerializer, EmergencyReportSerializer, QuizResultSerializer, FireStatisticsSerializer, FAQSerializer, FeedbackSerializer, StationEquipmentSerializer, UserStorySerializer

class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.filter(is_active=True)
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]

class FirePreventionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FirePrevention.objects.filter(is_active=True)
    serializer_class = FirePreventionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class FireStationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FireStation.objects.filter(is_active=True)
    serializer_class = FireStationSerializer
    permission_classes = [AllowAny]

class HeroicActViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HeroicAct.objects.filter(is_active=True)
    serializer_class = HeroicActSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Announcement.objects.filter(is_active=True)
    serializer_class = AnnouncementSerializer
    permission_classes = [AllowAny]

@method_decorator(csrf_exempt, name='dispatch')
class EmergencyReportViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyReportSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return EmergencyReport.objects.all()
        return EmergencyReport.objects.filter(reported_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)
    
    def destroy(self, request, *args, **kwargs):
        report = self.get_object()
        if report.status != 'pending':
            return Response({'error': 'Only pending reports can be cancelled.'}, status=400)
        if report.reported_by != request.user:
            return Response({'error': 'You can only cancel your own reports.'}, status=403)
        report.delete()
        return Response(status=204)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(reported_by=self.request.user)
        else:
            from django.contrib.auth.models import User
            anonymous_user, _ = User.objects.get_or_create(
                username='anonymous_reporter',
                defaults={'email': 'anonymous@system.local'}
            )
            serializer.save(reported_by=anonymous_user)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='track')
    def track(self, request, pk=None):
        try:
            report = EmergencyReport.objects.get(pk=pk)
            return Response({
                'id': report.id,
                'title': report.title,
                'location': report.location,
                'status': report.status,
                'priority': report.priority,
                'created_at': report.created_at,
                'updated_at': report.updated_at,
            })
        except EmergencyReport.DoesNotExist:
            return Response({'error': 'Report not found'}, status=404)

class QuizResultViewSet(viewsets.ModelViewSet):
    serializer_class = QuizResultSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']
    
    def get_queryset(self):
        return QuizResult.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        score = serializer.validated_data['score']
        total = serializer.validated_data.get('total_questions', 10)
        passed = (score / total) >= 0.8
        serializer.save(user=self.request.user, passed=passed)

class FireStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FireStatistics.objects.all()
    serializer_class = FireStatisticsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


class PublicEquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StationEquipmentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = StationEquipment.objects.all()
        station_id = self.request.query_params.get('station')
        if station_id:
            qs = qs.filter(fire_station_id=station_id)
        return qs


class LiveStatisticsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        from django.db.models import Avg, F, ExpressionWrapper, DurationField
        from django.utils import timezone

        current_year = timezone.now().year
        year = int(request.query_params.get('year', current_year))

        # Past years from manually entered FireStatistics
        manual_years = list(FireStatistics.objects.values_list('year', flat=True).order_by('-year'))
        all_years = sorted(set([current_year] + manual_years), reverse=True)

        # If requesting a past year that has manual data, return that
        if year != current_year:
            try:
                manual = FireStatistics.objects.get(year=year)
                return Response({
                    'year': year,
                    'is_live': False,
                    'available_years': all_years,
                    'total_incidents': manual.total_incidents,
                    'avg_response_time': float(manual.avg_response_time),
                    'lives_saved': manual.lives_saved,
                    'properties_protected': manual.properties_protected,
                    'electrical_fires': manual.electrical_fires,
                    'cooking_fires': manual.cooking_fires,
                    'smoking_fires': manual.smoking_fires,
                    'other_fires': manual.other_fires,
                    'pending': 0,
                    'responding': 0,
                    'resolved': manual.total_incidents,
                })
            except FireStatistics.DoesNotExist:
                pass

        # Live data for current year
        reports = EmergencyReport.objects.filter(created_at__year=year)
        total_incidents = reports.count()

        logs = IncidentResponseLog.objects.filter(
            report__created_at__year=year,
            time_dispatched__isnull=False,
            time_arrived__isnull=False,
        ).annotate(
            duration=ExpressionWrapper(F('time_arrived') - F('time_dispatched'), output_field=DurationField())
        )
        avg_seconds = logs.aggregate(avg=Avg('duration'))['avg']
        avg_response_time = round(avg_seconds.total_seconds() / 60, 1) if avg_seconds else 0

        critical_high = reports.filter(priority__in=['critical', 'high']).count()
        medium = reports.filter(priority='medium').count()
        low = reports.filter(priority='low').count()
        other = reports.exclude(priority__in=['critical', 'high', 'medium', 'low']).count()

        try:
            manual = FireStatistics.objects.get(year=year)
            lives_saved = manual.lives_saved
            properties_protected = manual.properties_protected
        except FireStatistics.DoesNotExist:
            lives_saved = 0
            properties_protected = 0

        return Response({
            'year': year,
            'is_live': True,
            'available_years': all_years,
            'total_incidents': total_incidents,
            'avg_response_time': avg_response_time,
            'lives_saved': lives_saved,
            'properties_protected': properties_protected,
            'electrical_fires': critical_high,
            'cooking_fires': medium,
            'smoking_fires': low,
            'other_fires': other,
            'pending': reports.filter(status='pending').count(),
            'responding': reports.filter(status='responding').count(),
            'resolved': reports.filter(status='resolved').count(),
        })


class UserStoryViewSet(viewsets.ModelViewSet):
    serializer_class = UserStorySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return UserStory.objects.filter(submitted_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


class FeaturedStoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserStorySerializer
    permission_classes = [AllowAny]
    queryset = UserStory.objects.filter(status='approved')


class RespondingEmergencyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmergencyReportSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return EmergencyReport.objects.filter(
            status='responding',
            latitude__isnull=False,
            longitude__isnull=False
        )


class EmergencyHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmergencyReportSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return EmergencyReport.objects.filter(
            status='resolved'
        ).order_by('-updated_at')[:10]
