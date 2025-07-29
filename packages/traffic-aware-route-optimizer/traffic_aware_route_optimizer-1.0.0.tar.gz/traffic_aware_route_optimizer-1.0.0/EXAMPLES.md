# Examples

This directory contains usage examples for the Traffic-Aware Route Optimizer.

## Basic Usage

### Simple Route Optimization

```python
from route_planner import GoogleRoutesClient, Location, Destination

# Initialize the client
client = GoogleRoutesClient(api_key="YOUR_API_KEY")

# Define start location (e.g., warehouse or depot)
start = Location(lat=40.7128, lng=-74.0060)

# Define destinations to visit
destinations = [
    Destination(
        destination_id="customer_1",
        name="Customer A",
        address="123 Main St, New York, NY",
        lat=40.7589,
        lng=-73.9851,
        priority=1
    ),
    Destination(
        destination_id="customer_2", 
        name="Customer B",
        address="456 Broadway, New York, NY",
        lat=40.7831,
        lng=-73.9712,
        priority=2
    )
]

# Optimize the route
route = client.optimize_route(
    start_location=start,
    destinations=destinations
)

print(f"Optimized route with {len(route.stops)} stops")
print(f"Total distance: {route.total_drive_km:.2f} km")
print(f"Total driving time: {route.total_drive_minutes} minutes")
```

### Advanced Usage with Time Windows

```python
from route_planner import GoogleRoutesClient, Location, Destination
from datetime import datetime

client = GoogleRoutesClient(api_key="YOUR_API_KEY")

# Delivery route with time constraints
destinations = [
    Destination(
        destination_id="delivery_1",
        name="Morning Delivery",
        address="100 First Ave, New York, NY",
        lat=40.7282,
        lng=-73.9942,
        priority=1,
        time_window_start="08:00",
        time_window_end="12:00",
        categories=["priority", "morning"]
    ),
    Destination(
        destination_id="delivery_2",
        name="Afternoon Pickup", 
        address="200 Second Ave, New York, NY",
        lat=40.7324,
        lng=-73.9857,
        priority=2,
        time_window_start="13:00", 
        time_window_end="17:00",
        categories=["pickup", "afternoon"]
    )
]

# Optimize with custom work schedule
route = client.optimize_route(
    start_location=Location(lat=40.7488, lng=-73.9857),
    destinations=destinations,
    visit_duration_minutes=45,  # 45 minutes per stop
    work_start="07:00",
    work_end="19:00",
    break_duration_minutes=30
)

# Print detailed schedule
for stop in route.stops:
    print(f"Stop {stop.sequence_number}: {stop.destination.name}")
    print(f"  Address: {stop.destination.address}")
    print(f"  Arrival: {stop.arrival.strftime('%H:%M')}")
    print(f"  Departure: {stop.departure.strftime('%H:%M')}")
    print(f"  Drive time: {stop.drive_minutes} minutes")
    print(f"  Drive distance: {stop.drive_distance_km:.1f} km")
    print()
```

### Error Handling

```python
from route_planner import GoogleRoutesClient, GoogleRoutesError

try:
    client = GoogleRoutesClient(api_key="YOUR_API_KEY")
    route = client.optimize_route(
        start_location=start,
        destinations=destinations
    )
except GoogleRoutesError as e:
    print(f"Route optimization failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Use Cases

- **Delivery Route Optimization** - Optimize delivery routes for logistics companies
- **Service Technician Scheduling** - Plan service visits with time windows
- **Sales Territory Planning** - Optimize sales rep visits to clients
- **Field Service Management** - Route field workers efficiently
- **Emergency Response** - Plan emergency service routes
- **Tourism and Sightseeing** - Create optimized tour routes
