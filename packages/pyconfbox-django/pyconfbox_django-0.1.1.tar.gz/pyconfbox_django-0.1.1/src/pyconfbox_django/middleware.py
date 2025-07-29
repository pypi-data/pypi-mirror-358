"""Django middleware for PyConfBox integration."""

from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse

try:
    from pyconfbox import Config
except ImportError:
    raise ImportError("pyconfbox is required for pyconfbox-django plugin")


class PyConfBoxMiddleware:
    """Django middleware to integrate PyConfBox with Django settings.

    This middleware initializes PyConfBox configuration and makes it available
    throughout the Django application lifecycle.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize the middleware.

        Args:
            get_response: The next middleware or view in the chain.
        """
        self.get_response = get_response
        self.config = self._initialize_config()

    def _initialize_config(self) -> Config:
        """Initialize PyConfBox configuration from Django settings.

        Returns:
            Configured PyConfBox Config instance.
        """
        pyconfbox_settings = getattr(settings, 'PYCONFBOX', {})

        default_storage = pyconfbox_settings.get('default_storage', 'environment')
        fallback_storage = pyconfbox_settings.get('fallback_storage', 'memory')
        env_prefix = pyconfbox_settings.get('env_prefix', '')

        config = Config(
            default_storage=default_storage,
            fallback_storage=fallback_storage,
            env_prefix=env_prefix
        )

        # Sync Django settings to PyConfBox
        self._sync_django_settings(config)

        return config

    def _sync_django_settings(self, config: Config) -> None:
        """Sync important Django settings to PyConfBox.

        Args:
            config: PyConfBox Config instance.
        """
        # Sync common Django settings
        django_settings = [
            'DEBUG', 'SECRET_KEY', 'ALLOWED_HOSTS', 'DATABASE_URL',
            'STATIC_URL', 'MEDIA_URL', 'TIME_ZONE', 'LANGUAGE_CODE'
        ]

        for setting_name in django_settings:
            if hasattr(settings, setting_name):
                value = getattr(settings, setting_name)
                config.set(setting_name, value, scope='django')

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request.

        Args:
            request: Django HTTP request.

        Returns:
            Django HTTP response.
        """
        # Make config available in request
        request.pyconfbox = self.config

        response = self.get_response(request)
        return response
