def get_user_role(user):
    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return 'admin'

    profile = getattr(user, 'profile', None)
    return getattr(profile, 'role', 'public')


def sync_user_role(user):
    profile = getattr(user, 'profile', None)
    if profile is None:
        return 'admin' if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False) else 'public'

    effective_role = get_user_role(user)
    if profile.role != effective_role:
        profile.role = effective_role
        profile.save(update_fields=['role'])

    return effective_role
