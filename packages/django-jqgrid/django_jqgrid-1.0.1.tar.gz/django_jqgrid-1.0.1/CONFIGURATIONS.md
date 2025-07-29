# Django JQGrid Configuration Guide

This document provides a comprehensive guide to all configuration options available in django-jqgrid.

## Table of Contents

1. [Global Settings](#global-settings)
2. [Model-Level Configuration](#model-level-configuration)
3. [View-Level Configuration](#view-level-configuration)
4. [Column Configuration](#column-configuration)
5. [Grid Options](#grid-options)
6. [Security Configuration](#security-configuration)
7. [Performance Configuration](#performance-configuration)
8. [UI/Theme Configuration](#uitheme-configuration)
9. [JavaScript Configuration](#javascript-configuration)
10. [Advanced Configuration](#advanced-configuration)

## Global Settings

Configure django-jqgrid globally in your Django settings.py file:

### Basic Configuration

```python
# settings.py

JQGRID_CONFIG = {
    # Display Settings
    'GRID_HEIGHT': 400,                    # Default grid height in pixels
    'ROW_NUM': 25,                         # Default rows per page
    'ROW_LIST': [10, 25, 50, 100],        # Page size options
    'VIEWRECORDS': True,                   # Show record count
    'GRIDVIEW': True,                      # Fast rendering mode
    
    # UI Settings
    'ICON_SET': 'fontAwesome',             # Icon set: 'fontAwesome', 'jQueryUI'
    'GUI_STYLE': 'bootstrap4',             # UI style: 'bootstrap4', 'bootstrap5', 'jqueryui'
    'DIRECTION': 'ltr',                    # Text direction: 'ltr', 'rtl'
    
    # Features
    'ENABLE_IMPORT_EXPORT': True,          # Enable import/export functionality
    'ENABLE_FILTERS': True,                # Enable advanced filters
    'ENABLE_COLUMN_CHOOSER': True,         # Allow column show/hide
    'ENABLE_REFRESH': True,                # Show refresh button
    'ENABLE_SEARCH': True,                 # Enable searching
    
    # Performance
    'ENABLE_CACHE': True,                  # Enable configuration caching
    'CACHE_TIMEOUT': 300,                  # Cache timeout in seconds
    'OPTIMIZE_QUERIES': True,              # Enable query optimization
    'USE_SELECT_RELATED': True,            # Auto use select_related
    'USE_PREFETCH_RELATED': True,          # Auto use prefetch_related
    
    # Security
    'ENABLE_CSRF': True,                   # Enable CSRF protection
    'FIELD_LEVEL_PERMISSIONS': False,      # Enable field-level permissions
    'AUDIT_LOG': True,                     # Enable audit logging
    
    # API Settings
    'API_URL_PREFIX': '/api/jqgrid/',      # API URL prefix
    'DATE_FORMAT': 'Y-m-d',                # Date format for API
    'DATETIME_FORMAT': 'Y-m-d H:i:s',      # DateTime format for API
    'TIME_FORMAT': 'H:i:s',                # Time format for API
}
```

### Advanced Global Settings

```python
JQGRID_CONFIG = {
    # Advanced Display
    'ALTERNATE_ROWS': True,                # Alternate row colors
    'AUTO_WIDTH': True,                    # Auto-adjust column widths
    'FORCE_FIT': True,                     # Force columns to fit grid width
    'SHRINK_TO_FIT': True,                 # Shrink columns to fit
    'SCROLL': False,                       # Enable horizontal scrolling
    'SCROLL_OFFSET': 18,                   # Scrollbar width
    
    # Sorting
    'SORT_ON_HEADER_CLICK': True,          # Sort by clicking headers
    'MULTIKEY': 'ctrlKey',                 # Key for multi-column sort
    'SORT_ORDER': 'asc',                   # Default sort order
    'SORT_NAME': None,                     # Default sort column
    
    # Selection
    'MULTISELECT': True,                   # Enable multi-row selection
    'MULTIBOXONLY': False,                 # Select only via checkbox
    'MULTIKEY_SELECT': 'shiftKey',         # Key for multi-select
    
    # Editing
    'CELL_EDIT': False,                    # Enable cell editing
    'INLINE_EDIT': True,                   # Enable inline editing
    'EDIT_URL': 'clientArray',             # Edit URL or 'clientArray'
    
    # Events
    'LOAD_ONCE': False,                    # Load all data at once
    'LOAD_UI': 'enable',                   # Loading UI: 'enable', 'disable', 'block'
    'H_OVERFLOW': False,                   # Horizontal overflow handling
    
    # Subgrid
    'SUBGRID': False,                      # Enable subgrids
    'SUBGRID_WIDTH': 20,                   # Subgrid column width
    
    # Tree Grid
    'TREE_GRID': False,                    # Enable tree grid
    'TREE_GRID_MODEL': 'nested',           # Tree model: 'nested', 'adjacency'
    'EXPAND_COLUMN': 'name',               # Column to show tree icons
}
```

## Model-Level Configuration

Configure grids at the model level using the `JQGridMeta` class:

### Basic Model Configuration

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    class JQGridMeta:
        # Basic grid configuration
        grid_config = {
            'caption': 'Product Inventory',
            'height': 450,
            'multiselect': True,
            'multiboxonly': False,
        }
        
        # Fields configuration
        fields = ['name', 'price', 'stock', 'category']  # Fields to include
        exclude_fields = ['id', 'created_at']            # Fields to exclude
        
        # Default sorting
        sort_name = 'name'
        sort_order = 'asc'
        
        # Features
        enable_crud = True
        enable_import_export = True
        enable_filters = True
```

### Advanced Model Configuration

```python
class Product(models.Model):
    # ... model fields ...
    
    class JQGridMeta:
        # Column-specific configuration
        column_config = {
            'name': {
                'label': 'Product Name',
                'width': 200,
                'searchable': True,
                'sortable': True,
                'editable': True,
                'editrules': {'required': True},
            },
            'price': {
                'label': 'Unit Price',
                'width': 100,
                'formatter': 'currency',
                'formatoptions': {'prefix': '$', 'decimalPlaces': 2},
                'align': 'right',
                'editable': True,
                'editrules': {'number': True, 'minValue': 0},
            },
            'stock': {
                'label': 'In Stock',
                'width': 80,
                'formatter': 'integer',
                'align': 'center',
                'cellattr': 'stock_cellattr',  # Custom cell attributes
                'editable': True,
            },
            'category': {
                'label': 'Category',
                'width': 150,
                'stype': 'select',  # Search type
                'searchoptions': {'sopt': ['eq', 'ne']},
                'editable': True,
                'edittype': 'select',
                'editoptions': {'dataUrl': '/api/categories/'},
            },
        }
        
        # Custom methods
        def stock_cellattr(self, rowId, val, rawObject, cm, rdata):
            """Custom cell attributes based on stock level"""
            if val < 10:
                return 'style="color:red;font-weight:bold;"'
            elif val < 50:
                return 'style="color:orange;"'
            return ''
        
        # Permissions
        can_add = True
        can_edit = True
        can_delete = True
        
        # Bulk actions
        bulk_actions = ['export', 'delete', 'update_price']
        
        # Custom toolbar buttons
        toolbar_buttons = [
            {
                'name': 'import',
                'icon': 'fa-upload',
                'title': 'Import Products',
                'action': 'importProducts',
            },
        ]
```

## View-Level Configuration

Configure grids in your views using mixins:

### Basic View Configuration

```python
from django_jqgrid.mixins import JqGridConfigMixin

class ProductListView(JqGridConfigMixin, ListView):
    model = Product
    template_name = 'products/list.html'
    
    # Override grid configuration
    grid_id = 'product-grid'
    grid_config = {
        'caption': 'Product Management',
        'height': 'auto',
    }
```

### Advanced View Configuration

```python
class ProductViewSet(JqGridConfigMixin, ModelViewSet):
    model = Product
    serializer_class = ProductSerializer
    
    def get_grid_config(self):
        """Dynamic grid configuration"""
        config = super().get_grid_config()
        
        # Customize based on user
        if self.request.user.is_staff:
            config['multiselect'] = True
            config['enable_delete'] = True
        else:
            config['multiselect'] = False
            config['enable_delete'] = False
            
        return config
    
    def get_column_config(self):
        """Dynamic column configuration"""
        config = super().get_column_config()
        
        # Hide price for non-staff users
        if not self.request.user.is_staff:
            config['price']['hidden'] = True
            
        return config
    
    def get_queryset(self):
        """Custom queryset with optimizations"""
        qs = super().get_queryset()
        
        # Apply optimizations
        qs = qs.select_related('category')
        qs = qs.prefetch_related('tags')
        
        # Apply filters
        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
            
        return qs
    
    def get_grid_data(self, request):
        """Custom data processing"""
        data = super().get_grid_data(request)
        
        # Add custom calculations
        for row in data['rows']:
            row['total_value'] = row['price'] * row['stock']
            
        return data
```

## Column Configuration

Detailed column configuration options:

### Basic Column Options

```python
column_config = {
    'field_name': {
        # Display
        'label': 'Column Label',           # Column header text
        'name': 'field_name',              # Field name (auto-set)
        'index': 'field_name',             # Sort index (auto-set)
        'width': 150,                      # Column width in pixels
        'align': 'left',                   # Alignment: 'left', 'center', 'right'
        'classes': 'custom-class',         # CSS classes
        'title': True,                     # Show tooltips
        
        # Visibility
        'hidden': False,                   # Hide column
        'hidedlg': False,                  # Hide from column chooser
        'viewable': True,                  # Include in view dialog
        
        # Features
        'sortable': True,                  # Enable sorting
        'search': True,                    # Enable searching
        'resizable': True,                 # Allow resize
        'fixed': False,                    # Fixed width
        'frozen': False,                   # Freeze column
    }
}
```

### Formatting Options

```python
column_config = {
    'price': {
        'formatter': 'currency',           # Built-in formatter
        'formatoptions': {
            'decimalSeparator': '.',
            'thousandsSeparator': ',',
            'decimalPlaces': 2,
            'prefix': '$',
            'suffix': '',
            'defaultValue': '0.00',
        },
    },
    'date': {
        'formatter': 'date',
        'formatoptions': {
            'srcformat': 'Y-m-d',          # Source format
            'newformat': 'm/d/Y',          # Display format
        },
    },
    'status': {
        'formatter': 'select',             # Select list formatter
        'editoptions': {
            'value': {
                'active': 'Active',
                'inactive': 'Inactive',
                'pending': 'Pending',
            }
        },
    },
    'custom': {
        'formatter': 'customFormatter',    # Custom JS function
        'unformat': 'customUnformatter',   # Custom unformat function
    },
}
```

### Editing Options

```python
column_config = {
    'name': {
        'editable': True,                  # Enable editing
        'edittype': 'text',                # Edit type
        'editoptions': {
            'size': 30,
            'maxlength': 200,
            'placeholder': 'Enter name...',
        },
        'editrules': {
            'required': True,              # Required field
            'edithidden': True,            # Edit hidden fields
            'number': False,               # Number validation
            'integer': False,              # Integer validation
            'minValue': 0,                 # Minimum value
            'maxValue': 1000,              # Maximum value
            'email': False,                # Email validation
            'url': False,                  # URL validation
            'date': False,                 # Date validation
            'custom': True,                # Custom validation
            'custom_func': 'validateName', # Custom function
        },
        'formoptions': {
            'label': 'Product Name:',      # Form label
            'elmprefix': '(*) ',           # Prefix for required
            'elmsuffix': '',               # Suffix text
            'rowpos': 1,                   # Row position
            'colpos': 1,                   # Column position
        },
    },
    'category': {
        'editable': True,
        'edittype': 'select',              # Select dropdown
        'editoptions': {
            'value': 'categories_url',     # URL for options
            'dataUrl': '/api/categories/', # Data URL
            'buildSelect': 'buildSelect',  # Custom builder
            'dataInit': 'initSelect',      # Initialize function
            'dataEvents': [                # Events
                {
                    'type': 'change',
                    'fn': 'categoryChanged',
                },
            ],
        },
        'stype': 'select',                 # Search type
        'searchoptions': {
            'value': ':All;1:Electronics;2:Clothing',
            'sopt': ['eq', 'ne'],          # Search operators
            'dataUrl': '/api/categories/', # Search data URL
        },
    },
}
```

### Search Options

```python
column_config = {
    'name': {
        'search': True,
        'stype': 'text',                   # Search input type
        'searchoptions': {
            'sopt': ['cn', 'eq', 'ne', 'bw', 'ew'], # Search operators
            'clearSearch': True,           # Show clear button
            'searchhidden': True,          # Search hidden columns
            'dataInit': 'initSearch',      # Initialize function
        },
    },
    'price': {
        'search': True,
        'stype': 'text',
        'searchoptions': {
            'sopt': ['eq', 'ne', 'lt', 'le', 'gt', 'ge'],
            'dataInit': 'initPriceRange',  # Custom range picker
        },
    },
    'date': {
        'search': True,
        'stype': 'text',
        'searchoptions': {
            'sopt': ['eq', 'ne', 'lt', 'le', 'gt', 'ge'],
            'dataInit': 'initDatePicker',  # Date picker
            'attr': {'class': 'datepicker'},
        },
    },
}
```

## Grid Options

Complete list of grid configuration options:

### Display Options

```python
grid_config = {
    # Size and Layout
    'width': None,                         # Grid width (None = auto)
    'height': 400,                         # Grid height
    'shrinkToFit': True,                   # Shrink columns to fit
    'forceFit': False,                     # Force column widths
    'autowidth': True,                     # Auto-adjust width
    
    # Appearance
    'caption': 'Grid Title',               # Grid caption
    'hidegrid': True,                      # Show/hide grid button
    'hiddengrid': False,                   # Start hidden
    'rownumbers': True,                    # Show row numbers
    'rownumWidth': 25,                     # Row number column width
    'alternateRows': True,                 # Alternate row colors
    
    # Scrolling
    'scroll': False,                       # Virtual scrolling
    'scrollrows': False,                   # Scroll rows
    'scrollTimeout': 200,                  # Scroll timeout
    'scrollOffset': 18,                    # Scrollbar width
}
```

### Data Options

```python
grid_config = {
    # Data Loading
    'url': '/api/data/',                   # Data URL
    'datatype': 'json',                    # Data type
    'mtype': 'GET',                        # HTTP method
    'loadonce': False,                     # Load all data once
    'loadui': 'enable',                    # Loading UI
    'loadtext': 'Loading...',              # Loading text
    
    # Paging
    'pager': '#pager',                     # Pager element
    'rowNum': 25,                          # Rows per page
    'rowList': [10, 25, 50, 100],         # Page size options
    'page': 1,                             # Initial page
    'viewrecords': True,                   # Show record info
    'recordpos': 'right',                  # Record position
    'records': 0,                          # Total records
    'pagerpos': 'center',                  # Pager position
    'pgbuttons': True,                     # Show page buttons
    'pginput': True,                       # Show page input
    
    # Sorting
    'sortname': '',                        # Sort column
    'sortorder': 'asc',                    # Sort order
    'sorttype': 'text',                    # Sort type
    'sortable': True,                      # Enable sorting
    'multiSort': True,                     # Multi-column sort
}
```

### Selection Options

```python
grid_config = {
    # Row Selection
    'multiselect': True,                   # Multi-row selection
    'multiboxonly': False,                 # Select via checkbox only
    'multiselectWidth': 20,                # Checkbox column width
    'multikey': 'ctrlKey',                 # Multi-select key
    
    # Cell Selection
    'cellEdit': False,                     # Cell editing
    'cellsubmit': 'clientArray',           # Cell submit type
    'cellurl': '/api/cell/',               # Cell save URL
    
    # Events
    'beforeSelectRow': 'beforeSelect',     # Before select event
    'onSelectRow': 'onSelect',             # On select event
    'onSelectAll': 'onSelectAll',          # Select all event
    'ondblClickRow': 'onDoubleClick',      # Double click event
    'onRightClickRow': 'onRightClick',     # Right click event
}
```

### Editing Options

```python
grid_config = {
    # Inline Editing
    'editurl': '/api/edit/',               # Edit URL
    'inlineEditing': True,                 # Enable inline edit
    'restoreAfterError': True,             # Restore on error
    'savedRow': [],                        # Saved row data
    
    # Form Editing
    'editDialog': True,                    # Enable edit dialog
    'editDialogOptions': {
        'width': 500,
        'height': 'auto',
        'modal': True,
        'closeAfterEdit': True,
        'reloadAfterSubmit': True,
    },
    
    # Add Dialog
    'addDialog': True,                     # Enable add dialog
    'addDialogOptions': {
        'width': 500,
        'height': 'auto',
        'modal': True,
        'closeAfterAdd': True,
        'reloadAfterSubmit': True,
    },
    
    # Delete Options
    'deleteDialog': True,                  # Confirm delete
    'deleteDialogOptions': {
        'msg': 'Delete selected records?',
        'bSubmit': 'Delete',
        'bCancel': 'Cancel',
    },
}
```

## Security Configuration

### Authentication Configuration

```python
# settings.py
JQGRID_CONFIG = {
    'AUTHENTICATION': {
        'ENABLED': True,                   # Require authentication
        'BACKENDS': [                      # Auth backends in order
            'session',                     # Django session
            'token',                       # DRF token
            'jwt',                         # JWT token
        ],
        'JWT_HEADER': 'Authorization',     # JWT header name
        'JWT_PREFIX': 'Bearer',            # JWT prefix
        'TOKEN_HEADER': 'X-Auth-Token',    # Token header
    },
}
```

### Permission Configuration

```python
# Model-level permissions
class Product(models.Model):
    class JQGridMeta:
        # Basic permissions
        permission_classes = ['IsAuthenticated']
        
        # Field-level permissions
        field_permissions = {
            'price': ['product.view_price'],
            'cost': ['product.view_cost'],
        }
        
        # Action permissions
        action_permissions = {
            'add': ['product.add_product'],
            'change': ['product.change_product'],
            'delete': ['product.delete_product'],
            'export': ['product.export_product'],
        }
        
        # Row-level permissions
        def has_row_permission(self, user, row, action):
            """Check row-level permissions"""
            if action == 'delete' and row.status == 'locked':
                return False
            return True
```

### CSRF Configuration

```python
JQGRID_CONFIG = {
    'CSRF': {
        'ENABLED': True,                   # Enable CSRF
        'COOKIE_NAME': 'csrftoken',        # CSRF cookie name
        'HEADER_NAME': 'X-CSRFToken',      # CSRF header name
        'SAFE_METHODS': ['GET', 'HEAD', 'OPTIONS', 'TRACE'],
    },
}
```

## Performance Configuration

### Query Optimization

```python
JQGRID_CONFIG = {
    'OPTIMIZATION': {
        'USE_SELECT_RELATED': True,        # Auto select_related
        'SELECT_RELATED_DEPTH': 2,         # Max depth
        'USE_PREFETCH_RELATED': True,      # Auto prefetch_related
        'PREFETCH_LOOKUPS': [              # Custom prefetch
            'tags',
            'categories__parent',
        ],
        'USE_ONLY': True,                  # Use only() for fields
        'USE_DEFER': False,                # Use defer() for fields
        'CHUNK_SIZE': 1000,                # Query chunk size
    },
}
```

### Caching Configuration

```python
JQGRID_CONFIG = {
    'CACHE': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 300,                    # Default timeout
        'KEY_PREFIX': 'jqgrid',            # Cache key prefix
        'VERSION': 1,                      # Cache version
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        },
        
        # What to cache
        'CACHE_CONFIG': True,              # Cache configurations
        'CACHE_DATA': False,               # Cache grid data
        'CACHE_FILTERS': True,             # Cache filter options
        'CACHE_EXPORT': True,              # Cache export data
    },
}
```

### Database Configuration

```python
# Multi-database support
class Product(models.Model):
    class JQGridMeta:
        using = 'products_db'              # Database alias
        
        # Custom router
        def db_for_read(self, **hints):
            """Custom database routing"""
            if self.request.user.is_staff:
                return 'primary_db'
            return 'readonly_db'
```

## UI/Theme Configuration

### Theme Settings

```python
JQGRID_CONFIG = {
    'THEME': {
        'NAME': 'bootstrap4',              # Theme name
        'CSS_FRAMEWORK': 'bootstrap',      # CSS framework
        'ICON_SET': 'fontawesome',         # Icon set
        'CUSTOM_CSS': [                    # Additional CSS
            'css/custom-grid.css',
        ],
        'CUSTOM_JS': [                     # Additional JS
            'js/custom-formatters.js',
        ],
    },
}
```

### Responsive Configuration

```python
grid_config = {
    'responsive': True,                    # Enable responsive
    'responsiveOptions': {
        'breakpoints': {
            'xs': 480,
            'sm': 768,
            'md': 992,
            'lg': 1200,
        },
        'columnVisibility': {              # Hide columns on small screens
            'xs': ['description', 'created_at'],
            'sm': ['created_at'],
        },
    },
}
```

## JavaScript Configuration

### Event Handlers

```javascript
// In your JavaScript file
var gridConfig = {
    // Loading events
    loadBeforeSend: function(xhr, settings) {
        // Before AJAX request
    },
    loadComplete: function(data) {
        // After data loaded
    },
    loadError: function(xhr, status, error) {
        // On load error
    },
    
    // Grid events
    gridComplete: function() {
        // Grid rendering complete
    },
    resizeStop: function(newwidth, index) {
        // Column resize
    },
    
    // Row events
    beforeSelectRow: function(rowid, e) {
        // Before row selection
        return true; // Allow selection
    },
    onSelectRow: function(rowid, status, e) {
        // Row selected
    },
    ondblClickRow: function(rowid, iRow, iCol, e) {
        // Double click row
    },
    
    // Cell events
    beforeEditCell: function(rowid, cellname, value, iRow, iCol) {
        // Before cell edit
    },
    afterEditCell: function(rowid, cellname, value, iRow, iCol) {
        // After cell edit
    },
    
    // Toolbar events
    beforeProcessing: function(data, status, xhr) {
        // Before processing server response
        return true;
    },
};
```

### Custom Formatters

```javascript
// Custom formatter function
function statusFormatter(cellvalue, options, rowObject) {
    var color = 'green';
    if (cellvalue === 'inactive') {
        color = 'red';
    } else if (cellvalue === 'pending') {
        color = 'orange';
    }
    return '<span style="color:' + color + '">' + cellvalue + '</span>';
}

// Custom unformatter
function statusUnformatter(cellvalue, options, cell) {
    return $('span', cell).text();
}

// Register formatter
$.fn.fmatter.status = statusFormatter;
$.fn.fmatter.status.unformat = statusUnformatter;
```

## Advanced Configuration

### Subgrid Configuration

```python
grid_config = {
    'subGrid': True,
    'subGridUrl': '/api/subgrid/',
    'subGridModel': [{
        'name': ['No', 'Item', 'Qty', 'Unit', 'Line Total'],
        'width': [55, 200, 80, 80, 100],
        'align': ['left', 'left', 'right', 'right', 'right'],
        'params': ['id'],
    }],
    'subGridOptions': {
        'plusicon': 'fa fa-plus',
        'minusicon': 'fa fa-minus',
        'openicon': 'fa fa-caret-right',
        'expandOnLoad': False,
        'selectOnExpand': True,
        'reloadOnExpand': True,
    },
}
```

### Tree Grid Configuration

```python
grid_config = {
    'treeGrid': True,
    'treeGridModel': 'adjacency',          # or 'nested'
    'ExpandColumn': 'name',
    'treedatatype': 'json',
    'treeReader': {
        'level_field': 'level',
        'parent_id_field': 'parent',
        'leaf_field': 'isLeaf',
        'expanded_field': 'expanded',
    },
    'tree_root_level': 0,
    'treeIcons': {
        'plus': 'fa fa-plus-square-o',
        'minus': 'fa fa-minus-square-o',
        'leaf': 'fa fa-file-o',
    },
}
```

### Custom Toolbar

```python
class Product(models.Model):
    class JQGridMeta:
        toolbar = [True, "top"]             # Show toolbar at top
        toolbar_buttons = [
            {
                'id': 'refresh',
                'icon': 'fa-refresh',
                'title': 'Refresh Grid',
                'action': 'refreshGrid',
            },
            {
                'id': 'columns',
                'icon': 'fa-columns',
                'title': 'Choose Columns',
                'action': 'columnChooser',
            },
            {
                'id': 'export',
                'icon': 'fa-download',
                'title': 'Export',
                'action': 'exportGrid',
                'options': ['excel', 'csv', 'pdf'],
            },
            {
                'id': 'filter',
                'icon': 'fa-filter',
                'title': 'Advanced Filter',
                'action': 'showFilter',
            },
            {
                'type': 'separator',
            },
            {
                'id': 'custom',
                'text': 'Custom Action',
                'icon': 'fa-cog',
                'action': 'customAction',
                'class': 'btn-primary',
            },
        ]
```

### Grouping Configuration

```python
grid_config = {
    'grouping': True,
    'groupingView': {
        'groupField': ['category'],         # Group by fields
        'groupOrder': ['asc'],              # Group order
        'groupText': ['<b>{0} - {1} Item(s)</b>'],
        'groupColumnShow': [True],          # Show group column
        'groupSummary': [True],             # Show summary
        'groupSummaryPos': ['footer'],      # Summary position
        'groupCollapse': False,             # Start collapsed
        'plusicon': 'fa fa-plus-square-o',
        'minusicon': 'fa fa-minus-square-o',
    },
    'groupingRemoveIcon': True,             # Remove icon option
    'groupingGroupBy': 'category,status',   # Multi-level grouping
}
```

### Export Configuration

```python
JQGRID_CONFIG = {
    'EXPORT': {
        'FORMATS': ['xlsx', 'csv', 'json', 'xml', 'pdf'],
        'MAX_ROWS': 10000,                 # Max export rows
        'CHUNK_SIZE': 1000,                # Export chunk size
        'INCLUDE_HEADERS': True,           # Include headers
        'EXCEL_OPTIONS': {
            'SHEET_NAME': 'Data Export',
            'AUTHOR': 'Django JQGrid',
            'FREEZE_PANES': True,
            'AUTO_FILTER': True,
        },
        'CSV_OPTIONS': {
            'DELIMITER': ',',
            'QUOTE_CHAR': '"',
            'ENCODING': 'utf-8',
        },
        'PDF_OPTIONS': {
            'ORIENTATION': 'portrait',
            'PAGE_SIZE': 'A4',
            'FONT_SIZE': 10,
        },
    },
}
```

### Import Configuration

```python
JQGRID_CONFIG = {
    'IMPORT': {
        'FORMATS': ['xlsx', 'csv'],        # Allowed formats
        'MAX_FILE_SIZE': 10485760,         # 10MB
        'CHUNK_SIZE': 500,                 # Import chunk size
        'VALIDATE_BEFORE_SAVE': True,      # Validate all rows
        'IGNORE_ERRORS': False,            # Continue on errors
        'DUPLICATE_HANDLING': 'update',    # 'skip', 'update', 'error'
        'FIELD_MAPPING': {                 # Map import fields
            'Product Name': 'name',
            'Price': 'price',
            'In Stock': 'stock',
        },
    },
}
```

## Environment Variables

You can also configure django-jqgrid using environment variables:

```bash
# Basic settings
JQGRID_DEBUG=True
JQGRID_CACHE_ENABLED=True
JQGRID_CACHE_TIMEOUT=300

# Security
JQGRID_CSRF_ENABLED=True
JQGRID_AUTH_REQUIRED=True

# Performance
JQGRID_OPTIMIZE_QUERIES=True
JQGRID_PAGE_SIZE=25

# UI
JQGRID_THEME=bootstrap4
JQGRID_ICON_SET=fontawesome
```

## Configuration Best Practices

1. **Start Simple**: Use defaults and add configuration as needed
2. **Use Model Meta**: Define common settings at the model level
3. **Override in Views**: Customize for specific use cases
4. **Cache Configurations**: Enable caching for better performance
5. **Security First**: Always enable CSRF and authentication
6. **Optimize Queries**: Use select_related and prefetch_related
7. **Test Configuration**: Test different configurations in development
8. **Document Custom Code**: Document custom formatters and validators
9. **Version Control**: Track configuration changes in version control
10. **Monitor Performance**: Use Django Debug Toolbar to monitor queries

This comprehensive configuration guide covers all aspects of django-jqgrid configuration. The package is designed to work with minimal configuration while providing extensive customization options for advanced use cases.