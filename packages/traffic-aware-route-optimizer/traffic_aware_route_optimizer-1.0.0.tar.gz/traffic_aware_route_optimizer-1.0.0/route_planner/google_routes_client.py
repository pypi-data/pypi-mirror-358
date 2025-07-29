"""
Google Routes API Client for traffic-aware route optimization.
Handles multi-waypoint optimization with time windows and traffic.
"""

import os
import asyncio
import logging
import json
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional, Tuple, Any
import googlemaps
import httpx
from googlemaps.exceptions import ApiError, Timeout, TransportError

from .schemas import (
    Destination, Location, OptimizedSchedule, ScheduleStop, 
    Break, RouteOptimizeInput
)

logger = logging.getLogger(__name__)


class GoogleRoutesError(Exception):
    """Custom exception for Google Routes API errors."""
    pass


class GoogleRoutesClient:
    """
    Client for Google Routes API with healthcare rep optimization features.
    
    Features:
    - Multi-waypoint route optimization
    - Real-time traffic consideration
    - Time window constraints
    - Lunch break insertion
    - Distance and duration calculations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Routes client.
        
        Args:
            api_key: Google Maps API key (defaults to env variable)
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API key is required")
        
        # Keep googlemaps client for health checks and geocoding
        self.client = googlemaps.Client(key=self.api_key)
        
        # HTTP client for Routes API v2
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "X-Goog-Api-Key": self.api_key,
                "Content-Type": "application/json",
                "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs,routes.optimizedIntermediateWaypointIndex"
            }
        )
        
        logger.info("GoogleRoutesClient initialized with Routes API v2")

    async def optimize_route(self, request: RouteOptimizeInput) -> OptimizedSchedule:
        """
        Optimize route for healthcare rep visits.
        
        Args:
            request: Route optimization parameters
            
        Returns:
            OptimizedSchedule with optimized stops and timing
            
        Raises:
            GoogleRoutesError: If optimization fails
        """
        try:
            # Parse work times
            work_start_time = time.fromisoformat(request.work_start)
            work_end_time = time.fromisoformat(request.work_end)
            
            # Filter destinations by time windows
            feasible_destinations = self._filter_feasible_destinations(
                request.destinations, work_start_time, work_end_time, request.visit_duration_minutes
            )
            
            if not feasible_destinations:
                raise GoogleRoutesError("No destinations can be visited within time constraints")
            
            # Get distance matrix for initial sorting
            provider_distances = await self._get_provider_distances(
                request.rep_location, feasible_destinations
            )
            
            # Sort by rating (priority) then distance
            sorted_destinations = self._sort_destinations_by_priority(
                feasible_destinations, provider_distances
            )
            
            # Optimize route with Google Routes API
            optimized_waypoints = await self._optimize_waypoint_order(
                request.rep_location, sorted_destinations
            )
            
            # Generate schedule with timing
            schedule = await self._generate_schedule_with_timing(
                request, optimized_waypoints, work_start_time, work_end_time
            )
            
            return schedule
            
        except Exception as e:
            logger.error(f"Route optimization failed: {e}")
            if isinstance(e, GoogleRoutesError):
                raise
            raise GoogleRoutesError(f"Optimization failed: {str(e)}")

    def _filter_feasible_destinations(
        self, 
        destinations: List[Destination], 
        work_start: time, 
        work_end: time,
        visit_duration_minutes: int
    ) -> List[Destination]:
        """Filter destinations that can be visited within their time windows."""
        feasible = []
        
        for provider in destinations:
            # If no time window specified, provider is always feasible
            if not provider.time_window_start or not provider.time_window_end:
                feasible.append(provider)
                continue
            
            # Parse provider time window
            provider_start = time.fromisoformat(provider.time_window_start)
            provider_end = time.fromisoformat(provider.time_window_end)
            
            # Check if provider window overlaps with work hours
            # and allows for minimum visit duration
            effective_start = max(work_start, provider_start)
            effective_end = min(work_end, provider_end)
            
            # Calculate available time in minutes
            start_minutes = effective_start.hour * 60 + effective_start.minute
            end_minutes = effective_end.hour * 60 + effective_end.minute
            available_minutes = end_minutes - start_minutes
            
            if available_minutes >= visit_duration_minutes:
                feasible.append(provider)
                logger.debug(f"Destination {provider.name} is feasible: {available_minutes}min available")
            else:
                logger.debug(f"Destination {provider.name} excluded: only {available_minutes}min available")
        
        logger.info(f"Filtered {len(feasible)}/{len(destinations)} feasible destinations")
        return feasible

    async def _get_provider_distances(
        self, 
        rep_location: Location, 
        destinations: List[Destination]
    ) -> Dict[str, float]:
        """Get straight-line distances from rep to each provider."""
        distances = {}
        
        for provider in destinations:
            # Calculate straight-line distance using Haversine formula
            distance_km = self._calculate_haversine_distance(
                rep_location.lat, rep_location.lng,
                provider.lat, provider.lng
            )
            distances[provider.provider_id] = distance_km
        
        return distances

    def _calculate_haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate straight-line distance between two points in kilometers."""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in kilometers
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c

    def _sort_destinations_by_priority(
        self, 
        destinations: List[Destination], 
        distances: Dict[str, float]
    ) -> List[Destination]:
        """Sort destinations by rating (priority) then distance."""
        return sorted(
            destinations,
            key=lambda p: (p.rating, distances.get(p.provider_id, float('inf')))
        )

    async def _optimize_waypoint_order(
        self, 
        rep_location: Location, 
        destinations: List[Destination]
    ) -> List[Destination]:
        """
        Use Google Routes API v2 to optimize waypoint order.
        Falls back to priority order if API fails.
        """
        if len(destinations) <= 1:
            return destinations
        
        try:
            # Prepare request for Routes API v2
            request_payload = {
                "origin": {
                    "location": {
                        "latLng": {
                            "latitude": rep_location.lat,
                            "longitude": rep_location.lng
                        }
                    }
                },
                "destination": {
                    "location": {
                        "latLng": {
                            "latitude": rep_location.lat,
                            "longitude": rep_location.lng
                        }
                    }
                },
                "intermediates": [
                    {
                        "location": {
                            "latLng": {
                                "latitude": provider.lat,
                                "longitude": provider.lng
                            }
                        }
                    }
                    for provider in destinations
                ],
                "travelMode": "DRIVE",
                "routingPreference": "TRAFFIC_AWARE",  # ✅ Compatible with optimizeWaypointOrder
                "computeAlternativeRoutes": False,
                "optimizeWaypointOrder": True
            }
            
            # Call Google Routes API v2
            url = "https://routes.googleapis.com/directions/v2:computeRoutes"
            
            response = await self.http_client.post(url, json=request_payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "routes" in result and len(result["routes"]) > 0:
                route = result["routes"][0]
                
                # Extract optimized waypoint order
                if "optimizedIntermediateWaypointIndex" in route:
                    waypoint_order = route["optimizedIntermediateWaypointIndex"]
                    optimized_destinations = [destinations[i] for i in waypoint_order]
                    
                    logger.info(f"Routes API v2 optimized order: {[p.name for p in optimized_destinations]}")
                    return optimized_destinations
                else:
                    logger.warning("No optimized waypoint order returned from Routes API v2")
            
        except Exception as e:
            logger.warning(f"Routes API v2 optimization failed, using priority order: {e}")
        
        # Fallback to priority-based order
        logger.info("Using priority-based order as fallback")
        return destinations

    async def _get_route_info(
        self, 
        origin: Location, 
        destination: Location
    ) -> Tuple[float, int]:
        """
        Get accurate route distance and duration using Routes API v2.
        
        Args:
            origin: Starting location
            destination: Ending location
            
        Returns:
            Tuple of (distance_km, duration_minutes)
        """
        try:
            request_payload = {
                "origin": {
                    "location": {
                        "latLng": {
                            "latitude": origin.lat,
                            "longitude": origin.lng
                        }
                    }
                },
                "destination": {
                    "location": {
                        "latLng": {
                            "latitude": destination.lat,
                            "longitude": destination.lng
                        }
                    }
                },
                "travelMode": "DRIVE",
                "routingPreference": "TRAFFIC_AWARE",  # ✅ Uses live traffic data for accurate timing
                "computeAlternativeRoutes": False
            }
            
            url = "https://routes.googleapis.com/directions/v2:computeRoutes"
            
            # Call Google Routes API v2 with live traffic data
            response = await self.http_client.post(url, json=request_payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "routes" in result and len(result["routes"]) > 0:
                route = result["routes"][0]
                
                # Extract distance and duration
                distance_meters = route.get("distanceMeters", 0)
                duration_seconds = 0
                
                if "duration" in route:
                    duration_str = route["duration"].rstrip('s')
                    duration_seconds = int(float(duration_str))
                
                distance_km = distance_meters / 1000.0
                duration_minutes = max(5, int(duration_seconds / 60))  # Minimum 5 minutes
                
                return distance_km, duration_minutes
                
        except Exception as e:
            logger.warning(f"Routes API v2 route info failed, using fallback calculation: {e}")
        
        # Fallback to Haversine distance calculation
        distance_km = self._calculate_haversine_distance(
            origin.lat, origin.lng, destination.lat, destination.lng
        )
        duration_minutes = max(5, int(distance_km * 2))  # Estimate: 2 minutes per km
        
        return distance_km, duration_minutes

    async def _generate_schedule_with_timing(
        self,
        request: RouteOptimizeInput,
        destinations: List[Destination],
        work_start: time,
        work_end: time
    ) -> OptimizedSchedule:
        """Generate complete schedule with arrival/departure times and lunch break."""
        today = datetime.now().date()
        
        # Define lunch break times with 15-minute buffer
        lunch_start_time = time(12, 0)  # 12:00 PM (official lunch start)
        lunch_buffer_time = time(12, 15)  # 12:15 PM (15-minute buffer for visits)
        lunch_end_time = time(13, 0)   # 1:00 PM (after 60 min lunch)
        
        # Define end-of-day with 15-minute buffer
        work_end_buffer = time(17, 15)  # 5:15 PM (15-minute buffer for end of day)
        
        # Create lunch break
        lunch_break = Break(
            start=datetime.combine(today, lunch_start_time),
            end=datetime.combine(today, lunch_end_time),
            location="Lunch break (12:00 PM - 1:00 PM, with 15-min buffer until 12:15 PM)"
        )
        
        logger.info(f"🕒 Using 15-minute buffers: Pre-lunch until 12:15 PM, End-of-day until 5:15 PM")
        logger.info(f"🚗 Using Google Routes API v2 with live traffic data for accurate timing")
        
        # Phase 1: Schedule visits before lunch (08:00 - 12:15 with buffer)
        morning_stops, morning_excluded, morning_totals = await self._schedule_time_period(
            request, destinations, today, work_start, lunch_buffer_time, "morning (with 15-min buffer)"
        )
        
        # Phase 2: Schedule remaining visits after lunch (13:00 - 17:15 with buffer)
        remaining_destinations = [p for p in destinations if p.provider_id not in [s.provider.provider_id for s in morning_stops]]
        afternoon_stops, afternoon_excluded, afternoon_totals = await self._schedule_time_period(
            request, remaining_destinations, today, lunch_end_time, work_end_buffer, "afternoon (with 15-min buffer)",
            start_location=morning_stops[-1].provider if morning_stops else request.rep_location
        )
        
        # Combine results
        all_stops = morning_stops + afternoon_stops
        
        # Only include destinations that were excluded from BOTH periods
        scheduled_provider_ids = {s.provider.provider_id for s in all_stops}
        all_excluded = [pid for pid in afternoon_excluded if pid not in scheduled_provider_ids]
        
        total_drive_km = morning_totals[0] + afternoon_totals[0]
        total_drive_minutes = morning_totals[1] + afternoon_totals[1]
        
        # Update sequence numbers
        for i, stop in enumerate(all_stops):
            stop.sequence_number = i + 1
        
        logger.info(f"Scheduled {len(all_stops)} visits: {len(morning_stops)} before lunch (with 15-min buffer), {len(afternoon_stops)} after lunch")
        logger.info(f"Excluded {len(all_excluded)} destinations due to time constraints")
        
        return OptimizedSchedule(
            rep_id=request.rep_id,
            visit_date=today,
            stops=all_stops,
            total_drive_km=round(total_drive_km, 1),
            total_drive_minutes=total_drive_minutes,
            lunch_break=lunch_break,
            excluded_destinations=all_excluded
        )

    async def _schedule_time_period(
        self,
        request: RouteOptimizeInput,
        destinations: List[Destination],
        today: datetime.date,
        period_start: time,
        period_end: time,
        period_name: str,
        start_location: Optional[any] = None
    ) -> Tuple[List[ScheduleStop], List[str], Tuple[float, int]]:
        """Schedule visits within a specific time period, prioritizing by provider rating then minimizing drive time."""
        if start_location is None:
            current_location = request.rep_location
        else:
            # Extract location from provider or use as Location object
            if hasattr(start_location, 'lat') and hasattr(start_location, 'lng'):
                current_location = Location(lat=start_location.lat, lng=start_location.lng)
            else:
                current_location = request.rep_location
        
        current_time = datetime.combine(today, period_start)
        period_end_datetime = datetime.combine(today, period_end)
        
        stops = []
        excluded_destinations = []
        total_drive_km = 0.0
        total_drive_minutes = 0
        available_destinations = destinations.copy()  # Work with a copy to avoid modifying original
        
        logger.info(f"Scheduling {period_name} period: {period_start} - {period_end} with {len(destinations)} destinations")
        
        # Continue scheduling until no more visits can fit in this period
        while available_destinations:
            best_provider = None
            best_provider_data = None
            best_priority = -1  # Lower value = higher priority
            best_drive_time = float('inf')
            
            # Collect all feasible destinations for this time slot
            feasible_destinations = []
            
            for provider in available_destinations:
                # Get accurate drive time using Routes API v2
                provider_location = Location(lat=provider.lat, lng=provider.lng)
                drive_distance, drive_time_minutes = await self._get_route_info(
                    current_location, provider_location
                )
                
                # Calculate visit timing
                arrival_time = current_time + timedelta(minutes=drive_time_minutes)
                departure_time = arrival_time + timedelta(minutes=request.visit_duration_minutes)
                
                # Check if visit fits within this time period
                if departure_time > period_end_datetime:
                    continue
                
                # Check provider time window if specified
                if provider.time_window_start and provider.time_window_end:
                    provider_start = datetime.combine(today, time.fromisoformat(provider.time_window_start))
                    provider_end = datetime.combine(today, time.fromisoformat(provider.time_window_end))
                    
                    # Check if provider's window overlaps with this time period
                    period_start_datetime = datetime.combine(today, period_start)
                    if (provider_end < period_start_datetime or provider_start > period_end_datetime):
                        continue
                    
                    # Check if visit fits within provider's window
                    if arrival_time < provider_start or departure_time > provider_end:
                        continue
                
                # This provider can be scheduled - add to feasible list
                feasible_destinations.append({
                    'provider': provider,
                    'arrival_time': arrival_time,
                    'departure_time': departure_time,
                    'drive_time_minutes': drive_time_minutes,
                    'drive_distance': drive_distance,
                    'provider_location': provider_location
                })
            
            # Select best provider by priority (rating) first, then by minimum drive time
            for feasible_data in feasible_destinations:
                provider = feasible_data['provider']
                drive_time_minutes = feasible_data['drive_time_minutes']
                
                # Get provider priority (higher rating = higher priority = lower priority value)
                provider_priority = 6 - provider.rating  # Rating 5 -> priority 1, Rating 1 -> priority 5
                
                # Select best provider: highest priority (lowest priority value) first, then shortest drive time
                is_better = False
                if provider_priority < best_priority:
                    # Higher priority provider
                    is_better = True
                elif provider_priority == best_priority and drive_time_minutes < best_drive_time:
                    # Same priority, but shorter drive time
                    is_better = True
                
                if is_better:
                    best_priority = provider_priority
                    best_drive_time = drive_time_minutes
                    best_provider = provider
                    best_provider_data = feasible_data
            
            # If no provider can be scheduled, we're done with this period
            if best_provider is None:
                # Add remaining destinations to excluded list
                for provider in available_destinations:
                    excluded_destinations.append(provider.provider_id)
                    logger.info(f"Excluded {provider.name} from {period_name}: no available time slot")
                break
            
            # Schedule the best provider
            stop = ScheduleStop(
                provider=best_provider,
                arrival=best_provider_data['arrival_time'],
                departure=best_provider_data['departure_time'],
                drive_minutes=best_provider_data['drive_time_minutes'],
                drive_distance_km=best_provider_data['drive_distance'],
                sequence_number=len(stops) + 1  # Will be updated later
            )
            stops.append(stop)
            
            # Update totals
            total_drive_km += best_provider_data['drive_distance']
            total_drive_minutes += best_provider_data['drive_time_minutes']
            
            # Update current position and time for next visit
            current_location = best_provider_data['provider_location']
            current_time = best_provider_data['departure_time']
            
            # Remove scheduled provider from available list
            available_destinations.remove(best_provider)
            
            logger.info(f"Scheduled {best_provider.name} (rating: {best_provider.rating}) in {period_name} at {best_provider_data['arrival_time'].strftime('%H:%M')}-{best_provider_data['departure_time'].strftime('%H:%M')}, drive: {best_provider_data['drive_time_minutes']}min")
        
        return stops, excluded_destinations, (total_drive_km, total_drive_minutes)

    async def health_check(self) -> bool:
        """
        Check if Google Routes API is accessible.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Simple geocoding test
            result = await asyncio.to_thread(
                self.client.geocode,
                "Detroit, MI"
            )
            return len(result) > 0
        except Exception as e:
            logger.error(f"Google API health check failed: {e}")
            return False

    async def close(self):
        """Close the HTTP client."""
        if hasattr(self, 'http_client'):
            await self.http_client.aclose()
            
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()