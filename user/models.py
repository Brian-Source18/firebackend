from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .roles import get_user_role

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('public', 'Public User'),
        ('station', 'Fire Station'),
        ('admin', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='public')
    fire_station = models.ForeignKey(
        'FireStation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='station_users',
        help_text='Assigned fire station (for station users only)'
    )
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, role=get_user_role(instance))

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    profile, _ = UserProfile.objects.get_or_create(
        user=instance,
        defaults={'role': get_user_role(instance)}
    )
    effective_role = get_user_role(instance)
    if profile.role != effective_role:
        profile.role = effective_role
        profile.save(update_fields=['role'])
    else:
        profile.save()

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'News'

    def __str__(self):
        return self.title

class FirePrevention(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='prevention_images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Fire Prevention Tips'

    def __str__(self):
        return self.title

class FireStation(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_number = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    station_type = models.CharField(max_length=50, choices=[('main', 'Main Station'), ('sub', 'Sub Station')])
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['station_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_station_type_display()})"

class HeroicAct(models.Model):
    title = models.CharField(max_length=200)
    story = models.TextField()
    date_of_incident = models.DateField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='heroic_acts/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_of_incident']
        verbose_name_plural = 'Heroic Acts'

    def __str__(self):
        return self.title

class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('emergency', 'Emergency'),
        ('warning', 'Warning'),
        ('info', 'Information'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='info')
    image = models.ImageField(upload_to='announcement_images/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class EmergencyReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responding', 'Responding'),
        ('resolved', 'Resolved'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    ALARM_LEVEL_CHOICES = [
        ('1st', '1st Alarm'),
        ('2nd', '2nd Alarm'),
        ('3rd', '3rd Alarm'),
        ('4th', '4th Alarm'),
        ('5th', '5th Alarm'),
        ('task_force_alpha', 'Task Force Alpha'),
        ('task_force_bravo', 'Task Force Bravo'),
        ('task_force_charlie', 'Task Force Charlie'),
        ('task_force_delta', 'Task Force Delta'),
        ('general_alarm', 'General Alarm'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    alarm_level = models.CharField(max_length=20, choices=ALARM_LEVEL_CHOICES, null=True, blank=True)
    resolution_notes = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='emergency_reports/', blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True, default='')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.status}"

class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    score = models.IntegerField()
    total_questions = models.IntegerField(default=10)
    passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.score}/{self.total_questions}"

class FireStatistics(models.Model):
    year = models.IntegerField()
    total_incidents = models.IntegerField(default=0)
    lives_saved = models.IntegerField(default=0)
    properties_protected = models.IntegerField(default=0)
    avg_response_time = models.DecimalField(max_digits=5, decimal_places=2, help_text="In minutes")
    electrical_fires = models.IntegerField(default=0)
    cooking_fires = models.IntegerField(default=0)
    smoking_fires = models.IntegerField(default=0)
    other_fires = models.IntegerField(default=0)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year']
        verbose_name_plural = 'Fire Statistics'
    
    def __str__(self):
        return f"Fire Statistics {self.year}"

class StationPersonnel(models.Model):
    RANK_CHOICES = [
        ('fire_marshal', 'Fire Marshal'),
        ('senior_fire_officer', 'Senior Fire Officer'),
        ('fire_officer', 'Fire Officer'),
        ('firefighter', 'Firefighter'),
    ]
    STATUS_CHOICES = [
        ('on_duty', 'On Duty'),
        ('on_leave', 'On Leave'),
        ('absent', 'Absent'),
        ('inactive', 'Inactive'),
    ]

    fire_station = models.ForeignKey(FireStation, on_delete=models.CASCADE, related_name='personnel')
    first_name = models.CharField(max_length=100)
    middle_initial = models.CharField(max_length=1, blank=True)
    last_name = models.CharField(max_length=100)
    rank = models.CharField(max_length=30, choices=RANK_CHOICES, default='firefighter')
    contact_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_rank_display()}"

class IncidentResponseLog(models.Model):
    report = models.OneToOneField(EmergencyReport, on_delete=models.CASCADE, related_name='response_log')
    time_dispatched = models.DateTimeField(null=True, blank=True)
    time_arrived = models.DateTimeField(null=True, blank=True)
    personnel_deployed = models.ManyToManyField(StationPersonnel, blank=True, related_name='response_logs')
    equipment_used = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    logged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Log for Report #{self.report.id}"

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} — {self.action} — {self.target}"

class FireTruck(models.Model):
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('damaged', 'Damaged'),
        ('under_repair', 'Under Repair'),
    ]
    WATER_CHOICES = [
        ('full', 'Full'),
        ('half', 'Half'),
        ('empty', 'Empty'),
    ]

    fire_station = models.ForeignKey(FireStation, on_delete=models.CASCADE, related_name='fire_trucks')
    truck_number = models.CharField(max_length=50)
    model = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    water_level = models.CharField(max_length=10, choices=WATER_CHOICES, default='full')
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['truck_number']

    def __str__(self):
        return f"{self.truck_number} — {self.fire_station.name}"


class StationEquipment(models.Model):
    CATEGORY_CHOICES = [
        ('suppression', 'Fire Suppression Equipment'),
        ('rescue', 'Rescue Equipment'),
        ('ppe', 'Personal Protective Equipment'),
        ('detection', 'Search & Detection Tools'),
        ('medical', 'Medical Equipment'),
        ('ventilation', 'Ventilation & Support Tools'),
    ]
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('damaged', 'Damaged'),
        ('under_repair', 'Under Repair'),
    ]
    EQUIPMENT_CHOICES = [
        ('fire_hose', 'Fire Hose'),
        ('nozzle', 'Nozzle'),
        ('fire_hydrant', 'Fire Hydrant'),
        ('fire_extinguisher', 'Fire Extinguisher'),
        ('fire_pump', 'Fire Pump'),
        ('foam_system', 'Foam System'),
        ('ladder', 'Ladder (Extension & Aerial)'),
        ('hydraulic_cutter', 'Hydraulic Cutter/Spreader (Jaws of Life)'),
        ('axe_halligan', 'Axe & Halligan Tool'),
        ('rope_harness', 'Rope & Harness'),
        ('crowbar', 'Crowbar'),
        ('turnout_gear', 'Fire-Resistant Suit (Turnout Gear)'),
        ('helmet', 'Helmet'),
        ('gloves_boots', 'Gloves & Boots'),
        ('scba', 'SCBA (Self-Contained Breathing Apparatus)'),
        ('flashlight', 'Flashlight'),
        ('thermal_camera', 'Thermal Imaging Camera'),
        ('gas_detector', 'Gas Detector'),
        ('radio', 'Radio'),
        ('first_aid_kit', 'First Aid Kit'),
        ('aed', 'AED (Automated External Defibrillator)'),
        ('stretcher', 'Stretcher'),
        ('oxygen_tank', 'Oxygen Tank'),
        ('ventilation_fan', 'Ventilation Fan'),
        ('generator', 'Generator'),
        ('chainsaw', 'Chainsaw'),
    ]

    fire_station = models.ForeignKey(FireStation, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=100, choices=EQUIPMENT_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    operational = models.PositiveIntegerField(default=0)
    damaged = models.PositiveIntegerField(default=0)
    under_repair = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']
        unique_together = ['fire_station', 'name']

    def __str__(self):
        return f"{self.get_name_display()} — {self.fire_station.name}"


class UserStory(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    title = models.CharField(max_length=200)
    story = models.TextField()
    image = models.ImageField(upload_to='user_stories/')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.submitted_by.username}"


class Feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    name = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback from {self.user or self.name} — {self.rating}★"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('emergency', 'Emergency Procedures'),
        ('safety', 'Fire Safety'),
        ('equipment', 'Equipment & Tools'),
        ('permits', 'Permits & Regulations'),
        ('prevention', 'Fire Prevention'),
        ('training', 'Training & Education'),
    ]
    
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='safety')
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
    
    def __str__(self):
        return self.question[:50]
