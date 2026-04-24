from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import EmergencyReport, FireStation, StationPersonnel, IncidentResponseLog, AuditLog, StationEquipment, FireTruck
from .serializers import EmergencyReportSerializer, FireStationSerializer, StationPersonnelSerializer, IncidentResponseLogSerializer, StationEquipmentSerializer, FireTruckSerializer
from .permissions import IsStationUser

def log_action(user, action, target):
    AuditLog.objects.create(user=user, action=action, target=str(target))

class StationEmergencyReportViewSet(viewsets.ModelViewSet):
    """Station create, view and update Emergency Reports"""
    serializer_class = EmergencyReportSerializer
    permission_classes = [IsStationUser]
    http_method_names = ['get', 'post', 'patch']  # View, create, and update
    
    def get_queryset(self):
        # Station users see all reports (they can respond to any emergency)
        return EmergencyReport.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        obj = serializer.save(reported_by=self.request.user)
        log_action(self.request.user, 'Created Emergency Report', f'Report #{obj.id} — {obj.title}')

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        if response.status_code == 200:
            obj = self.get_object()
            log_action(request.user, f'Updated Report status to {obj.status}', f'Report #{obj.id} — {obj.title}')
        return response

class StationNotificationsViewSet(viewsets.ViewSet):
    """Polling-based notifications for station users"""
    permission_classes = [IsStationUser]

    def list(self, request):
        new_reports = EmergencyReport.objects.filter(
            status='pending'
        ).order_by('-created_at')

        return Response({
            'count': new_reports.count(),
            'reports': EmergencyReportSerializer(new_reports, many=True).data,
        })

class StationResponseLogViewSet(viewsets.ViewSet):
    """Station create/update response log for a report"""
    permission_classes = [IsStationUser]

    def retrieve(self, request, pk=None):
        try:
            log = IncidentResponseLog.objects.get(report_id=pk)
            return Response(IncidentResponseLogSerializer(log).data)
        except IncidentResponseLog.DoesNotExist:
            return Response(None)

    def create_or_update(self, request, pk=None):
        personnel_ids = request.data.get('personnel_deployed_ids', [])
        data = {
            'time_dispatched': request.data.get('time_dispatched') or None,
            'time_arrived': request.data.get('time_arrived') or None,
            'equipment_used': request.data.get('equipment_used', ''),
            'notes': request.data.get('notes', ''),
        }
        try:
            log = IncidentResponseLog.objects.get(report_id=pk)
            for k, v in data.items():
                setattr(log, k, v)
            log.save()
        except IncidentResponseLog.DoesNotExist:
            report = EmergencyReport.objects.get(pk=pk)
            log = IncidentResponseLog.objects.create(report=report, logged_by=request.user, **data)
        log.personnel_deployed.set(personnel_ids)
        return Response(IncidentResponseLogSerializer(log).data)

class StationPersonnelViewSet(viewsets.ModelViewSet):
    """Station view and update their own personnel status"""
    serializer_class = StationPersonnelSerializer
    permission_classes = [IsStationUser]
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.fire_station:
            return StationPersonnel.objects.filter(fire_station=user.profile.fire_station)
        return StationPersonnel.objects.none()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_action(request.user, f'Updated Personnel status to {instance.status}', f'{instance.first_name} {instance.last_name}')
        return Response(serializer.data)

class StationDashboardViewSet(viewsets.ViewSet):
    """Station dashboard statistics"""
    permission_classes = [IsStationUser]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get station dashboard statistics"""
        # Get all reports (station can respond to any emergency)
        total_reports = EmergencyReport.objects.count()
        pending_reports = EmergencyReport.objects.filter(status='pending').count()
        responding_reports = EmergencyReport.objects.filter(status='responding').count()
        resolved_reports = EmergencyReport.objects.filter(status='resolved').count()
        
        recent_reports = EmergencyReport.objects.order_by('-created_at')[:5]
        
        return Response({
            'total_reports': total_reports,
            'pending_reports': pending_reports,
            'responding_reports': responding_reports,
            'resolved_reports': resolved_reports,
            'recent_reports': EmergencyReportSerializer(recent_reports, many=True).data,
        })

class StationStatisticsViewSet(viewsets.ViewSet):
    """Station statistics"""
    permission_classes = [IsStationUser]
    
    @action(detail=False, methods=['get'])
    def index(self, request):
        """Get station statistics"""
        total_reports = EmergencyReport.objects.count()
        pending_reports = EmergencyReport.objects.filter(status='pending').count()
        responding_reports = EmergencyReport.objects.filter(status='responding').count()
        resolved_reports = EmergencyReport.objects.filter(status='resolved').count()
        
        # Reports by priority
        reports_by_priority = {
            'critical': EmergencyReport.objects.filter(priority='critical').count(),
            'high': EmergencyReport.objects.filter(priority='high').count(),
            'medium': EmergencyReport.objects.filter(priority='medium').count(),
            'low': EmergencyReport.objects.filter(priority='low').count(),
        }
        
        return Response({
            'total_reports': total_reports,
            'pending_reports': pending_reports,
            'responding_reports': responding_reports,
            'resolved_reports': resolved_reports,
            'reports_by_priority': reports_by_priority,
        })
    
    def list(self, request):
        """Alias for index"""
        return self.index(request)

class StationFireTruckViewSet(viewsets.ModelViewSet):
    serializer_class = FireTruckSerializer
    permission_classes = [IsStationUser]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.fire_station:
            return FireTruck.objects.filter(fire_station=user.profile.fire_station)
        return FireTruck.objects.none()

    def perform_create(self, serializer):
        serializer.save(fire_station=self.request.user.profile.fire_station)


class StationEquipmentViewSet(viewsets.ModelViewSet):
    """Station users manage their own station's equipment"""
    serializer_class = StationEquipmentSerializer
    permission_classes = [IsStationUser]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.fire_station:
            return StationEquipment.objects.filter(fire_station=user.profile.fire_station)
        return StationEquipment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(fire_station=user.profile.fire_station)


class StationProfileViewSet(viewsets.ViewSet):
    """Station profile information"""
    permission_classes = [IsStationUser]
    
    @action(detail=False, methods=['get'])
    def index(self, request):
        """Get station profile"""
        user = request.user
        if hasattr(user, 'profile') and user.profile.fire_station:
            station = user.profile.fire_station
            serializer = FireStationSerializer(station)
            return Response(serializer.data)
        return Response({'error': 'No station assigned'}, status=status.HTTP_404_NOT_FOUND)
    
    def list(self, request):
        """Alias for index"""
        return self.index(request)
