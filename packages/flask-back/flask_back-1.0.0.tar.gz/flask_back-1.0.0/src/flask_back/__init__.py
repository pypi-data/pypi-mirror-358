# flask_back/__init__.py


from flask import request, session
from .version import __version__
from functools import wraps


class Back:
    def __init__(self, app=None, **settings):

        """
        Initialize a Back instance.

        If an app is given, this calls `init_app` with the given settings.

        :param app: The Flask app to integrate with
        :param settings: Keyword arguments to pass to `init_app`
        """
        self._excluded_endpoints = set()
        self._default_url = "/"
        self._use_referrer = False

        if app:
            self.init_app(app, **settings)

    def init_app(self, app, **settings):
        """
        Initialize the extension with an app. This is typically called
        automatically when the extension is initialized with an app.

        Parameters
        ----------
        app : Flask
            The flask app to initialize the extension with.
        **settings
            Additional keyword arguments that can be passed to configure the
            extension. Recognized settings are:

            excluded_endpoints : list
                A list of endpoints that should not have their URLs saved.
            default_url : str
                The default URL to go back to if no other URL is saved.
            use_referrer : bool
                Whether to use the HTTP referrer header to determine where to
                go back to.

        """
        self._excluded_endpoints = set(settings.get("excluded_endpoints", []))
        self._default_url = settings.get("default_url", "/")
        self._use_referrer = settings.get("use_referrer", False)

        app.before_request(self._before_request)
        app.context_processor(self._inject_back_url)
        app.extensions = getattr(app, "extensions", {})
        app.extensions["back"] = self

    def _before_request(self):
        """
        Save the current URL if the request is a GET and the endpoint is not
        excluded.

        This is called automatically by the app before each request.

        """
        if request.method != "GET":
            return

        if (request.endpoint in self._excluded_endpoints) or (request.path == '/go-back'):
            return

        session["back_url"] = request.path

    def save_url(self, func=None):
        """
        Decorator to save the current URL before calling the given function.

        If the request method is GET, the current URL is saved to the session.
        If the request method is not GET, the URL is not saved.

        This is useful if you want a specific view function to save the current
        URL, without having to manually check the request method.

        If no function is given, this returns the decorator itself, which can
        be used as a decorator.

        :param func: The view function to decorate
        :return: The decorated view function
        """
        if func is None:
            return self.save_url

        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == "GET":
                session["back_url"] = request.path
            return func(*args, **kwargs)

        return wrapper

    def get_url(self, default=None):
        """
        Get the URL to go back to.

        If the request method is GET and the endpoint is not excluded, the
        current URL is saved to the session. If the request method is not GET,
        the URL is not saved.

        This function returns the saved URL if it exists, or the default URL if
        it does not.

        If `use_referrer` is True, and the request has a referrer, the referrer
        is returned instead of the saved URL.

        :param default: The default URL to return if no URL is saved.
        :return: The URL to go back to
        """
        if "back_url" in session:
            return session["back_url"]
        if self._use_referrer and request.referrer:
            return request.referrer
        return default or self._default_url

    def clear(self):
        """
        Clear the saved back URL from the session.

        This removes the "back_url" key from the session if it exists,
        effectively clearing the saved URL. This can be used when you want
        to reset the back navigation state.
        """
        session.pop("back_url", None)

    def exclude(self, func):
        """
        Decorator to mark a view function as excluded from saving the current URL.

        This marks the given view function as excluded from saving the current URL.
        If the request method is GET and the endpoint is not excluded, the current
        URL is saved to the session. If the request method is not GET, the URL is
        not saved.

        This can be used to mark a view function as not needing to save the current
        URL, for example if the view function is a redirect or an AJAX endpoint.

        If no function is given, this returns the decorator itself, which can
        be used as a decorator.

        :param func: The view function to mark as excluded
        :return: The decorated view function, or the decorator itself if no
                 function is given.
        """
        self._excluded_endpoints.add(func.__name__)
        return func

    def _inject_back_url(self):
        """
        Inject the back URL into the template context.

        This injects the back URL into the template context as `back_url`.
        This is called automatically by the app before each request.

        :return: A dictionary containing the back URL
        """
        return dict(back_url=self.get_url())
