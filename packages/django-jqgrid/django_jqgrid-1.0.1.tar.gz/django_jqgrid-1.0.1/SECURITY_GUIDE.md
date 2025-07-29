# Django JQGrid Security Configuration Guide

## Overview

Django JQGrid provides flexible security configuration supporting multiple authentication methods including session-based CSRF, token-based authentication, and JWT tokens. This guide covers all security features and configuration options.

## Quick Setup

### 1. Add Context Processor

Add the security context processor to your Django settings:

```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                # ... other context processors
                'django_jqgrid.context_processors.jqgrid_security',
            ],
        },
    },
]
```

### 2. Configure Security Settings

Add security configuration to your Django settings:

```python
# settings.py
JQGRID_SECURITY_CONFIG = {
    'auth_method': 'session',  # 'session', 'token', 'jwt', 'auto'
    'csrf_enabled': True,
    'require_authentication': True,
}
```

## Authentication Methods

### 1. Session-Based Authentication (Default)

Best for traditional Django applications with session-based authentication.

```python
# settings.py
JQGRID_SECURITY_CONFIG = {
    'auth_method': 'session',
    'csrf_enabled': True,
    'csrf_token_name': 'csrftoken',
    'csrf_header_name': 'X-CSRFToken',
    'session_enabled': True,
    'session_check_endpoint': '/api/auth/check/',
    'login_redirect': '/login/',
    'require_authentication': True,
}

# Optional: Auto session checking
JQGRID_SECURITY_CONFIG.update({
    'session_auto_check': True,
    'session_check_interval': 300000,  # 5 minutes
})
```

**Features:**
- ✅ CSRF protection
- ✅ Session validation
- ✅ Automatic login redirect
- ✅ Session monitoring

### 2. Token-Based Authentication

Best for API-first applications or when integrating with external systems.

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'rest_framework.authtoken',  # Required for token auth
    'django_jqgrid',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

JQGRID_SECURITY_CONFIG = {
    'auth_method': 'token',
    'csrf_enabled': False,  # Not needed with token auth
    'token_enabled': True,
    'token_type': 'Bearer',  # or 'Token', 'API-Key'
    'token_header_name': 'Authorization',
    'token_key': 'auth_token',
    'token_storage': 'localStorage',  # or 'sessionStorage', 'cookie'
    'require_authentication': True,
}
```

**JavaScript Usage:**
```javascript
// Set token after login
window.jqGridSecurity.setAuthToken('your-token-here');

// Token is automatically included in all requests
```

### 3. JWT Authentication

Best for modern applications requiring stateless authentication.

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'rest_framework',
    'rest_framework_simplejwt',  # Required for JWT
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
    'jwt_header_name': 'Authorization',
    'jwt_token_key': 'jwt_token',
    'jwt_storage': 'localStorage',
    'jwt_refresh_key': 'refresh_token',
    'jwt_auto_refresh': True,
    'jwt_refresh_endpoint': '/api/auth/refresh/',
    'require_authentication': True,
}
```

**JavaScript Usage:**
```javascript
// Set JWT tokens after login
window.jqGridSecurity.setJWTTokens('access-token', 'refresh-token');

// Tokens are automatically managed and refreshed
```

### 4. Auto-Detection

Automatically detects the best authentication method based on installed packages:

```python
# settings.py
JQGRID_SECURITY_CONFIG = {
    'auth_method': 'auto',  # Detects JWT > Token > Session
    'require_authentication': True,
}
```

## Security Profiles

Use predefined security profiles for common scenarios:

```python
# settings.py
from django_jqgrid.security import apply_security_profile

# Apply a security profile
apply_security_profile('high_security')
```

### Available Profiles

#### 1. Session Only (Default)
```python
apply_security_profile('session_only')
```
- Session-based authentication
- CSRF protection enabled
- Authentication required

#### 2. Token Authentication
```python
apply_security_profile('token_auth')
```
- Token-based authentication
- CSRF disabled
- Bearer token format

#### 3. JWT Authentication
```python
apply_security_profile('jwt_auth')
```
- JWT authentication
- Auto token refresh
- CSRF disabled

#### 4. Public Access
```python
apply_security_profile('public_access')
```
- No authentication required
- CSRF enabled for forms
- Good for public read-only grids

#### 5. High Security
```python
apply_security_profile('high_security')
```
- JWT authentication
- CSRF protection
- Field-level permissions
- Audit logging
- Rate limiting
- Session monitoring

## Field-Level Permissions

Control field visibility and editability based on user permissions:

```python
# views.py
from django_jqgrid.security import JQGridFieldPermission

class SecureProductView(JQGridView):
    model = Product
    
    def get_column_config(self):
        config = super().get_column_config()
        
        # Check field-level permissions
        field_perms = JQGridFieldPermission(self.request.user, self.model)
        
        for field_name, field_config in config.items():
            # Hide fields user can't view
            if not field_perms.can_view_field(field_name):
                field_config['hidden'] = True
            
            # Make fields read-only if user can't edit
            if not field_perms.can_edit_field(field_name):
                field_config['editable'] = False
        
        return config
```

### Django Permissions

Create custom permissions for field-level access:

```python
# models.py
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        permissions = [
            ('view_product_cost', 'Can view product cost'),
            ('change_product_cost', 'Can change product cost'),
            ('view_product_price', 'Can view product price'),
            ('change_product_price', 'Can change product price'),
        ]
```

## Custom Security Headers

Add custom headers to all requests:

```python
# settings.py
JQGRID_SECURITY_CONFIG = {
    'custom_headers': {
        'X-API-Version': '1.0',
        'X-Client-Type': 'jqgrid',
        'X-Request-ID': 'auto-generate',  # Special value for auto-generation
    }
}
```

## JavaScript Security API

### Configuration

```javascript
// Custom security configuration
window.JQGRID_SECURITY_CONFIG = {
    authMethod: 'jwt',
    jwt: {
        enabled: true,
        autoRefresh: true,
        refreshEndpoint: '/api/auth/refresh/'
    },
    callbacks: {
        onUnauthorized: function(xhr, status, error) {
            // Custom unauthorized handler
            window.location.href = '/login/';
        },
        onTokenExpired: function() {
            // Custom token expiry handler
            alert('Your session has expired. Please log in again.');
        }
    }
};
```

### Token Management

```javascript
// Set authentication tokens
window.jqGridSecurity.setAuthToken('your-api-token');
window.jqGridSecurity.setJWTTokens('access-token', 'refresh-token');

// Clear all tokens
window.jqGridSecurity.clearTokens();

// Get current security headers
var headers = window.jqGridSecurity.getSecurityHeaders();
console.log(headers); // { 'Authorization': 'Bearer token...', 'X-CSRFToken': '...' }

// Check session
window.jqGridSecurity.checkSession();
```

### Event Callbacks

```javascript
// Security event handlers
window.jqGridSecurity.updateConfig({
    callbacks: {
        beforeRequest: function(xhr, settings) {
            console.log('Making request to:', settings.url);
        },
        
        afterRequest: function(xhr, status) {
            console.log('Request completed with status:', status);
        },
        
        onUnauthorized: function(xhr, status, error) {
            // Redirect to login
            window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
        },
        
        onForbidden: function(xhr, status, error) {
            alert('You do not have permission to perform this action.');
        },
        
        onTokenExpired: function() {
            // Handle token expiration
            window.jqGridSecurity.clearTokens();
            window.location.href = '/login/';
        }
    }
});
```

## Security Best Practices

### 1. Production Settings

```python
# production_settings.py
JQGRID_SECURITY_CONFIG = {
    'auth_method': 'jwt',
    'csrf_enabled': True,
    'require_authentication': True,
    'field_level_permissions': True,
    'audit_log_enabled': True,
    'rate_limiting_enabled': True,
    'session_auto_check': True,
    'session_check_interval': 300000,  # 5 minutes
    'custom_headers': {
        'X-API-Version': '1.0',
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
    }
}

# HTTPS enforcement
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
```

### 2. Permission Classes

```python
# permissions.py
from rest_framework.permissions import BasePermission
from django_jqgrid.security import JQGridPermission

class ProductGridPermission(JQGridPermission):
    """Custom permission for product grid"""
    
    def has_permission(self, request, view):
        # Basic authentication check
        if not super().has_permission(request, view):
            return False
        
        # Custom business logic
        if request.method == 'DELETE':
            return request.user.has_perm('products.delete_product')
        
        return True

# views.py
class ProductGridView(JQGridView):
    model = Product
    permission_classes = [ProductGridPermission]
```

### 3. Rate Limiting

```python
# Install django-ratelimit
# pip install django-ratelimit

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

@method_decorator(ratelimit(key='user', rate='100/h', method='POST'), name='post')
class ProductGridView(JQGridView):
    model = Product
```

### 4. Audit Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django_jqgrid.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
}

JQGRID_SECURITY_CONFIG = {
    'audit_log_enabled': True,
}
```

## Troubleshooting

### Common Issues

1. **CSRF Token Missing**
   ```javascript
   // Check if CSRF token is available
   console.log('CSRF Token:', window.jqGridSecurity.getCSRFToken());
   ```

2. **Token Not Included in Requests**
   ```javascript
   // Verify security headers
   console.log('Security Headers:', window.jqGridSecurity.getSecurityHeaders());
   ```

3. **Session Expired**
   ```javascript
   // Force session check
   window.jqGridSecurity.checkSession();
   ```

4. **Permission Denied**
   ```python
   # Check user permissions in Django shell
   user.get_all_permissions()
   user.has_perm('app.view_model')
   ```

### Debug Mode

Enable debug logging:

```python
# settings.py
LOGGING = {
    'loggers': {
        'django_jqgrid.security': {
            'level': 'DEBUG',
        },
    },
}
```

```javascript
// Enable JavaScript debugging
window.jqGridSecurity.config.debug = true;
```

## Migration Guide

### From Basic Setup

If you're upgrading from basic django-jqgrid without security:

1. Add context processor
2. Add security configuration
3. Update templates if needed
4. Test authentication flow

### From Custom Security

If you have custom security implementation:

1. Review current security setup
2. Map to new configuration options
3. Update JavaScript if needed
4. Test thoroughly

This comprehensive security system provides flexible authentication and authorization options while maintaining backward compatibility and ease of use.