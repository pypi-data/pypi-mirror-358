"""Django settings storage for PyConfBox."""

from typing import Any, Dict, List, Optional

from django.conf import settings

try:
    from pyconfbox.core.types import ConfigValue
    from pyconfbox.storage.base import BaseStorage
except ImportError:
    raise ImportError("pyconfbox is required for pyconfbox-django plugin")


class DjangoStorage(BaseStorage):
    """Storage backend that integrates with Django settings.

    This storage allows PyConfBox to read from and write to Django settings,
    providing seamless integration between PyConfBox and Django configuration.
    """

    def __init__(self, prefix: str = "PYCONFBOX_") -> None:
        """Initialize Django storage.

        Args:
            prefix: Prefix for PyConfBox settings in Django settings.
        """
        super().__init__()
        self.prefix = prefix
        self._ensure_settings_dict()

    def _ensure_settings_dict(self) -> None:
        """Ensure that Django settings has a dictionary for PyConfBox settings."""
        if not hasattr(settings, '_pyconfbox_data'):
            settings._pyconfbox_data = {}

    def _get_setting_name(self, key: str) -> str:
        """Get the Django setting name for a PyConfBox key.

        Args:
            key: PyConfBox configuration key.

        Returns:
            Django setting name.
        """
        return f"{self.prefix}{key.upper()}"

    def get(self, key: str) -> Optional[ConfigValue]:
        """Get a configuration value from Django settings.

        Args:
            key: Configuration key.

        Returns:
            Configuration value if found, None otherwise.
        """
        # First try direct Django setting
        setting_name = self._get_setting_name(key)
        if hasattr(settings, setting_name):
            value = getattr(settings, setting_name)
            return ConfigValue(
                key=key,
                value=value,
                data_type=type(value),
                scope='django',
                storage='django'
            )

        # Then try PyConfBox data
        if hasattr(settings, '_pyconfbox_data'):
            pyconfbox_data = getattr(settings, '_pyconfbox_data')
            if key in pyconfbox_data:
                stored_value = pyconfbox_data[key]
                return ConfigValue(**stored_value)

        return None

    def set(self, key: str, config_value: ConfigValue) -> None:
        """Set a configuration value in Django settings.

        Args:
            key: Configuration key.
            config_value: Configuration value to set.
        """
        self._ensure_settings_dict()

        # Store in PyConfBox data
        pyconfbox_data = getattr(settings, '_pyconfbox_data')
        pyconfbox_data[key] = config_value.model_dump()

        # Also set as Django setting for direct access
        setting_name = self._get_setting_name(key)
        setattr(settings, setting_name, config_value.value)

    def delete(self, key: str) -> bool:
        """Delete a configuration value from Django settings.

        Args:
            key: Configuration key.

        Returns:
            True if deleted, False if not found.
        """
        deleted = False

        # Remove from PyConfBox data
        if hasattr(settings, '_pyconfbox_data'):
            pyconfbox_data = getattr(settings, '_pyconfbox_data')
            if key in pyconfbox_data:
                del pyconfbox_data[key]
                deleted = True

        # Remove Django setting
        setting_name = self._get_setting_name(key)
        if hasattr(settings, setting_name):
            delattr(settings, setting_name)
            deleted = True

        return deleted

    def exists(self, key: str) -> bool:
        """Check if a configuration key exists in Django settings.

        Args:
            key: Configuration key.

        Returns:
            True if exists, False otherwise.
        """
        # Check Django setting
        setting_name = self._get_setting_name(key)
        if hasattr(settings, setting_name):
            return True

        # Check PyConfBox data
        if hasattr(settings, '_pyconfbox_data'):
            pyconfbox_data = getattr(settings, '_pyconfbox_data')
            return key in pyconfbox_data

        return False

    def keys(self) -> List[str]:
        """Get all configuration keys from Django settings.

        Returns:
            List of configuration keys.
        """
        keys = []

        # Get keys from PyConfBox data
        if hasattr(settings, '_pyconfbox_data'):
            pyconfbox_data = getattr(settings, '_pyconfbox_data')
            keys.extend(pyconfbox_data.keys())

        # Get keys from Django settings with prefix
        for attr_name in dir(settings):
            if attr_name.startswith(self.prefix):
                key = attr_name[len(self.prefix):].lower()
                if key not in keys:
                    keys.append(key)

        return keys

    def clear(self) -> None:
        """Clear all PyConfBox configuration from Django settings."""
        # Clear PyConfBox data
        if hasattr(settings, '_pyconfbox_data'):
            getattr(settings, '_pyconfbox_data').clear()

        # Clear Django settings with prefix
        for attr_name in list(dir(settings)):
            if attr_name.startswith(self.prefix):
                delattr(settings, attr_name)

    def update(self, config_values: Dict[str, ConfigValue]) -> None:
        """Update multiple configuration values in Django settings.

        Args:
            config_values: Dictionary of configuration values.
        """
        for key, config_value in config_values.items():
            self.set(key, config_value)

    def get_info(self) -> Dict[str, Any]:
        """Get information about the Django storage.

        Returns:
            Storage information dictionary.
        """
        return {
            'type': 'django',
            'prefix': self.prefix,
            'django_version': getattr(settings, 'DJANGO_VERSION', 'unknown'),
            'settings_module': getattr(settings, 'SETTINGS_MODULE', 'unknown'),
            'total_keys': len(self.keys())
        }
