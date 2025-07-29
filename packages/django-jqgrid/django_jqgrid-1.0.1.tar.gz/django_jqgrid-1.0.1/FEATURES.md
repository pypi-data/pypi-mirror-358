# Django JQGrid Features Guide

## Overview

Django JQGrid is a comprehensive package that provides powerful data grid functionality with minimal setup. This guide covers all features and capabilities in detail.

## Table of Contents

- [Auto-Configuration](#auto-configuration)
- [CRUD Operations](#crud-operations)
- [Advanced Filtering](#advanced-filtering)
- [Bulk Operations](#bulk-operations)
- [Multi-Database Support](#multi-database-support)
- [Responsive Design](#responsive-design)
- [Security Features](#security-features)
- [Performance Optimization](#performance-optimization)
- [Customization Options](#customization-options)

## Auto-Configuration

### Model Discovery

The package automatically discovers Django models and creates appropriate grid configurations:

```python
# Automatic discovery based on model fields
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

# Automatically generates:
# - Column configuration with appropriate editors
# - Search functionality for all fields
# - Proper formatters (currency, date, boolean, etc.)
# - Foreign key dropdowns
# - Validation rules
```

### Field Type Detection

Automatically configures columns based on Django field types:

| Django Field Type | Grid Configuration |
|------------------|-------------------|
| CharField/TextField | Text input with search |
| IntegerField | Numeric input with number formatting |
| DecimalField | Decimal input with currency formatting |
| BooleanField | Checkbox with true/false display |
| DateField | Date picker with date formatting |
| DateTimeField | DateTime picker with timestamp formatting |
| ForeignKey | Select dropdown with related data |
| EmailField | Email input with validation |
| URLField | URL input with link formatting |
| ImageField | Image display with upload capability |
| FileField | File display with download links |

### Intelligent Defaults

```python
# Automatic configuration includes:
{
    "datatype": "json",
    "responsive": True,
    "multiselect": True,
    "rownumbers": True,
    "sortable": True,
    "searchable": True,
    "height": 400,
    "autowidth": True,
    "pagination": True
}
```

## CRUD Operations

### Built-in Form Handling

Complete CRUD operations without additional coding:

**Create (Add):**
- Modal form with field validation
- Required field indicators
- Custom form layouts
- Success/error notifications

**Read (View):**
- Detailed view modal
- Formatted data display
- Related field information
- Printable view option

**Update (Edit):**
- Inline editing support
- Form-based editing
- Batch field updates
- Change tracking

**Delete:**
- Single record deletion
- Bulk deletion
- Confirmation dialogs
- Soft delete support

### Form Customization

```python
class ProductGridView(JQGridView):
    model = Product
    
    # Custom form configuration
    jqgrid_field_overrides = {
        'name': {
            'editrules': {'required': True, 'minlength': 3},
            'editoptions': {'placeholder': 'Enter product name'}
        },
        'price': {
            'formatter': 'currency',
            'formatoptions': {'prefix': '$', 'suffix': ' USD'}
        }
    }
```


## Advanced Filtering

### Search Interface

**Filter Toolbar:**
- Per-column search inputs
- Operator selection (contains, equals, greater than, etc.)
- Date range pickers
- Boolean toggles
- Multi-select dropdowns

**Advanced Search Dialog:**
- Complex query builder
- AND/OR logic combinations
- Nested condition groups
- Save/load search templates
- Export search results

### Filter Types

```python
# Available filter operations
FILTER_OPERATIONS = {
    'text': ['eq', 'ne', 'cn', 'nc', 'bw', 'bn', 'ew', 'en'],
    'number': ['eq', 'ne', 'lt', 'le', 'gt', 'ge'],
    'date': ['eq', 'ne', 'lt', 'le', 'gt', 'ge'],
    'select': ['eq', 'ne', 'in', 'ni'],
    'boolean': ['eq', 'ne']
}
```

### Custom Filters

```python
class ProductGridView(JQGridView):
    model = Product
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Custom filter logic
        if self.request.GET.get('low_stock'):
            queryset = queryset.filter(stock__lt=10)
        
        if self.request.GET.get('category_type'):
            queryset = queryset.filter(
                category__type=self.request.GET['category_type']
            )
        
        return queryset
```

## Bulk Operations

### Built-in Bulk Actions

**Bulk Update:**
- Update multiple records simultaneously
- Field-specific bulk updates
- Conditional bulk updates
- Progress tracking for large operations

**Bulk Delete:**
- Delete multiple selected records
- Confirmation dialogs
- Cascade deletion handling
- Undo functionality

**Custom Bulk Actions:**
```python
class ProductGridView(JQGridView):
    model = Product
    
    bulk_actions = [
        {
            'id': 'mark-featured',
            'label': 'Mark as Featured',
            'icon': 'fa-star',
            'class': 'btn-warning'
        },
        {
            'id': 'apply-discount',
            'label': 'Apply Discount',
            'icon': 'fa-percentage',
            'class': 'btn-info',
            'form_fields': [
                {
                    'name': 'discount_percent',
                    'type': 'number',
                    'label': 'Discount %',
                    'required': True
                }
            ]
        }
    ]
    
    def handle_bulk_action(self, action_id, selected_ids, form_data):
        if action_id == 'mark-featured':
            Product.objects.filter(
                id__in=selected_ids
            ).update(is_featured=True)
            
        elif action_id == 'apply-discount':
            discount = float(form_data['discount_percent']) / 100
            products = Product.objects.filter(id__in=selected_ids)
            for product in products:
                product.price *= (1 - discount)
                product.save()
```

## Multi-Database Support

### Database Routing

```python
class ProductGridView(JQGridView):
    model = Product
    using = 'products_db'  # Specific database
    
    def get_queryset(self):
        return Product.objects.using(self.using).all()

# Multiple database configuration
class MultiDBGridView(JQGridView):
    def get_queryset(self):
        # Route based on user or other criteria
        if self.request.user.is_superuser:
            return Product.objects.using('admin_db').all()
        else:
            return Product.objects.using('user_db').all()
```

### Cross-Database Relations

```python
# Handle relations across databases
class OrderGridView(JQGridView):
    model = Order
    
    def get_queryset(self):
        # Optimize cross-database queries
        return Order.objects.select_related('customer')\
                          .prefetch_related('items')\
                          .using('orders_db')
```

## Responsive Design

### Mobile Optimization

**Responsive Layout:**
- Automatic column hiding on small screens
- Touch-friendly controls
- Swipe gestures for navigation
- Optimized form inputs for mobile

**Adaptive Interface:**
- Collapsible toolbars
- Modal forms for small screens
- Simplified navigation
- Progressive disclosure

### Screen Size Adaptations

```javascript
// Automatic responsive behavior
{
    responsive: true,
    adaptiveHeight: true,
    breakpoints: {
        tablet: 768,
        phone: 480
    },
    hiddenColumns: {
        phone: ['created_at', 'updated_at'],
        tablet: ['description']
    }
}
```

## Security Features

### Authentication Integration

```python
class SecureGridView(JQGridView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter based on user permissions
        if self.request.user.is_superuser:
            return Product.objects.all()
        else:
            return Product.objects.filter(
                created_by=self.request.user
            )
```

### Field-Level Security

```python
def get_column_config(self):
    config = super().get_column_config()
    user = self.request.user
    
    # Hide sensitive fields
    if not user.has_perm('products.view_cost'):
        config['cost']['hidden'] = True
    
    # Make fields read-only
    if not user.has_perm('products.change_price'):
        config['price']['editable'] = False
    
    return config
```

### CSRF Protection

All operations include automatic CSRF protection:
- Form submissions
- AJAX requests
- Bulk operations
- Import/export operations

### Input Validation

```python
# Server-side validation
class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    
    def validate_price(self, value):
        if value <= 0:
            raise ValidationError("Price must be positive")
        return value

# Client-side validation
jqgrid_field_overrides = {
    'price': {
        'editrules': {
            'required': True,
            'number': True,
            'minValue': 0.01
        }
    }
}
```

## Performance Optimization

### Query Optimization

**Automatic Optimization:**
- Select/prefetch related fields
- Query result caching
- Database connection pooling
- Lazy loading of non-essential data

**Custom Optimization:**
```python
class OptimizedGridView(JQGridView):
    model = Product
    
    # Optimize queries
    select_related = ['category', 'manufacturer']
    prefetch_related = ['tags', 'reviews']
    
    # Limit fields
    only_fields = ['id', 'name', 'price', 'stock']
    
    # Add database indexes
    class Meta:
        indexes = [
            models.Index(fields=['name', 'category']),
            models.Index(fields=['price', 'stock']),
        ]
```

### Caching Strategies

```python
from django.core.cache import cache

class CachedGridView(JQGridView):
    cache_timeout = 300  # 5 minutes
    
    def get_grid_data(self, request):
        cache_key = f'grid_data_{self.model.__name__}_{request.GET.urlencode()}'
        data = cache.get(cache_key)
        
        if data is None:
            data = super().get_grid_data(request)
            cache.set(cache_key, data, self.cache_timeout)
        
        return data
```

### Large Dataset Handling

**Pagination Optimization:**
- Cursor-based pagination for large datasets
- Virtual scrolling for smooth performance
- Progressive loading
- Background data preloading

**Memory Management:**
- Efficient serialization
- Streaming responses for exports
- Garbage collection optimization
- Connection pooling

## Customization Options

### Theme Customization

**Built-in Themes:**
- Bootstrap 4/5 integration
- Material Design theme
- Classic jqGrid theme
- Custom CSS theme support

**Custom Styling:**
```css
/* Custom grid styling */
.ui-jqgrid {
    font-family: 'Inter', sans-serif;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.ui-jqgrid-htable th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
}
```

### JavaScript Customization

**Custom Formatters:**
```javascript
// Register custom formatter
window.jqGridConfig.formatters.percentage = function(cellValue, options, rowObject) {
    return `<span class="percentage">${cellValue}%</span>`;
};

// Custom row styling
window.jqGridConfig.rowRenderers.conditional = function(cellValue, options, rowObject) {
    if (rowObject.stock < 10) {
        return 'background-color: #ffebee;';
    }
    return '';
};
```

**Event Handling:**
```javascript
// Grid lifecycle events
$(document).on('jqGrid:afterLoad', function(e, gridId) {
    console.log('Grid loaded:', gridId);
});

$(document).on('jqGrid:beforeSave', function(e, rowData) {
    // Custom validation
    if (rowData.price < 0) {
        e.preventDefault();
        alert('Price cannot be negative');
    }
});
```

### Template Customization

**Custom Grid Templates:**
```html
<!-- templates/custom_grid.html -->
{% extends "django_jqgrid/base.html" %}

{% block grid_toolbar %}
    <div class="custom-toolbar">
        <h2>{{ grid_title }}</h2>
        <div class="custom-buttons">
            <!-- Custom buttons -->
        </div>
    </div>
{% endblock %}

{% block grid_footer %}
    <div class="custom-footer">
        <p>Total Records: <span id="record-count"></span></p>
    </div>
{% endblock %}
```

**Form Templates:**
```html
<!-- Custom edit form -->
<div class="custom-edit-form">
    <div class="form-section">
        <h3>Basic Information</h3>
        <!-- Form fields -->
    </div>
    <div class="form-section">
        <h3>Advanced Options</h3>
        <!-- Additional fields -->
    </div>
</div>
```

### Plugin System

**Custom Plugins:**
```javascript
// Register custom plugin
window.jqGridManager.plugins.customFeature = {
    init: function(tableInstance) {
        // Plugin initialization
    },
    
    activate: function(tableInstance) {
        // Activate plugin features
    }
};
```

**Hook System:**
```python
# Server-side hooks
class CustomGridView(JQGridView):
    def before_save(self, instance, data):
        # Custom logic before saving
        instance.modified_by = self.request.user
        return instance
    
    def after_delete(self, instance):
        # Custom logic after deletion
        log_deletion(instance, self.request.user)
```

This comprehensive feature set makes Django JQGrid a powerful solution for building data-intensive web applications with minimal development time while maintaining full customization capabilities.