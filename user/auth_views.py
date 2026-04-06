from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string
from .roles import get_user_role, sync_user_role

# Temporary in-memory store for reset codes: {username: {code, expiry}}
_reset_codes = {}

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    
    if not username or not email or not password:
        return Response({'error': 'Please provide username, email and password'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    # Profile is auto-created by signal with role='public'
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'User registered successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': get_user_role(user),
            'fire_station_id': user.profile.fire_station_id if user.profile.fire_station else None,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Please provide username and password'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    role = sync_user_role(user)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role,
            'fire_station_id': user.profile.fire_station_id if user.profile.fire_station else None,
            'fire_station_name': user.profile.fire_station.name if user.profile.fire_station else None,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def profile(request):
    user = request.user
    role = sync_user_role(user)
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': role,
        'fire_station_id': user.profile.fire_station_id if user.profile.fire_station else None,
    })

@api_view(['PATCH'])
def update_profile(request):
    user = request.user
    new_email = request.data.get('email')
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if new_email:
        if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            return Response({'error': 'Email already in use.'}, status=status.HTTP_400_BAD_REQUEST)
        user.email = new_email
        user.save()

    if new_password:
        if not current_password:
            return Response({'error': 'Current password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()

    return Response({'message': 'Profile updated successfully.'})

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    username = request.data.get('username')
    if not username:
        return Response({'error': 'Please provide your username'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'No account found with that username'}, status=status.HTTP_404_NOT_FOUND)
    
    if not user.email:
        return Response({'error': 'No email associated with this account'}, status=status.HTTP_400_BAD_REQUEST)
    
    code = ''.join(random.choices(string.digits, k=6))
    expiry = timezone.now() + timedelta(minutes=10)
    _reset_codes[username] = {'code': code, 'expiry': expiry}
    
    send_mail(
        subject='Password Reset Code - Cebu City Fire Department',
        message=f'Your password reset code is: {code}\n\nThis code expires in 10 minutes.\n\nIf you did not request this, please ignore this email.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    
    masked_email = user.email[:2] + '***@' + user.email.split('@')[1]
    return Response({'message': f'Reset code sent to {masked_email}'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    username = request.data.get('username')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    
    if not username or not code or not new_password:
        return Response({'error': 'Please provide username, code and new password'}, status=status.HTTP_400_BAD_REQUEST)
    
    reset_data = _reset_codes.get(username)
    if not reset_data:
        return Response({'error': 'No reset code found. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if timezone.now() > reset_data['expiry']:
        del _reset_codes[username]
        return Response({'error': 'Reset code has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if reset_data['code'] != code:
        return Response({'error': 'Invalid reset code'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        del _reset_codes[username]
        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
