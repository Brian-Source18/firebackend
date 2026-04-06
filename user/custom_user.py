from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('public', 'Public User'),
        ('station', 'Fire Station'),
        ('admin', 'Administrator'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='public'
    )
    
    fire_station = models.ForeignKey(
        'FireStation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='station_users',
        help_text='Assigned fire station (for station users only)'
    )
    
    class Meta:
        db_table = 'auth_user'  # Keep same table name to avoid migration issues
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
