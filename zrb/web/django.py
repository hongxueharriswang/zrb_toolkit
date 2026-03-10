from functools import wraps
from django.http import HttpResponseForbidden
from ..engine.access import AccessEngine
from ..core.types import AccessMode

class ZRBDjango:
    def __init__(self, get_response=None, engine: AccessEngine = None):
        self.get_response = get_response
        self.engine = engine

    def __call__(self, request):
        host = request.get_host()
        request.zone_id = self._zone_from_host(host)
        response = self.get_response(request)
        return response

    def _zone_from_host(self, host):
        if host.startswith("faculty."):
            return "zone_faculty"
        return "root"

    def n_rzbac(self, roles=None, operation=None):
        return self._decorator(roles, operation, AccessMode.DIRECT)

    def i_rzbac(self, roles=None, operation=None):
        return self._decorator(roles, operation, AccessMode.INFERENTIAL)

    def _decorator(self, roles, operation, mode):
        def decorator(view_func):
            @wraps(view_func)
            def _wrapped_view(request, *args, **kwargs):
                op_id = operation or self._resolve_operation(request)
                from ..core.models import User
                dj_user = request.user
                user = User(id=str(dj_user.id), username=dj_user.username, email=getattr(dj_user, 'email', ''), attributes={})
                zone = self.engine.storage.get_zone(getattr(request, 'zone_id', 'root'))
                op = self.engine.storage.get_operation(op_id)
                if not user or not zone or not op:
                    return HttpResponseForbidden()
                if not self.engine.decide(user, op, zone, mode):
                    return HttpResponseForbidden()
                return view_func(request, *args, **kwargs)
            return _wrapped_view
        return decorator

    def _resolve_operation(self, request):
        if hasattr(request, 'resolver_match') and request.resolver_match:
            return f"{request.resolver_match.app_name}:{request.resolver_match.url_name}"
        return ""
