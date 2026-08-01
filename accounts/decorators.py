from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*roles):
    """Restringe uma view a utilizadores pertencentes a um dos grupos indicados.
    Admins (grupo 'admin' ou superuser) têm sempre acesso.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_admin_role() or user.groups.filter(name__in=roles).exists():
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Não tem permissão para aceder a esta página.')
            return redirect('dashboard')
        return _wrapped
    return decorator
