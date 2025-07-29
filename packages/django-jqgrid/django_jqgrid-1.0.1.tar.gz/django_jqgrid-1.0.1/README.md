# Django jqGrid

A powerful Django app that seamlessly integrates jqGrid with Django REST Framework, providing advanced data grid functionality for your Django applications.

## Features

- **Seamless Integration**: Easy integration with Django REST Framework
- **Advanced Grid Features**: Full jqGrid functionality including sorting, filtering, pagination, and CRUD operations
- **Import/Export Ready**: Extensible framework for adding import/export capabilities
- **Multi-Database Support**: Works with multiple database configurations
- **Security**: Built-in security features and permission handling
- **Customizable**: Highly customizable grid configurations and styling
- **Responsive Design**: Mobile-friendly responsive grid layouts
- **Internationalization**: Support for multiple languages

## Quick Start

### Installation

```bash
pip install django-jqgrid
```

### Django Settings

Add `django_jqgrid` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... your other apps
    'rest_framework',  # Required dependency
    'django_jqgrid',
    'example',  # Optional: include example app for demonstrations
]

# Optional: Django jqGrid configuration
JQGRID_CONFIG = {
    'DEFAULT_ROWS_PER_PAGE': 25,
    'ENABLE_EXCEL_EXPORT': True,
    'ENABLE_CSV_EXPORT': True,
    'ENABLE_FILTERING': True,
    'ENABLE_CRUD_OPERATIONS': True,
}
```

### URL Configuration

```python
from django.urls import path, include

urlpatterns = [
    # ... your other URL patterns
    path('api/', include('django_jqgrid.urls')),
]
```

### Basic Usage

```python
from django_jqgrid.views import JqGridView
from django_jqgrid.serializers import JqGridSerializer
from .models import YourModel

class YourModelGrid(JqGridView):
    model = YourModel
    serializer_class = JqGridSerializer
    
    jqgrid_config = {
        'caption': 'Your Model Grid',
        'autowidth': True,
        'height': 400,
        'columns': [
            {'name': 'id', 'index': 'id', 'width': 50, 'sortable': True},
            {'name': 'name', 'index': 'name', 'width': 200, 'sortable': True},
            {'name': 'email', 'index': 'email', 'width': 200, 'sortable': True},
        ]
    }
```

## Example Project

The package includes a complete Django project demonstrating all jqGrid features:

- **Product Management**: Complex grid with multiple field types, filtering, and custom formatters
- **Customer Management**: User data handling with search and relationship display
- **Order Tracking**: Financial data, status workflows, and date handling
- **Category Management**: Simple CRUD operations and relationships

### Running the Example Project

```bash
# Navigate to example project
cd example_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ..  # Install django-jqgrid from parent directory

# Setup the project
python setup_example.py

# OR manually:
python manage.py migrate
python manage.py load_sample_data
python manage.py runserver
```

Visit: `http://localhost:8000/`

The example project serves as both documentation and a complete reference implementation.

## Documentation

- [Installation Guide](INSTALLATION_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Features Overview](FEATURES.md)
- [Configuration Options](CONFIGURATIONS.md)
- [Security Guide](SECURITY_GUIDE.md)
- [Contributing](CONTRIBUTING.md)

## Requirements

- Python 3.8+
- Django 3.2+
- Django REST Framework 3.12+

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- GitHub Issues: [Report Issues](https://github.com/yourusername/django-jqgrid/issues)
- Documentation: [Read the Docs](https://django-jqgrid.readthedocs.io)
- Email: support@django-jqgrid.org

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a complete list of changes.