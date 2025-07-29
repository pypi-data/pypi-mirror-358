# PyConfBox Django Plugin

**Django integration plugin for PyConfBox configuration management**

This plugin enables seamless integration of PyConfBox with Django applications, providing automatic synchronization with Django settings and middleware support.

> **한국어 문서**: [README_ko.md](README_ko.md) | **English Documentation**: README.md (current)

## 🚀 Installation

```bash
pip install pyconfbox-django
```

## 📋 Requirements

- Python 3.8+
- Django 3.2+
- pyconfbox >= 0.1.0

## 🔧 Configuration

### Add Middleware to Django Settings

```python
# settings.py
MIDDLEWARE = [
    'pyconfbox_django.middleware.PyConfBoxMiddleware',
    # ... other middleware
]

# PyConfBox configuration
PYCONFBOX = {
    'default_storage': 'environment',
    'fallback_storage': 'memory',
    'env_prefix': 'DJANGO_',
}
```

## 💡 Usage

### Django Storage Backend

```python
from pyconfbox_django import DjangoStorage
from pyconfbox import Config

# Integrate with Django settings
django_storage = DjangoStorage()
config = Config(default_storage=django_storage)

# Automatically reflects to Django settings
config.set('DEBUG', True, scope='django')
config.set('SECRET_KEY', 'your-secret-key', scope='django')
config.set('ALLOWED_HOSTS', ['localhost', '127.0.0.1'], scope='django')
```

### Accessing Django Settings

```python
from pyconfbox_django import get_django_config

# Get Django-specific configuration
django_config = get_django_config()

# Access Django settings through PyConfBox
debug_mode = django_config.get('DEBUG')
secret_key = django_config.get('SECRET_KEY')
```

### Middleware Features

The PyConfBox middleware provides:

- **Automatic configuration loading** on request start
- **Configuration context** available in views
- **Environment variable synchronization**
- **Settings validation** and type conversion

### Advanced Configuration

```python
# settings.py
PYCONFBOX = {
    'default_storage': 'environment',
    'fallback_storage': 'memory',
    'env_prefix': 'DJANGO_',
    'auto_sync': True,  # Automatically sync with Django settings
    'validate_settings': True,  # Validate Django settings
    'cache_timeout': 300,  # Cache timeout in seconds
}
```

## 🎯 Features

- **🔄 Auto-sync**: Automatic synchronization with Django settings
- **🔧 Middleware**: Request-level configuration management
- **🎯 Scope Support**: Django-specific configuration scope
- **🔒 Type Safety**: Automatic type validation and conversion
- **⚡ Performance**: Efficient caching and lazy loading

## 📖 Documentation

- **[Main PyConfBox Documentation](../../docs/README.md)**
- **[Django Integration Guide](../../docs/en/django-integration.md)**
- **[API Reference](../../docs/en/api-reference.md)**
- **[한국어 문서](../../docs/ko/README.md)**

## 🔗 Related Packages

- **[pyconfbox](../pyconfbox/)** - Main PyConfBox package
- **[pyconfbox-mysql](../pyconfbox-mysql/)** - MySQL storage backend
- **[pyconfbox-postgresql](../pyconfbox-postgresql/)** - PostgreSQL storage backend
- **[pyconfbox-mongodb](../pyconfbox-mongodb/)** - MongoDB storage backend

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](../../.github/CONTRIBUTING.md) for details.

## 📄 License

MIT License - See the [LICENSE](LICENSE) file for details.

---

**Enhance your Django applications with PyConfBox!** 🚀 