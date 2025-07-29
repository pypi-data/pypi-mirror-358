# Django JQGrid Security Examples

This file provides practical examples of implementing security features in Django JQGrid.

## Example 1: Session-Based Authentication

### Django Settings
```python
# settings.py
JQGRID_SECURITY_CONFIG = {
    'auth_method': 'session',
    'csrf_enabled': True,
    'require_authentication': True,
    'session_enabled': True,
    'login_redirect': '/accounts/login/',
}
```

### View Implementation
```python
# views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django_jqgrid.api_views import JqGridModelViewSet

class SecureProductView(LoginRequiredMixin, JqGridModelViewSet):
    model = Product
    login_url = '/accounts/login/'
    
    def get_queryset(self):
        # Only show products for the authenticated user
        return Product.objects.filter(created_by=self.request.user)
```

### Template Usage
```html
<!-- products.html -->
{% extends "base.html" %}
{% load jqgrid_tags %}

{% block content %}
    <h1>My Products</h1>
    {% if user.is_authenticated %}
        {% jqgrid 'products-grid' 'myapp' 'product' %}
    {% else %}
        <p><a href="{% url 'login' %}">Login</a> to view products.</p>
    {% endif %}
{% endblock %}

{% block extra_js %}
    {% jqgrid_js %}
    <script>
        $(document).ready(function() {
            // Initialize grid for authenticated users
            if (window.jqGridSecurity.config.session.enabled) {
                window.jqGridManager.initializeTable({
                    gridId: 'products-grid',
                    appName: 'myapp',
                    tableName: 'product'
                });
            }
        });
    </script>
{% endblock %}
```

## Example 2: Token-Based Authentication

### Django Settings
```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'rest_framework.authtoken',
    'django_jqgrid',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

JQGRID_SECURITY_CONFIG = {
    'auth_method': 'token',
    'csrf_enabled': False,
    'token_enabled': True,
    'token_type': 'Bearer',
    'token_storage': 'localStorage',
    'require_authentication': True,
}
```

### API View with Token Auth
```python
# views.py
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_jqgrid.api_views import JqGridModelViewSet

class TokenProductView(JqGridModelViewSet):
    model = Product
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)

@api_view(['POST'])
def get_auth_token(request):
    """Get authentication token for user"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    else:
        return Response({'error': 'Invalid credentials'}, status=401)
```

### Frontend Implementation
```html
<!-- login.html -->
<form id="login-form">
    <input type="text" id="username" placeholder="Username" required>
    <input type="password" id="password" placeholder="Password" required>
    <button type="submit">Login</button>
</form>

<script>
$('#login-form').on('submit', function(e) {
    e.preventDefault();
    
    $.ajax({
        url: '/api/auth/token/',
        method: 'POST',
        data: {
            username: $('#username').val(),
            password: $('#password').val()
        },
        success: function(response) {
            // Store token
            window.jqGridSecurity.setAuthToken(response.token);
            
            // Redirect to main page
            window.location.href = '/products/';
        },
        error: function() {
            alert('Invalid credentials');
        }
    });
});
</script>
```

## Example 3: JWT Authentication

### Django Settings
```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_jqgrid',
]

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

JQGRID_SECURITY_CONFIG = {
    'auth_method': 'jwt',
    'csrf_enabled': False,
    'jwt_enabled': True,
    'jwt_auto_refresh': True,
    'jwt_refresh_endpoint': '/api/auth/refresh/',
    'require_authentication': True,
}
```

### JWT Authentication View
```python
# views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# urls.py
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('api/auth/login/', CustomTokenObtainPairView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    # ... other URLs
]
```

### Frontend JWT Implementation
```javascript
// login.js
function loginWithJWT(username, password) {
    $.ajax({
        url: '/api/auth/login/',
        method: 'POST',
        data: {
            username: username,
            password: password
        },
        success: function(response) {
            // Store JWT tokens
            window.jqGridSecurity.setJWTTokens(
                response.access,
                response.refresh
            );
            
            // Initialize grids
            initializeGrids();
        },
        error: function() {
            alert('Login failed');
        }
    });
}

// Auto-refresh handling
window.jqGridSecurity.updateConfig({
    callbacks: {
        onTokenExpired: function() {
            console.log('Token expired, redirecting to login');
            window.location.href = '/login/';
        }
    }
});
```

## Example 4: Field-Level Permissions

### Model with Custom Permissions
```python
# models.py
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        permissions = [
            ('view_product_cost', 'Can view product cost'),
            ('change_product_cost', 'Can change product cost'),
            ('view_all_products', 'Can view all products'),
        ]
```

### View with Field Permissions
```python
# views.py
from django_jqgrid.security import JQGridFieldPermission

class ProductView(JqGridModelViewSet):
    model = Product
    
    def get_queryset(self):
        user = self.request.user
        if user.has_perm('myapp.view_all_products'):
            return Product.objects.all()
        else:
            return Product.objects.filter(owner=user)
    
    def get_column_config(self):
        config = super().get_column_config()
        user = self.request.user
        
        # Field-level permission checking
        field_perms = JQGridFieldPermission(user, self.model)
        
        # Hide cost field if user can't view it
        if not user.has_perm('myapp.view_product_cost'):
            config['cost']['hidden'] = True
        
        # Make cost read-only if user can't change it
        if not user.has_perm('myapp.change_product_cost'):
            config['cost']['editable'] = False
        
        # Dynamic field visibility based on ownership
        if not user.has_perm('myapp.view_all_products'):
            # Hide owner field for non-admin users
            config['owner']['hidden'] = True
        
        return config
```

### Group-Based Permissions
```python
# permissions.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def setup_product_permissions():
    """Setup group-based permissions for products"""
    
    # Get content type
    content_type = ContentType.objects.get_for_model(Product)
    
    # Create groups
    managers_group, _ = Group.objects.get_or_create(name='Product Managers')
    staff_group, _ = Group.objects.get_or_create(name='Staff')
    
    # Assign permissions to managers
    manager_perms = [
        'view_product',
        'add_product',
        'change_product',
        'delete_product',
        'view_product_cost',
        'change_product_cost',
        'view_all_products',
    ]
    
    for perm_name in manager_perms:
        try:
            permission = Permission.objects.get(
                codename=perm_name,
                content_type=content_type
            )
            managers_group.permissions.add(permission)
        except Permission.DoesNotExist:
            print(f"Permission {perm_name} not found")
    
    # Assign limited permissions to staff
    staff_perms = [
        'view_product',
        'add_product',
        'change_product',
    ]
    
    for perm_name in staff_perms:
        try:
            permission = Permission.objects.get(
                codename=perm_name,
                content_type=content_type
            )
            staff_group.permissions.add(permission)
        except Permission.DoesNotExist:
            print(f"Permission {perm_name} not found")

# Call this in your data migration or management command
setup_product_permissions()
```

## Example 5: Multi-Authentication Support

### Settings for Multiple Auth Methods
```python
# settings.py
JQGRID_SECURITY_CONFIG = {
    'auth_method': 'auto',  # Auto-detect best method
    'csrf_enabled': True,
    'token_enabled': True,
    'jwt_enabled': True,
    'require_authentication': True,
    
    # Fallback configuration
    'session_enabled': True,
    'login_redirect': '/login/',
    
    # Custom headers for API versioning
    'custom_headers': {
        'X-API-Version': '2.0',
        'X-Client-ID': 'jqgrid-client'
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

### View Supporting Multiple Auth
```python
# views.py
class FlexibleProductView(JqGridModelViewSet):
    model = Product
    
    def get_permissions(self):
        """Dynamic permissions based on authentication method"""
        if self.request.auth:  # Token or JWT auth
            return [IsAuthenticated()]
        else:  # Session auth
            return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        # Different access levels based on auth method
        if hasattr(self.request, 'auth') and self.request.auth:
            # API access - more restrictive
            return Product.objects.filter(
                owner=user,
                is_active=True
            )
        else:
            # Web access - full access for staff
            if user.is_staff:
                return Product.objects.all()
            else:
                return Product.objects.filter(owner=user)
```

### JavaScript Multi-Auth Handler
```javascript
// multi-auth.js
window.MultiAuthHandler = {
    init: function() {
        // Try to determine auth method
        var authMethod = this.detectAuthMethod();
        
        // Update security configuration
        window.jqGridSecurity.updateConfig({
            authMethod: authMethod
        });
        
        console.log('Using authentication method:', authMethod);
    },
    
    detectAuthMethod: function() {
        // Check for JWT token
        if (localStorage.getItem('jwt_token')) {
            return 'jwt';
        }
        
        // Check for API token
        if (localStorage.getItem('auth_token')) {
            return 'token';
        }
        
        // Default to session
        return 'session';
    },
    
    login: function(credentials, preferredMethod) {
        var self = this;
        
        switch (preferredMethod) {
            case 'jwt':
                this.loginJWT(credentials);
                break;
            case 'token':
                this.loginToken(credentials);
                break;
            default:
                this.loginSession(credentials);
        }
    },
    
    loginJWT: function(credentials) {
        $.ajax({
            url: '/api/auth/jwt/login/',
            method: 'POST',
            data: credentials,
            success: function(response) {
                window.jqGridSecurity.setJWTTokens(
                    response.access,
                    response.refresh
                );
                window.location.reload();
            }
        });
    },
    
    loginToken: function(credentials) {
        $.ajax({
            url: '/api/auth/token/',
            method: 'POST',
            data: credentials,
            success: function(response) {
                window.jqGridSecurity.setAuthToken(response.token);
                window.location.reload();
            }
        });
    },
    
    loginSession: function(credentials) {
        // Use traditional form submission for session auth
        $('#login-form').submit();
    }
};

// Initialize on page load
$(document).ready(function() {
    window.MultiAuthHandler.init();
});
```

## Example 6: High Security Configuration

### Production Security Settings
```python
# production_settings.py
import os

# High security configuration
JQGRID_SECURITY_CONFIG = {
    'auth_method': 'jwt',
    'csrf_enabled': True,
    'require_authentication': True,
    'field_level_permissions': True,
    'audit_log_enabled': True,
    'rate_limiting_enabled': True,
    
    # JWT settings
    'jwt_enabled': True,
    'jwt_auto_refresh': True,
    'jwt_refresh_endpoint': '/api/auth/refresh/',
    
    # Session monitoring
    'session_enabled': True,
    'session_auto_check': True,
    'session_check_interval': 60000,  # 1 minute
    'session_check_endpoint': '/api/auth/check/',
    
    # Security headers
    'custom_headers': {
        'X-API-Version': '1.0',
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    }
}

# Additional security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
X_FRAME_OPTIONS = 'DENY'

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django_jqgrid.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Secure View Implementation
```python
# secure_views.py
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django_ratelimit.decorators import ratelimit
from django_jqgrid.api_views import JqGridModelViewSet
from django_jqgrid.security import JQGridPermission, log_security_event

@method_decorator([
    csrf_protect,
    never_cache,
    ratelimit(key='user', rate='100/h', method='POST'),
    ratelimit(key='user', rate='1000/h', method='GET'),
], name='dispatch')
class SecureProductView(JqGridModelViewSet):
    model = Product
    permission_classes = [JQGridPermission]
    
    def dispatch(self, request, *args, **kwargs):
        # Log access attempt
        log_security_event(
            request.user if request.user.is_authenticated else 'anonymous',
            'grid_access',
            {'model': 'Product', 'ip': request.META.get('REMOTE_ADDR')}
        )
        return super().dispatch(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Log creation
        log_security_event(
            self.request.user,
            'record_create',
            {'model': 'Product', 'data': serializer.validated_data}
        )
        super().perform_create(serializer)
    
    def perform_update(self, serializer):
        # Log updates
        log_security_event(
            self.request.user,
            'record_update',
            {'model': 'Product', 'pk': serializer.instance.pk}
        )
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        # Log deletion
        log_security_event(
            self.request.user,
            'record_delete',
            {'model': 'Product', 'pk': instance.pk}
        )
        super().perform_destroy(instance)
```

These examples demonstrate various security scenarios and can be adapted to your specific use case. The security system is designed to be flexible and can accommodate different authentication methods and security requirements.