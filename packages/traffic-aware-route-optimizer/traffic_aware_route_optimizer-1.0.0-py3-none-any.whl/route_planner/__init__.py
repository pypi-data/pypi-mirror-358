"""
Traffic-Aware Route Optimizer Package
"""

from .google_routes_client import GoogleRoutesClient, GoogleRoutesError
from .schemas import (
    Location, Destination, OptimizedSchedule, ScheduleStop,
    Break, RouteOptimizeInput
)

__version__ = "1.0.0"
__all__ = [
    "GoogleRoutesClient",
    "GoogleRoutesError", 
    "Location",
    "Destination",
    "OptimizedSchedule",
    "ScheduleStop",
    "Break",
    "RouteOptimizeInput"
]