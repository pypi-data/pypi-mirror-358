# jqGrid JavaScript Architecture

This document explains the modular JavaScript architecture of django-jqgrid and how to extend it with custom functionality.

## File Structure

```
django_jqgrid/static/django_jqgrid/js/
├── core/                           # Core library files (minimal, reusable)
│   ├── jqgrid-core.js             # Table management, initialization, hooks
│   ├── jqgrid-config.js           # Configuration system and extension points
│   └── jqgrid-security.js         # Security features (CSRF, JWT, sessions)
├── plugins/                        # Optional plugin files
│   ├── jqgrid-formatters.js       # Common formatters (phone, email, etc.)
│   ├── jqgrid-bulk-actions.js     # Common bulk action patterns
│   └── jqgrid-row-renderers.js    # Common row rendering patterns
└── examples/                       # Example-specific customizations
    ├── demo-app-config.js          # Demo project customizations
    ├── crm-extensions.js           # CRM/Sales specific examples
    └── admin-extensions.js         # Admin panel examples

example/example_project/demo_app/static/demo_app/js/
└── demo-config.js                  # Demo app specific configuration
```

## Core vs Plugin vs Example Architecture

### Core Files (Always Loaded)

These files provide the essential jqGrid functionality and should remain lightweight:

- **jqgrid-core.js**: Multi-table management, grid initialization, toolbar creation, hooks
- **jqgrid-config.js**: Configuration system with extension points
- **jqgrid-security.js**: Authentication and security features

### Plugin Files (Optional)

These files provide commonly-used features that can be optionally loaded:

- **jqgrid-formatters.js**: Phone links, email links, image display, file downloads, etc.
- **jqgrid-bulk-actions.js**: Common bulk operations like export, email, etc.
- **jqgrid-row-renderers.js**: Different row layout patterns

### Example Files (Application-Specific)

These files show how to extend the library for specific use cases:

- **demo-config.js**: Demonstrates custom formatters, buttons, and bulk actions
- **crm-extensions.js**: CRM/Sales specific functionality examples
- **admin-extensions.js**: Django admin integration examples

## Usage in Templates

### Basic Usage (Core Only)

```html
<!-- Load core jqGrid functionality -->
{% jqgrid_js %}

<!-- Your grid -->
{% jqgrid "my_grid" "myapp" "mymodel" %}
```

### With Plugins

```html
<!-- Load core -->
{% jqgrid_js %}

<!-- Load optional plugins -->
{% jqgrid_plugins "formatters" "bulk-actions" %}

<!-- Your grid -->
{% jqgrid "my_grid" "myapp" "mymodel" %}
```

### With Custom Configuration

```html
<!-- Load core and plugins -->
{% jqgrid_js %}
{% jqgrid_plugins "formatters" %}

<!-- Load your custom configuration -->
<script src="{% static 'myapp/js/my-grid-config.js' %}"></script>

<!-- Your grid -->
{% jqgrid "my_grid" "myapp" "mymodel" %}
```

## Extending the Library

### Creating Custom Formatters

```javascript
// In your app's static JS file
$(document).ready(function() {
    // Extend with custom formatters
    window.JqGridConfig.extendFormatters({
        myCustomFormatter: function(cellval, opts, rowdata) {
            return `<span class="custom">${cellval}</span>`;
        }
    });
});
```

### Using Action Button Formatters

The formatters plugin provides configurable action buttons for ID columns:

#### Legacy open_button (Backward Compatibility)
```javascript
// Configure the default open button action
window.jqGridConfig.openButtonAction = function(id, rowData) {
    // Your custom action - open modal, navigate, etc.
    window.location.href = `/detail/${id}/`;
};
```

#### Configurable Action Buttons
```javascript
// Configure multiple action types
window.jqGridConfig.actionHandlers = {
    view: function(id, rowData) {
        // Open detail view
        $('#detail-modal').modal('show').find('.modal-body').load(`/api/detail/${id}/`);
    },
    
    edit: function(id, rowData) {
        // Open edit form
        window.location.href = `/edit/${id}/`;
    },
    
    delete: function(id, rowData) {
        if (confirm('Delete this record?')) {
            // Make DELETE API call
            fetch(`/api/delete/${id}/`, { method: 'DELETE' })
                .then(() => location.reload());
        }
    }
};
```

#### Using in Column Configuration
```python
# In your Django model configuration
class MyModelMixin:
    def get_column_config(self):
        config = super().get_column_config()
        
        # Use legacy open_button
        config['id']['formatter'] = 'open_button'
        
        # Or use configurable action button
        config['id']['formatter'] = 'actionButton'
        config['id']['formatoptions'] = {
            'buttonText': 'Edit',
            'buttonClass': 'btn btn-sm btn-warning',
            'buttonIcon': 'fas fa-edit',
            'actionType': 'edit'
        }
        
        # Contact field formatters with responsive options
        config['phone']['formatter'] = 'mobile'
        config['phone']['formatoptions'] = {
            'compact': True  # Use icon-only mode for narrow columns
        }
        
        config['email']['formatter'] = 'email'
        config['email']['formatoptions'] = {
            'compact': False  # Use full text with icon
        }
        
        # Or use icon-only formatters for very compact display
        config['phone']['formatter'] = 'phoneIcon'  # Just phone icon button
        config['email']['formatter'] = 'emailIcon'  # Just email icon button
        
        return config
```

### Responsive Formatter Options

The formatters plugin now includes responsive options to handle different screen sizes:

#### Contact Formatters
```javascript
// Full mode (default) - shows icon + text
config['phone']['formatter'] = 'mobile'
config['phone']['formatoptions'] = { compact: false }

// Compact mode - shows icon with text on hover
config['phone']['formatter'] = 'mobile'  
config['phone']['formatoptions'] = { compact: true }

// Icon-only mode - minimal space usage
config['phone']['formatter'] = 'phoneIcon'
```

#### CSS Classes for Column Optimization
```css
/* Suggested column CSS classes */
.phone-column { width: 120px; min-width: 100px; }
.email-column { width: 180px; min-width: 150px; }
.action-column { width: 80px; min-width: 60px; text-align: center; }
.status-column { width: 100px; min-width: 80px; }
```

### Creating Custom Buttons

```javascript
// Add custom buttons for specific models
window.JqGridConfig.customButtons = {
    mymodel: [
        {
            id: 'my-action',
            label: 'My Action',
            icon: 'fas fa-star',
            class: 'btn-warning',
            action: function(tableInstance) {
                // Your custom action
                alert('Custom action executed!');
            }
        }
    ]
};
```

### Creating Custom Bulk Actions

```javascript
// Add custom bulk actions
window.JqGridConfig.bulkActions = {
    mymodel: [
        {
            id: 'bulk-process',
            label: 'Process Selected',
            icon: 'fas fa-cogs',
            class: 'btn-info',
            action: function(selectedIds, tableInstance) {
                console.log('Processing:', selectedIds);
                // Make API call to process selected items
            }
        }
    ]
};
```

## Plugin Development

### Creating a New Plugin

1. Create a new file in `django_jqgrid/static/django_jqgrid/js/plugins/`
2. Wrap your code in an IIFE (Immediately Invoked Function Expression)
3. Check for dependencies and register your extensions

```javascript
/**
 * My Custom Plugin
 */
(function() {
    'use strict';
    
    // Check dependencies
    if (typeof window.JqGridConfig === 'undefined') {
        console.error('My Plugin: JqGridConfig not found');
        return;
    }
    
    // Your plugin functionality
    const myExtensions = {
        // Your formatters, actions, etc.
    };
    
    // Register with the system
    window.JqGridConfig.extendFormatters(myExtensions);
    
    console.log('My Plugin loaded successfully');
})();
```

### Register Plugin in Template Tags

Add your plugin to the available plugins in `jqgrid_tags.py`:

```python
available_plugins = {
    'formatters': 'django_jqgrid/js/plugins/jqgrid-formatters.js',
    'bulk-actions': 'django_jqgrid/js/plugins/jqgrid-bulk-actions.js',
    'my-plugin': 'django_jqgrid/js/plugins/my-plugin.js',  # Add this
}
```

Then use it in templates:
```html
{% jqgrid_plugins "formatters" "my-plugin" %}
```

## Best Practices

### 1. Keep Core Clean
- Don't add business-specific logic to core files
- Keep formatters and actions configurable
- Use the extension system instead of modifying core

### 2. Use Plugins for Common Patterns
- Create reusable formatters and actions as plugins
- Document plugin dependencies
- Make plugins optional and self-contained

### 3. Use Examples for Inspiration
- Study the example files to understand extension patterns
- Copy and modify examples for your use case
- Keep example code well-documented

### 4. Namespace Your Extensions
- Use descriptive names for custom formatters/actions
- Avoid conflicts with existing functionality
- Prefix custom functionality with your app name if needed

### 5. Handle Dependencies
- Always check if required objects exist before using them
- Gracefully degrade if dependencies are missing
- Use console.error for missing dependencies

## Migration from Monolithic Structure

If you have existing code that depends on the old structure:

1. **Move custom formatters** from core files to your app's static JS
2. **Replace hardcoded references** with configurable extensions
3. **Use the plugin system** for commonly reused functionality
4. **Update templates** to load the modular files

This new architecture provides better separation of concerns, improved maintainability, and easier customization while maintaining backward compatibility through the configuration system.