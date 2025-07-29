# Django JQGrid API Reference

## Overview

This document provides comprehensive API reference for Django JQGrid package. The API is built on Django REST Framework and provides endpoints for grid configuration, data operations, and import/export functionality.

## Base URL Pattern

All API endpoints follow the pattern:
```
/api/{app_name}/{model_name}/
```

Where:
- `app_name`: Django app label (e.g., 'myapp')
- `model_name`: Model name in lowercase (e.g., 'product')

## Core Endpoints

### 1. Grid Configuration

**Endpoint:** `GET /api/{app_name}/{model_name}/jqgrid_config/`

Returns complete jqGrid configuration including column model, grid options, and method options.

**Response Format:**
```json
{
    "jqgrid_options": {
        "url": "/api/myapp/product/",
        "editurl": "/api/myapp/product/crud/",
        "colModel": [...],
        "colNames": [...],
        "datatype": "json",
        "mtype": "GET",
        "height": 400,
        "autowidth": true,
        "multiselect": true,
        "rownumbers": true,
        "sortname": "id",
        "sortorder": "asc"
    },
    "method_options": {
        "navGrid": {...},
        "filterToolbar": {...}
    },
    "bulk_action_config": {
        "actions": [...],
        "updateableFields": [...]
    },
    "header_titles": {...},
    "import_config": {...},
    "export_config": {...}
}
```

### 2. Data Operations

**Endpoint:** `GET /api/{app_name}/{model_name}/`

Returns paginated grid data with jqGrid-compatible format.

**Query Parameters:**
- `page`: Page number
- `page_size`: Number of records per page
- `sidx`: Sort field
- `sord`: Sort order ('asc' or 'desc')
- `_search`: Enable search ('true' or 'false')
- `filters`: JSON string with search filters

**Response Format:**
```json
{
    "data": {
        "data": [...],
        "page": 1,
        "total_pages": 10,
        "records": 250
    }
}
```

### 3. CRUD Operations

**Endpoint:** `POST /api/{app_name}/{model_name}/crud/`

Handles Create, Read, Update, Delete operations via jqGrid form submissions.

**Request Parameters:**
- `oper`: Operation type ('add', 'edit', 'del')
- `id`: Record ID (for edit/delete operations)
- Additional fields based on operation

**Response Format:**
```json
{
    "success": true,
    "message": "Record created successfully",
    "id": 123
}
```

### 4. Bulk Operations

**Endpoint:** `POST /api/{app_name}/{model_name}/bulk_action/`

Handles bulk update and delete operations.

**Request Format:**
```json
{
    "ids": [1, 2, 3, 4],
    "action": {
        "field1": "new_value",
        "field2": "another_value"
    }
}
```

For deletion:
```json
{
    "ids": [1, 2, 3, 4],
    "action": {
        "_delete": true
    }
}
```

**Response Format:**
```json
{
    "status": "success",
    "message": "Updated 4 records",
    "updated_ids": [1, 2, 3, 4]
}
```

## Import/Export Endpoints

### 5. Data Import

**Endpoint:** `POST /api/{app_name}/{model_name}/import_data/`

Imports data from uploaded files (CSV, Excel).

**Request Format:** `multipart/form-data`
- `import_file`: File to upload
- `mapped_columns`: JSON string with column mappings
- `default_values`: JSON string with default values

**Response Format:**
```json
{
    "status": true,
    "message": "Data imported successfully",
    "task_id": "abc123",
    "imported_count": 150,
    "failed_count": 5
}
```

### 6. Data Export

**Endpoint:** `GET /api/{app_name}/{model_name}/export_data/`

Exports grid data in various formats.

**Query Parameters:**
- `ext`: Export format ('csv', 'xlsx', 'pdf', 'json')
- `columns`: Comma-separated column names or 'all'
- `background`: Process in background ('true' or 'false')
- `_search`: Include current search filters
- `filters`: JSON string with filters
- `sidx`: Sort field
- `sord`: Sort order

**Response:** File download or task ID for background processing

### 7. Sample File Download

**Endpoint:** `GET /api/{app_name}/{model_name}/sample_import/`

Downloads a sample import file template.

**Response:** CSV file with proper headers

### 8. Dropdown Data

**Endpoint:** `GET /api/{app_name}/{model_name}/dropdown/`

Returns dropdown options for select fields.

**Query Parameters:**
- `field_name`: Field name for the dropdown

**Response Format:**
```json
{
    ":": "All",
    "1": "Option 1",
    "2": "Option 2"
}
```

### 9. Task Status

**Endpoint:** `GET /api/{app_name}/task/{task_id}/`

Returns status of background tasks (import/export).

**Response Format:**
```json
{
    "data": {
        "task_status": "COMPLETED",
        "completed_count": 150,
        "total_count": 150,
        "completed_percentage": 100,
        "file_url": "/media/exports/data.xlsx"
    }
}
```

## ViewSet Classes

### JqGridModelViewSet

Base viewset that provides all jqGrid functionality.

**Key Methods:**
- `get_model()`: Returns model class from URL parameters
- `get_queryset()`: Returns optimized queryset
- `get_serializer_class()`: Returns dynamic or custom serializer
- `apply_jqgrid_filters()`: Applies search filters from jqGrid

**Usage:**
```python
from django_jqgrid.api_views import JqGridModelViewSet

class CustomGridViewSet(JqGridModelViewSet):
    # Optional customizations
    visible_columns = ['field1', 'field2', 'field3']
    search_fields = ['field1', 'field2']
    ordering_fields = ['field1', 'field3']
    
    import_config = {
        'allowed_formats': ['csv', 'xlsx'],
        'sample_file': '/path/to/sample.csv'
    }
    
    export_config = {
        'allowed_formats': ['csv', 'xlsx', 'pdf']
    }
```

## Mixins

### JqGridConfigMixin

Provides grid configuration functionality.

**Key Attributes:**
- `visible_columns`: List of columns to show in grid
- `search_fields`: List of searchable fields
- `ordering_fields`: List of sortable fields
- `groupable_fields`: List of fields that can be grouped
- `frozen_columns`: List of columns to freeze
- `conditional_formatting`: Dict of formatting rules
- `bulk_updateable_fields`: List of fields for bulk updates

**Key Methods:**
- `initgrid()`: Initialize grid configuration
- `get_tmplgilters()`: Get saved filter templates
- `jqgrid_config()`: Return configuration as API response

### JqGridBulkActionMixin

Provides bulk action functionality.

**Key Methods:**
- `get_bulk_queryset(ids)`: Filter queryset by IDs
- `get_bulk_editable_fields()`: Get allowed bulk edit fields
- `validate_bulk_data(data)`: Validate bulk action request
- `process_bulk_update(objs, updates)`: Process bulk updates
- `bulk_action()`: Handle bulk action requests

## JavaScript API

### Global Objects

**window.jqGridManager**: Main grid manager
- `initializeTable(config)`: Initialize a new grid
- `getTableInstance(id)`: Get existing grid instance
- `utils.notify(type, message, instance)`: Show notifications

**window.importExportUtils**: Import/export utilities
- `initializeImportExport(instance, data)`: Setup import/export
- `exportTableData(instance, format, background, columns)`: Export data
- `config.hooks`: Extensible hooks for custom functionality

### Event Handlers

**Grid Events:**
- `jqGrid:afterLoad`: Fired after grid loads
- `jqGrid:beforeSave`: Fired before save operation
- `jqGrid:afterSave`: Fired after successful save
- `jqGrid:beforeDelete`: Fired before delete operation

**Custom Events:**
- `grid:importComplete`: Fired after import completion
- `grid:exportStart`: Fired when export starts
- `grid:bulkActionComplete`: Fired after bulk action

### Customization Options

**Notification Handler:**
```javascript
window.jqGridConfig.notify = function(type, message, tableInstance) {
    // Custom notification implementation
    console.log(`[${type}] ${message}`);
};
```

**Custom Formatters:**
```javascript
window.jqGridConfig.formatters.custom = function(cellValue, options, rowObject) {
    return `<span class="custom">${cellValue}</span>`;
};
```

**Import/Export Hooks:**
```javascript
window.importExportUtils.config.hooks.beforeImport = function(tableInstance, file, extension) {
    console.log('About to import file:', file.name);
    return true; // Continue with import
};

window.importExportUtils.config.hooks.afterExport = function(tableInstance, format, background, response) {
    console.log('Export completed:', response);
};
```

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
    "status": "error",
    "message": "Invalid operation",
    "errors": {...}
}
```

**404 Not Found:**
```json
{
    "error": "Model myapp.product not found"
}
```

**500 Internal Server Error:**
```json
{
    "error": "An unexpected error occurred",
    "data": null
}
```

### JavaScript Error Handling

```javascript
// Check for configuration errors
$(document).on('grid:configError', function(e, error) {
    console.error('Grid configuration error:', error);
});

// Handle import/export errors
window.importExportUtils.config.notify = function(type, message, tableInstance) {
    if (type === 'error') {
        // Custom error handling
        showCustomErrorDialog(message);
    }
};
```

## Security Considerations

### Authentication

All endpoints respect Django's authentication system. Ensure proper authentication is configured:

```python
# In your ViewSet
class SecureGridViewSet(JqGridModelViewSet):
    permission_classes = [IsAuthenticated]
```

### Field-Level Permissions

Control field visibility and editability based on user permissions:

```python
def get_column_config(self):
    config = super().get_column_config()
    user = self.request.user
    
    if not user.has_perm('myapp.view_sensitive_field'):
        config['sensitive_field']['hidden'] = True
    
    return config
```

### CSRF Protection

All POST requests include CSRF protection automatically. For custom AJAX requests:

```javascript
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
```

## Performance Optimization

### Query Optimization

```python
class OptimizedGridViewSet(JqGridModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('foreign_key_field')\
                      .prefetch_related('many_to_many_field')\
                      .only('field1', 'field2', 'field3')
```

### Caching

```python
from django.core.cache import cache

class CachedGridViewSet(JqGridModelViewSet):
    cache_timeout = 300
    
    def list(self, request, *args, **kwargs):
        cache_key = f"grid_data_{self.get_model().__name__}_{request.GET.urlencode()}"
        response = cache.get(cache_key)
        
        if response is None:
            response = super().list(request, *args, **kwargs)
            cache.set(cache_key, response.data, self.cache_timeout)
        
        return response
```

## Troubleshooting

### Debug Mode

Enable debug mode for detailed logging:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django_jqgrid': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Common Issues

1. **Grid not loading**: Check browser console for JavaScript errors
2. **Import/Export not working**: Verify FontAwesome is loaded and import/export configs are set
3. **Permissions issues**: Ensure proper Django permissions are configured
4. **Performance issues**: Use query optimization and caching strategies

For more troubleshooting tips, see the main README.md file.