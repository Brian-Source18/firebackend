from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import (
    NewsViewSet, FirePreventionViewSet, FireStationViewSet, HeroicActViewSet,
    AnnouncementViewSet, EmergencyReportViewSet, QuizResultViewSet,
    FireStatisticsViewSet, FAQViewSet, RespondingEmergencyViewSet,
    EmergencyHistoryViewSet, FeedbackViewSet, LiveStatisticsViewSet,
    PublicEquipmentViewSet, UserStoryViewSet, FeaturedStoryViewSet,
)
from user.admin_views import (
    AdminNewsViewSet, AdminFirePreventionViewSet, AdminFireStationViewSet,
    AdminHeroicActViewSet, AdminAnnouncementViewSet, AdminFAQViewSet,
    AdminFireStatisticsViewSet, AdminEmergencyReportViewSet, AdminQuizResultViewSet,
    AdminUserViewSet, AdminStationAccountViewSet, AdminDashboardViewSet, AdminPersonnelViewSet,
    AdminResponseLogViewSet, AdminAuditLogViewSet, AdminFeedbackViewSet, AdminEquipmentViewSet, AdminFireTruckViewSet,
    AdminUserStoryViewSet,
)
from user.station_views import (
    StationEmergencyReportViewSet, StationDashboardViewSet,
    StationStatisticsViewSet, StationProfileViewSet, StationPersonnelViewSet,
    StationNotificationsViewSet, StationResponseLogViewSet, StationEquipmentViewSet, StationFireTruckViewSet,
)
from user.auth_views import register, login, profile, update_profile, forgot_password, reset_password
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

# Public API router
router = DefaultRouter()
router.register(r'news', NewsViewSet)
router.register(r'fire-prevention', FirePreventionViewSet)
router.register(r'fire-stations', FireStationViewSet)
router.register(r'heroic-acts', HeroicActViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'emergency-reports', EmergencyReportViewSet, basename='emergency-report')
router.register(r'quiz-results', QuizResultViewSet, basename='quiz-result')
router.register(r'statistics', FireStatisticsViewSet)
router.register(r'faq', FAQViewSet)
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'responding-emergencies', RespondingEmergencyViewSet, basename='responding-emergencies')
router.register(r'emergency-history', EmergencyHistoryViewSet, basename='emergency-history')
router.register(r'live-statistics', LiveStatisticsViewSet, basename='live-statistics')
router.register(r'user-stories', UserStoryViewSet, basename='user-stories')
router.register(r'featured-stories', FeaturedStoryViewSet, basename='featured-stories')
router.register(r'station-equipment', PublicEquipmentViewSet, basename='public-equipment')

# Admin API router
admin_router = DefaultRouter()
admin_router.register(r'news', AdminNewsViewSet, basename='admin-news')
admin_router.register(r'fire-prevention', AdminFirePreventionViewSet, basename='admin-fire-prevention')
admin_router.register(r'fire-stations', AdminFireStationViewSet, basename='admin-fire-stations')
admin_router.register(r'heroic-acts', AdminHeroicActViewSet, basename='admin-heroic-acts')
admin_router.register(r'announcements', AdminAnnouncementViewSet, basename='admin-announcements')
admin_router.register(r'faq', AdminFAQViewSet, basename='admin-faq')
admin_router.register(r'statistics', AdminFireStatisticsViewSet, basename='admin-statistics')
admin_router.register(r'emergency-reports', AdminEmergencyReportViewSet, basename='admin-emergency-reports')
admin_router.register(r'quiz-results', AdminQuizResultViewSet, basename='admin-quiz-results')
admin_router.register(r'users', AdminUserViewSet, basename='admin-users')
admin_router.register(r'station-accounts', AdminStationAccountViewSet, basename='admin-station-accounts')
admin_router.register(r'personnel', AdminPersonnelViewSet, basename='admin-personnel')
admin_router.register(r'response-logs', AdminResponseLogViewSet, basename='admin-response-logs')
admin_router.register(r'feedback', AdminFeedbackViewSet, basename='admin-feedback')
admin_router.register(r'audit-logs', AdminAuditLogViewSet, basename='admin-audit-logs')
admin_router.register(r'dashboard', AdminDashboardViewSet, basename='admin-dashboard')
admin_router.register(r'equipment', AdminEquipmentViewSet, basename='admin-equipment')
admin_router.register(r'user-stories', AdminUserStoryViewSet, basename='admin-user-stories')
admin_router.register(r'fire-trucks', AdminFireTruckViewSet, basename='admin-fire-trucks')

# Station API router
station_router = DefaultRouter()
station_router.register(r'emergency-reports', StationEmergencyReportViewSet, basename='station-emergency-reports')
station_router.register(r'dashboard', StationDashboardViewSet, basename='station-dashboard')
station_router.register(r'statistics', StationStatisticsViewSet, basename='station-statistics')
station_router.register(r'personnel', StationPersonnelViewSet, basename='station-personnel')
station_router.register(r'profile', StationProfileViewSet, basename='station-profile')
station_router.register(r'notifications', StationNotificationsViewSet, basename='station-notifications')
station_router.register(r'equipment', StationEquipmentViewSet, basename='station-equipment')
station_router.register(r'fire-trucks', StationFireTruckViewSet, basename='station-fire-trucks')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/admin/', include(admin_router.urls)),
    path('api/station/', include(station_router.urls)),
    path('api/station/response-log/<int:pk>/', StationResponseLogViewSet.as_view({'get': 'retrieve', 'post': 'create_or_update'}), name='station-response-log'),
    path('api/auth/register/', register, name='register'),
    path('api/auth/login/', login, name='login'),
    path('api/auth/profile/', profile, name='profile'),
    path('api/auth/update-profile/', update_profile, name='update_profile'),
    path('api/auth/forgot-password/', forgot_password, name='forgot_password'),
    path('api/auth/reset-password/', reset_password, name='reset_password'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
