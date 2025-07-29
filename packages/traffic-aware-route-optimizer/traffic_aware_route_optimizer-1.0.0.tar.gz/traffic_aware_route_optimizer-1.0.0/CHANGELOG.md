# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-25

### Added
- Initial release of Traffic-Aware Route Optimizer
- Multi-waypoint route optimization using Google Routes API
- Real-time traffic consideration for accurate routing
- Time window constraints for destinations
- Flexible scheduling with configurable work hours and breaks
- Priority-based destination routing
- Support for custom visit durations
- Distance and travel time calculations
- Comprehensive data models with Pydantic validation
- Error handling for API failures and invalid inputs
- Type hints throughout the codebase
- Comprehensive documentation and examples

### Features
- **GoogleRoutesClient** - Main client for route optimization
- **Location** - Geographic coordinate representation  
- **Destination** - Destination with metadata and time constraints
- **OptimizedSchedule** - Complete route optimization results
- **ScheduleStop** - Individual stop details in optimized route
- **Break** - Break time information and scheduling

### API Coverage
- Route optimization with multiple waypoints
- Traffic-aware route calculation
- Time window constraint handling
- Priority-based stop ordering
- Custom scheduling parameters

### Dependencies
- pydantic>=2.0.0 for data validation
- googlemaps>=4.10.0 for Google Maps API integration
- httpx>=0.24.0 for HTTP requests

### Documentation
- Comprehensive README with usage examples
- API reference documentation
- Contributing guidelines
- Example use cases and scenarios
- PyPI publishing guide

## [Unreleased]

### Planned
- Support for vehicle-specific routing (truck, car, bicycle)
- Multiple depot support
- Advanced optimization algorithms
- Route visualization capabilities
- Batch processing for multiple routes
- Enhanced error reporting and diagnostics
