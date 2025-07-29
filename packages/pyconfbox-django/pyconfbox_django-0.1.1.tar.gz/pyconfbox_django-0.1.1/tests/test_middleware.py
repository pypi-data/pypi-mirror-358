"""Tests for Django middleware."""

from typing import TYPE_CHECKING
import pytest
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from unittest.mock import Mock, patch

# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        USE_TZ=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        MIDDLEWARE=[
            'pyconfbox_django.middleware.PyConfBoxMiddleware',
        ],
    )

from pyconfbox_django.middleware import PyConfBoxMiddleware

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from pytest_mock.plugin import MockerFixture


class TestPyConfBoxMiddleware:
    """Test cases for PyConfBoxMiddleware."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.get_response = Mock(return_value=HttpResponse("OK"))

    @patch('pyconfbox_django.middleware.Config')
    def test_middleware_initialization(self, mock_config: Mock) -> None:
        """Test middleware initialization."""
        mock_config.return_value = Mock()
        
        middleware = PyConfBoxMiddleware(self.get_response)
        
        assert middleware.get_response == self.get_response
        assert middleware.config is not None
        mock_config.assert_called_once()

    @patch('pyconfbox_django.middleware.Config')
    def test_config_initialization_with_default_settings(self, mock_config: Mock) -> None:
        """Test config initialization with default settings."""
        mock_config.return_value = Mock()
        
        # Test without PYCONFBOX setting
        if hasattr(settings, 'PYCONFBOX'):
            delattr(settings, 'PYCONFBOX')
        
        middleware = PyConfBoxMiddleware(self.get_response)
        
        # Should use default values
        call_kwargs = mock_config.call_args[1]
        assert 'default_storage' in call_kwargs
        assert 'fallback_storage' in call_kwargs

    @patch('pyconfbox_django.middleware.Config')
    def test_config_initialization_with_custom_settings(self, mock_config: Mock) -> None:
        """Test config initialization with custom settings."""
        mock_config.return_value = Mock()
        
        custom_settings = {
            'default_storage': 'redis',
            'fallback_storage': 'file',
            'env_prefix': 'MYAPP_'
        }
        
        settings.PYCONFBOX = custom_settings
        
        try:
            middleware = PyConfBoxMiddleware(self.get_response)
            
            call_kwargs = mock_config.call_args[1]
            assert call_kwargs.get('default_storage') == 'redis'
            assert call_kwargs.get('fallback_storage') == 'file'
            assert call_kwargs.get('env_prefix') == 'MYAPP_'
        finally:
            if hasattr(settings, 'PYCONFBOX'):
                delattr(settings, 'PYCONFBOX')

    @patch('pyconfbox_django.middleware.Config')
    def test_django_settings_sync(self, mock_config: Mock) -> None:
        """Test Django settings synchronization."""
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        middleware = PyConfBoxMiddleware(self.get_response)
        
        # Check that config.set was called for Django settings
        assert mock_config_instance.set.called

    @patch('pyconfbox_django.middleware.Config')
    def test_request_processing(self, mock_config: Mock) -> None:
        """Test request processing."""
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        middleware = PyConfBoxMiddleware(self.get_response)
        request = self.factory.get('/')
        
        response = middleware(request)
        
        # Check that config is attached to request
        assert hasattr(request, 'pyconfbox')
        assert request.pyconfbox == middleware.config
        
        # Check that get_response was called
        self.get_response.assert_called_once_with(request)
        assert response.content == b"OK"

    @patch('pyconfbox_django.middleware.Config')
    def test_middleware_call_chain(self, mock_config: Mock) -> None:
        """Test middleware call chain."""
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        def mock_get_response(request: HttpRequest) -> HttpResponse:
            # Verify config is available in request
            assert hasattr(request, 'pyconfbox')
            return HttpResponse("Success")
        
        middleware = PyConfBoxMiddleware(mock_get_response)
        request = self.factory.get('/')
        
        response = middleware(request)
        
        assert response.content == b"Success"

    @patch('pyconfbox_django.middleware.Config')
    def test_error_handling_in_initialization(self, mock_config: Mock) -> None:
        """Test error handling during initialization."""
        mock_config.side_effect = Exception("Config error")
        
        with pytest.raises(Exception, match="Config error"):
            PyConfBoxMiddleware(self.get_response)

    @patch('pyconfbox_django.middleware.Config')
    def test_middleware_with_different_request_methods(self, mock_config: Mock) -> None:
        """Test middleware with different HTTP methods."""
        mock_config_instance = Mock()
        mock_config.return_value = mock_config_instance
        
        middleware = PyConfBoxMiddleware(self.get_response)
        
        for method in ['GET', 'POST', 'PUT', 'DELETE']:
            request = getattr(self.factory, method.lower())('/')
            response = middleware(request)
            
            assert hasattr(request, 'pyconfbox')
            assert response.content == b"OK" 