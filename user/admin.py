from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, News, FirePrevention, FireStation, HeroicAct, Announcement, EmergencyReport, QuizResult, FireStatistics, FAQ

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'get_role', 'get_fire_station', 'is_staff', 'is_active']
    list_filter = ['profile__role', 'is_staff', 'is_active']
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'N/A'
    get_role.short_description = 'Role'
    
    def get_fire_station(self, obj):
        return obj.profile.fire_station.name if hasattr(obj, 'profile') and obj.profile.fire_station else 'N/A'
    get_fire_station.short_description = 'Fire Station'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'content']
    exclude = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(FirePrevention)
class FirePreventionAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    exclude = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(FireStation)
class FireStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'station_type', 'contact_number', 'latitude', 'longitude', 'is_active']
    list_filter = ['is_active', 'station_type']
    search_fields = ['name', 'address']
    exclude = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(HeroicAct)
class HeroicActAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_of_incident', 'location', 'created_by', 'is_active']
    list_filter = ['is_active', 'date_of_incident']
    search_fields = ['title', 'story', 'location']
    exclude = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active', 'priority', 'created_at']
    search_fields = ['title', 'message']
    exclude = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(EmergencyReport)
class EmergencyReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'reported_by', 'priority', 'status', 'location', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description', 'location', 'reported_by__username']
    readonly_fields = ['reported_by', 'created_at', 'updated_at']

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'score', 'total_questions', 'passed', 'completed_at']
    list_filter = ['passed', 'completed_at']
    search_fields = ['user__username']
    readonly_fields = ['user', 'completed_at']

@admin.register(FireStatistics)
class FireStatisticsAdmin(admin.ModelAdmin):
    list_display = ['year', 'total_incidents', 'lives_saved', 'avg_response_time', 'updated_at']
    list_filter = ['year']
    fields = ['year', 'total_incidents', 'lives_saved', 'properties_protected', 'avg_response_time', 'electrical_fires', 'cooking_fires', 'smoking_fires', 'other_fires']
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['question', 'answer']
    exclude = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
