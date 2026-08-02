from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def permission_required(*perms):
    """Restringe uma view a utilizadores com alguma das Permission indicadas
    (codename com prefixo de app, ex. 'vehicles.add_vehicleentry'). Superusers
    e membros de grupos com essa permissão atribuída têm sempre acesso - a
    ligação entre "quem pode o quê" fica toda em Group/Permission (giríveis em
    /admin/auth/group/), não hardcoded aqui.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if any(user.has_perm(perm) for perm in perms):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Não tem permissão para aceder a esta página.')
            return redirect('dashboard')
        return _wrapped
    return decorator
