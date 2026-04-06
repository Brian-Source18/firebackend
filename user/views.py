from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import News, FirePrevention, FireStation, HeroicAct, Announcement, EmergencyReport, QuizResult, FireStatistics, FAQ, Feedback
from .serializers import NewsSerializer, FirePreventionSerializer, FireStationSerializer, HeroicActSerializer, AnnouncementSerializer, EmergencyReportSerializer, QuizResultSerializer, FireStatisticsSerializer, FAQSerializer, FeedbackSerializer

class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.filter(is_active=True)
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class FirePreventionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FirePrevention.objects.filter(is_active=True)
    serializer_class = FirePreventionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class FireStationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FireStation.objects.filter(is_active=True)
    serializer_class = FireStationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class HeroicActViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HeroicAct.objects.filter(is_active=True)
    serializer_class = HeroicActSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Announcement.objects.filter(is_active=True)
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@method_decorator(csrf_exempt, name='dispatch')
class EmergencyReportViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyReportSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    http_method_names = ['get', 'post', 'patch', 'delete']
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return EmergencyReport.objects.all()
        return EmergencyReport.objects.filter(reported_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        print("\n=== CREATE REQUEST ===")
        print(f"User authenticated: {request.user.is_authenticated}")
        print(f"Request data: {request.data}")
        print(f"Request FILES: {request.FILES}")
        
        serializer = self.get_serializer(data=request.data)
        print(f"Serializer validation starting...")
        
        if not serializer.is_valid():
            print(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=400)
        
        print("Validation passed, calling perform_create")
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
        print("\n=== PERFORM CREATE ===")
        if self.request.user.is_authenticated:
            print(f"Authenticated user: {self.request.user.username}")
            serializer.save(reported_by=self.request.user)
        else:
            print("Anonymous user, using anonymous_reporter")
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


class RespondingEmergencyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmergencyReportSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return EmergencyReport.objects.filter(
            status='responding',
            latitude__isnull=False,
            longitude__isnull=False
        )
