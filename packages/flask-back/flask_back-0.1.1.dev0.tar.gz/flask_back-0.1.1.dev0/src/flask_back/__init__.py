# flask_back/__init__.py


from flask import request, session
from .version import __version__
from functools import wraps


class Back:
    def __init__(self, app=None, **settings):
        self._excluded_endpoints = set()
        self._default_url = "/"
        self._use_referrer = False

        if app:
            self.init_app(app, **settings)

    def init_app(self, app, **settings):
        self._excluded_endpoints = set(settings.get("excluded_endpoints", []))
        self._default_url = settings.get("default_url", "/")
        self._use_referrer = settings.get("use_referrer", False)

        app.before_request(self._before_request)
        app.context_processor(self._inject_back_url)
        app.extensions = getattr(app, "extensions", {})
        app.extensions["back"] = self

    def _before_request(self):
        if request.method != "GET":
            return

        if (request.endpoint in self._excluded_endpoints) or (request.path == '/go-back'):
            return

        session["back_url"] = request.path

    def save_url(self, func=None):
        if func is None:
            return self.save_url

        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == "GET":
                session["back_url"] = request.path
            return func(*args, **kwargs)

        return wrapper

    def get_url(self, default=None):
        if "back_url" in session:
            return session["back_url"]
        if self._use_referrer and request.referrer:
            return request.referrer
        return default or self._default_url

    def clear(self):
        session.pop("back_url", None)

    def exclude(self, func):
        self._excluded_endpoints.add(func.__name__)
        return func

    def _inject_back_url(self):
        return dict(back_url=self.get_url())
