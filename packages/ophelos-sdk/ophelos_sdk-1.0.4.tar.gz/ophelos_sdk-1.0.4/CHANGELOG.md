# Changelog

All notable changes to the Ophelos Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2024-12-19

### Fixed
- **Pagination Issue**: Fixed `has_more` always returning `False` in paginated responses
  - Extract pagination from response headers per [Ophelos API specification](https://ophelos-api.readme.io/reference/pagination)
  - Parse Link header for `next`, `prev`, `first` relations with cursor extraction
  - Extract `X-Total-Count` header for total count information
  - Added `pagination` field to `PaginatedResponse` for easy cursor navigation

### Enhanced
- **Development Toolchain**: Added autoflake for code cleanup and improved requirements structure
- **Code Quality**: Applied Black formatting to entire codebase (27 files)
- **Documentation**: Enhanced README.md and USAGE.md with accurate pagination examples

### Added
- **Pagination Examples**: `examples/enhanced_pagination_demo.py` with cursor-based navigation
- **Test Coverage**: Comprehensive pagination tests for Link header parsing and edge cases

### Changed
- **BREAKING CHANGE**: Package renamed from `ophelos` to `ophelos_sdk`
- Import statements now use `from ophelos_sdk import OphelosClient`

## [1.0.3] - 2024-06-24

### Added
- **Access Token Authentication**: Direct access token support alongside OAuth2
- **Model-First API**: `to_api_body()` method with intelligent field management
- **Test Coverage**: 143 model tests and 254+ total tests

### Enhanced
- **Model Organization**: Separate files for each model type
- **Error Handling**: Graceful fallback for invalid API responses
- **Code Quality**: Black, isort, mypy, flake8 compliance

### Fixed
- **JSON Serialization**: Date/datetime handling in API bodies
- **Type Safety**: mypy annotation errors
- **Import Organization**: Standardized across 60 files

## [1.0.2] - 2024-06-14

### Added
- **Multi-tenant Support**: `tenant_id` parameter with automatic header injection
- **Thread Safety**: Thread-safe OAuth2 token management
- **Concurrent Examples**: ThreadPoolExecutor usage patterns

### Enhanced
- **Authentication**: Thread-safe token caching
- **Retry Logic**: Jittered retry with 0-1.5s additive jitter
- **Documentation**: Multi-tenant usage patterns

## [1.0.0] - 2024-01-15

### Added
- Initial release with complete Ophelos API coverage
- OAuth2 client credentials authentication
- Type-safe Pydantic models
- Resource managers for all endpoints
- Webhook signature validation
- Built-in pagination support
- Comprehensive documentation

### Security
- HMAC-SHA256 webhook verification
- Secure credential handling
- Automatic token refresh

## [Unreleased]

### Planned
- Async client support
- Enhanced error messages
- CLI tool for API testing
- Performance optimizations 