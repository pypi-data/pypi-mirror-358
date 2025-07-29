# Changelog

All notable changes to django-jqgrid will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.32] - 2024-12-18

### Added
- Enhanced import/export functionality with background processing
- FontAwesome icon library integration
- Comprehensive API documentation
- Advanced features documentation
- Installation guide with demo project setup
- Automated setup scripts for demo project
- REST Framework integration improvements
- Better error handling and validation
- Enhanced JavaScript API with hooks system
- Improved documentation and examples

### Enhanced
- Import/Export UI with better user experience
- Column mapping interface for imports
- Export format selection with templates
- Background task processing for large operations
- Progress tracking for import/export operations
- Better mobile responsiveness
- Improved security features

### Fixed
- Missing REST Framework configuration in demo project
- Icon display issues in import/export buttons
- JavaScript error handling improvements
- Template rendering optimizations

## [1.0.0] - 2024-01-15

### Added
- Initial release of django-jqgrid
- Auto-configuration system for Django models
- Full CRUD support with REST API integration
- Advanced filtering and search capabilities
- Import/Export functionality for Excel and CSV
- Bulk actions support
- Field-level permissions
- Query optimization with automatic select_related/prefetch_related
- Configuration caching for improved performance
- Comprehensive template tag system
- Management command for model discovery
- Multi-database support
- Responsive grid layouts
- Custom formatter support
- JavaScript hooks for extensibility
- Extensive configuration options via Django settings
- Field-specific configuration methods
- Permission-based field visibility
- Dynamic model loading
- Custom bulk action handlers
- Theme support (Bootstrap 4/5, jQuery UI)
- Internationalization support

### Security
- CSRF protection enabled by default
- Field-level permission checks
- XSS prevention in formatters

## [0.9.0] - 2024-01-01 (Pre-release)

### Added
- Beta version with core functionality
- Basic grid rendering
- CRUD operations
- Simple filtering

### Known Issues
- Performance optimization not implemented
- Limited customization options
- No caching support

## Future Releases

### [1.1.0] - Planned
- GraphQL support
- Real-time updates via WebSockets
- Advanced export formats (PDF, XML)
- Column grouping
- Pivot table support
- Enhanced mobile responsiveness

### [1.2.0] - Planned
- AI-powered data insights
- Advanced charting integration
- Audit trail functionality
- Version control for data changes
- Collaborative editing features