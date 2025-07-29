 # Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-XX

### Added
- Initial release of AgentMeter Python SDK
- Core `AgentMeterClient` for API interactions
- `AgentMeterTracker` for thread-safe usage tracking
- LangChain integration with `LangChainAgentMeterCallback`
- Decorators for automatic function and agent tracking (`@meter_function`, `@meter_agent`)
- Context managers for manual tracking (`track_usage`, `MeterContext`)
- Comprehensive error handling and retry logic
- Support for multiple event types (API_REQUEST, FUNCTION_CALL, AGENT_EXECUTION, CUSTOM)
- Environment variable configuration support
- Automatic batching and flushing of events
- Token usage estimation utilities
- Complete test suite with pytest
- Examples for basic usage and LangChain integration
- Type hints support (py.typed)

### Features
- **API Integration**: Full support for AgentMeter API endpoints
- **LangChain Compatibility**: Built-in callbacks for LangChain agents and chains
- **Thread Safety**: Safe for use in multi-threaded applications
- **Automatic Tracking**: Decorators and context managers for easy integration
- **Flexible Configuration**: Environment variables and programmatic config
- **Error Handling**: Comprehensive exception handling with retries
- **Token Tracking**: Support for input/output token counting
- **Metadata Support**: Rich metadata collection for debugging and analysis

### Documentation
- Complete README with usage examples
- API reference documentation
- LangChain integration guide
- Configuration options documentation