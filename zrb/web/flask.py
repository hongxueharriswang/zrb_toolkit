from functools import wraps
from flask import request, abort
from ..engine.access import AccessEngine
from ..core.types import AccessMode

class ZRBFlask:
    def __init__(self, app=None, engine: AccessEngine = None):
        self.engine = engine
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['zrb'] = self
        @app.before_request
        def set_zone():
            host = request.host
            request.zone_id = self._zone_from_host(host)

    def _zone_from_host(self, host: str) -> str:
        if host.startswith("faculty."):
            return "zone_faculty"
        return "root"

    def n_rzbac(self, roles=None, operation=None):
        return self._decorator(roles, operation, AccessMode.DIRECT)

    def i_rzbac(self, roles=None, operation=None):
        return self._decorator(roles, operation, AccessMode.INFERENTIAL)

    def _decorator(self, roles, operation, mode: AccessMode):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                op_id = operation or self._resolve_operation()
                try:
                    from flask_login import current_user
                except Exception:
                    abort(403)
                if not getattr(current_user, 'is_authenticated', False):
                    abort(403)
                from ..core.models import User
                user = User(id=str(current_user.id), username=getattr(current_user, 'username', str(current_user.id)), email=getattr(current_user, 'email', ''), attributes={})
                zone = self.engine.storage.get_zone(getattr(request, 'zone_id', 'root'))
                op = self.engine.storage.get_operation(op_id)
                if not user or not zone or not op:
                    abort(403)
                if not self.engine.decide(user, op, zone, mode):
                    abort(403)
                return f(*args, **kwargs)
            return decorated
        return decorator

    def _resolve_operation(self) -> str:
        return request.endpoint or ""
