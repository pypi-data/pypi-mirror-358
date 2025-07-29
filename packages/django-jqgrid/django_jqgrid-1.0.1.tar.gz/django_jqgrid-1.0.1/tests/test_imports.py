"""Test basic imports and package structure."""

def test_package_import():
    """Test that the package can be imported."""
    import django_jqgrid
    assert hasattr(django_jqgrid, '__version__')


def test_version_format():
    """Test that version follows semantic versioning."""
    import django_jqgrid
    version_parts = django_jqgrid.__version__.split('.')
    assert len(version_parts) >= 2
    # Test that major and minor versions are numbers
    assert version_parts[0].isdigit()
    assert version_parts[1].isdigit()


def test_apps_config():
    """Test that Django app config can be imported."""
    from django_jqgrid.apps import DjangoJqgridConfig
    assert DjangoJqgridConfig.name == 'django_jqgrid'
    assert DjangoJqgridConfig.verbose_name == 'Django jqGrid'