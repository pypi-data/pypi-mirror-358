"""Tests for Django settings storage."""

from typing import TYPE_CHECKING, Any, Dict
import pytest
from django.conf import settings
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
    )

from pyconfbox.core.types import ConfigValue, ConfigScope
from pyconfbox_django.settings import DjangoStorage

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest
    from pytest_mock.plugin import MockerFixture


class TestDjangoStorage:
    """Test cases for DjangoStorage."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.storage = DjangoStorage()

    def test_initialization_default_prefix(self) -> None:
        """Test storage initialization with default prefix."""
        storage = DjangoStorage()
        assert storage.prefix == "PYCONFBOX_"

    def test_initialization_custom_prefix(self) -> None:
        """Test storage initialization with custom prefix."""
        storage = DjangoStorage("CUSTOM_")
        assert storage.prefix == "CUSTOM_"

    def test_get_setting_name(self) -> None:
        """Test setting name generation."""
        storage = DjangoStorage("TEST_")
        assert storage._get_setting_name("api_key") == "TEST_API_KEY"
        assert storage._get_setting_name("database_url") == "TEST_DATABASE_URL"

    def test_ensure_settings_dict(self) -> None:
        """Test settings dictionary initialization."""
        # Remove existing _pyconfbox_data if it exists
        if hasattr(settings, '_pyconfbox_data'):
            delattr(settings, '_pyconfbox_data')
        
        self.storage._ensure_settings_dict()
        
        assert hasattr(settings, '_pyconfbox_data')
        assert isinstance(getattr(settings, '_pyconfbox_data'), dict)

    def test_get_from_django_setting(self) -> None:
        """Test getting value from Django setting."""
        # Set a test setting directly
        settings.PYCONFBOX_TEST_KEY = 'test_value'
        
        try:
            result = self.storage.get('test_key')
            
            assert result is not None
            assert result.value == 'test_value'
            assert result.key == 'test_key'
            assert result.storage == 'django'
        finally:
            if hasattr(settings, 'PYCONFBOX_TEST_KEY'):
                delattr(settings, 'PYCONFBOX_TEST_KEY')

    def test_get_from_pyconfbox_data(self) -> None:
        """Test getting value from PyConfBox data."""
        test_data = {
            'test_key': {
                'key': 'test_key',
                'value': 'test_value',
                'data_type': str,  # Use actual type object
                'scope': ConfigScope.GLOBAL,
                'storage': 'django',
                'immutable': False,
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-01T00:00:00'
            }
        }
        
        settings._pyconfbox_data = test_data
        
        try:
            result = self.storage.get('test_key')
            
            assert result is not None
            assert result.value == 'test_value'
            assert result.key == 'test_key'
        finally:
            if hasattr(settings, '_pyconfbox_data'):
                delattr(settings, '_pyconfbox_data')

    def test_get_nonexistent_key(self) -> None:
        """Test getting nonexistent key."""
        result = self.storage.get('nonexistent_key')
        assert result is None

    def test_set_value(self) -> None:
        """Test setting a configuration value."""
        config_value = ConfigValue(
            key='test_key',
            value='test_value',
            data_type=str,  # Use actual type object
            scope=ConfigScope.GLOBAL,
            storage='django',
            immutable=False
        )
        
        # Ensure _pyconfbox_data exists
        settings._pyconfbox_data = {}
        
        try:
            self.storage.set('test_key', config_value)
            
            # Check PyConfBox data
            pyconfbox_data = getattr(settings, '_pyconfbox_data')
            assert 'test_key' in pyconfbox_data
            
            # Check Django setting
            setting_name = self.storage._get_setting_name('test_key')
            assert hasattr(settings, setting_name)
            assert getattr(settings, setting_name) == 'test_value'
        finally:
            if hasattr(settings, '_pyconfbox_data'):
                delattr(settings, '_pyconfbox_data')
            setting_name = self.storage._get_setting_name('test_key')
            if hasattr(settings, setting_name):
                delattr(settings, setting_name)

    def test_delete_existing_key(self) -> None:
        """Test deleting an existing key."""
        # Set up initial data
        test_data = {'test_key': {'key': 'test_key', 'value': 'test_value'}}
        setting_name = self.storage._get_setting_name('test_key')
        
        settings._pyconfbox_data = test_data
        setattr(settings, setting_name, 'test_value')
        
        try:
            result = self.storage.delete('test_key')
            
            assert result is True
            assert 'test_key' not in test_data
        finally:
            if hasattr(settings, '_pyconfbox_data'):
                delattr(settings, '_pyconfbox_data')
            if hasattr(settings, setting_name):
                delattr(settings, setting_name)

    def test_delete_nonexistent_key(self) -> None:
        """Test deleting a nonexistent key."""
        result = self.storage.delete('nonexistent_key')
        assert result is False

    def test_exists_with_django_setting(self) -> None:
        """Test key existence check with Django setting."""
        setting_name = self.storage._get_setting_name('test_key')
        setattr(settings, setting_name, 'test_value')
        
        try:
            assert self.storage.exists('test_key') is True
        finally:
            if hasattr(settings, setting_name):
                delattr(settings, setting_name)

    def test_exists_with_pyconfbox_data(self) -> None:
        """Test key existence check with PyConfBox data."""
        test_data = {'test_key': {'key': 'test_key', 'value': 'test_value'}}
        settings._pyconfbox_data = test_data
        
        try:
            assert self.storage.exists('test_key') is True
        finally:
            if hasattr(settings, '_pyconfbox_data'):
                delattr(settings, '_pyconfbox_data')

    def test_exists_nonexistent_key(self) -> None:
        """Test key existence check for nonexistent key."""
        assert self.storage.exists('nonexistent_key') is False

    def test_keys_from_pyconfbox_data(self) -> None:
        """Test getting keys from PyConfBox data."""
        test_data = {
            'key1': {'key': 'key1', 'value': 'value1'},
            'key2': {'key': 'key2', 'value': 'value2'}
        }
        
        settings._pyconfbox_data = test_data
        
        try:
            keys = self.storage.keys()
            
            assert 'key1' in keys
            assert 'key2' in keys
        finally:
            if hasattr(settings, '_pyconfbox_data'):
                delattr(settings, '_pyconfbox_data')

    def test_keys_from_django_settings(self) -> None:
        """Test getting keys from Django settings with prefix."""
        settings.PYCONFBOX_KEY1 = 'value1'
        settings.PYCONFBOX_KEY2 = 'value2'
        
        try:
            keys = self.storage.keys()
            
            assert 'key1' in keys
            assert 'key2' in keys
        finally:
            if hasattr(settings, 'PYCONFBOX_KEY1'):
                delattr(settings, 'PYCONFBOX_KEY1')
            if hasattr(settings, 'PYCONFBOX_KEY2'):
                delattr(settings, 'PYCONFBOX_KEY2')

    def test_clear(self) -> None:
        """Test clearing all configuration data."""
        test_data = {'key1': 'value1', 'key2': 'value2'}
        settings._pyconfbox_data = test_data
        settings.PYCONFBOX_KEY1 = 'value1'
        
        try:
            self.storage.clear()
            
            assert len(test_data) == 0
        finally:
            if hasattr(settings, '_pyconfbox_data'):
                delattr(settings, '_pyconfbox_data')
            if hasattr(settings, 'PYCONFBOX_KEY1'):
                delattr(settings, 'PYCONFBOX_KEY1')

    def test_update(self) -> None:
        """Test updating multiple configuration values."""
        config_values = {
            'key1': ConfigValue(
                key='key1',
                value='value1',
                data_type=str,  # Use actual type object
                scope=ConfigScope.GLOBAL,
                storage='django',
                immutable=False
            ),
            'key2': ConfigValue(
                key='key2',
                value='value2',
                data_type=str,  # Use actual type object
                scope=ConfigScope.GLOBAL,
                storage='django',
                immutable=False
            )
        }
        
        with patch.object(self.storage, 'set') as mock_set:
            self.storage.update(config_values)
            
            assert mock_set.call_count == 2

    def test_get_info(self) -> None:
        """Test getting storage information."""
        with patch.object(self.storage, 'keys', return_value=['key1', 'key2']):
            info = self.storage.get_info()
            
            assert info['type'] == 'django'
            assert info['prefix'] == 'PYCONFBOX_'
            assert info['total_keys'] == 2
            assert 'settings_module' in info 