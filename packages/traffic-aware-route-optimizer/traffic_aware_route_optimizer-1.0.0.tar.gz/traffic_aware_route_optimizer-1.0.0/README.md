# Traffic-Aware Route Optimizer

A lightweight, extensible Python library for traffic-aware route optimization using Google Routes API. This tool provides multi-waypoint route optimization with real-time traffic consideration, time window constraints, and flexible scheduling options.

## Project Description

The Traffic-Aware Route Optimizer aims to provide an extendable, efficient route optimization solution for Python applications. This tool is built for Python 3.8+ and provides a simple yet powerful interface for complex routing problems.

## Documentation

The documentation and examples can be found in this README and the project's GitHub repository.

## Project Status

This tool is actively maintained and has been successfully deployed in various logistics and routing applications. We welcome contributions and feedback from the community.

## Features

- **Multi-waypoint route optimization** - Optimize routes with multiple stops
- **Real-time traffic consideration** - Uses Google Routes API for current traffic data
- **Time window constraints** - Support for delivery time windows and scheduling
- **Flexible scheduling options** - Configurable work hours, break times, and visit durations
- **Distance and duration calculations** - Accurate travel time and distance metrics
- **Priority-based routing** - Support for different destination priorities

## Installation and Usage

We recommend using a virtual environment for development.

### Installation from PyPI

```bash
pip install traffic-aware-route-optimizer
```

### Development Installation

Clone the repository and install in development mode:

```bash
git clone https://github.com/lutic1/traffic-aware-route-optimizer.git
cd traffic-aware-route-optimizer
pip install -e .
```

## Usage Example

```python
from route_planner import GoogleRoutesClient, Location, Destination

# Initialize client with your Google Routes API key
client = GoogleRoutesClient(api_key="YOUR_GOOGLE_ROUTES_API_KEY")

# Define starting location
start_location = Location(lat=40.7128, lng=-74.0060)

# Define destinations to visit
destinations = [
    Destination(
        destination_id="stop_1",
        name="First Stop",
        address="123 Main St, New York, NY",
        lat=40.7589,
        lng=-73.9851,
        priority=1,  # Higher priority (1=urgent, 5=low)
        time_window_start="09:00",
        time_window_end="17:00"
    ),
    Destination(
        destination_id="stop_2", 
        name="Second Stop",
        address="456 Broadway, New York, NY",
        lat=40.7831,
        lng=-73.9712,
        priority=2
    )
]

# Optimize the route
try:
    optimized_route = client.optimize_route(
        start_location=start_location,
        destinations=destinations,
        visit_duration_minutes=30,
        work_start="08:00",
        work_end="18:00"
    )
    
    print(f"Total distance: {optimized_route.total_drive_km:.2f} km")
    print(f"Total time: {optimized_route.total_drive_minutes} minutes")
    
    for stop in optimized_route.stops:
        print(f"Stop {stop.sequence_number}: {stop.destination.name}")
        print(f"  Arrival: {stop.arrival}")
        print(f"  Departure: {stop.departure}")
        
except Exception as e:
    print(f"Route optimization failed: {e}")
```

## Requirements

- Python 3.8+
- Google Routes API key
- Dependencies:
  - `pydantic>=2.0.0` - Data validation and parsing
  - `googlemaps>=4.10.0` - Google Maps API client
  - `httpx>=0.24.0` - HTTP client for API requests

## Configuration

Set your Google Routes API key as an environment variable:

```bash
export GOOGLE_MAPS_API_KEY="your_api_key_here"
```

Or pass it directly to the client:

```python
client = GoogleRoutesClient(api_key="your_api_key_here")
```

## API Reference

### Core Classes

- **`GoogleRoutesClient`** - Main client for route optimization
- **`Location`** - Geographic coordinate representation
- **`Destination`** - Destination with metadata and constraints
- **`OptimizedSchedule`** - Complete optimized route result
- **`ScheduleStop`** - Individual stop in the optimized route

## Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Luis Ticas** - luis.ticas1@gmail.com

## Acknowledgments

- Built using Google Routes API for accurate traffic-aware routing
- Inspired by the need for efficient logistics and route planning solutions

## Requirements

- Python 3.8+
- Google Maps API key
- pydantic>=2.0.0
- googlemaps>=4.10.0
- httpx>=0.24.0
