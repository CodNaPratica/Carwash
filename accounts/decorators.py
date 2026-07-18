from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*roles):
    """Restringe uma view a utilizadores com um dos roles indicados.
    Admins (role='admin' ou superuser) têm sempre acesso.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_admin_role() or user.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Não tem permissão para aceder a esta página.')
            return redirect('dashboard')
        return _wrapped
    return decorator
