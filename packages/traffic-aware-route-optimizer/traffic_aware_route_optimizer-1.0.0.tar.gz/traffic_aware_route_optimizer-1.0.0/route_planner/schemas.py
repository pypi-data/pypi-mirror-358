"""
Pydantic schemas for Traffic-Aware Route Optimizer.
Data models for route optimization with traffic awareness.
"""

from datetime import datetime, time
from datetime import date as DateType
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Location(BaseModel):
    """Geographic location with latitude and longitude."""
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")


class Destination(BaseModel):
    """Destination information for route optimization."""
    destination_id: str = Field(..., description="Unique destination identifier")
    name: str = Field(..., description="Destination name")
    address: str = Field(..., description="Street address")
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")
    priority: int = Field(..., ge=1, le=5, description="Priority rating (1=urgent, 5=low)")
    categories: List[str] = Field(default_factory=list, description="Destination categories or tags")
    time_window_start: Optional[str] = Field(None, description="Available from time (HH:MM)")
    time_window_end: Optional[str] = Field(None, description="Available until time (HH:MM)")

    @field_validator('time_window_start', 'time_window_end')
    @classmethod
    def validate_time_format(cls, v):
        """Validate time format is HH:MM."""
        if v is not None:
            try:
                time.fromisoformat(v)
            except ValueError:
                raise ValueError('Time must be in HH:MM format')
        return v


class RouteOptimizeInput(BaseModel):
    """Input parameters for route optimization."""
    trip_id: str = Field(..., description="Unique trip identifier")
    start_location: Location = Field(..., description="Starting location")
    destinations: List[Destination] = Field(..., description="List of destinations to visit")
    visit_duration_minutes: int = Field(60, ge=15, le=240, description="Duration per visit")
    work_start: str = Field("08:00", description="Work day start time (HH:MM)")
    work_end: str = Field("17:00", description="Work day end time (HH:MM)")
    break_duration_minutes: int = Field(60, ge=30, le=120, description="Break duration")

    @field_validator('work_start', 'work_end')
    @classmethod
    def validate_work_time_format(cls, v):
        """Validate work time format is HH:MM."""
        try:
            time.fromisoformat(v)
        except ValueError:
            raise ValueError('Work time must be in HH:MM format')
        return v

    @field_validator('destinations')
    @classmethod
    def validate_destinations_not_empty(cls, v):
        """Ensure at least one destination is provided."""
        if not v:
            raise ValueError('At least one destination must be provided')
        return v


class ScheduleStop(BaseModel):
    """Individual stop in the optimized schedule."""
    destination: Destination = Field(..., description="Destination information")
    arrival: datetime = Field(..., description="Planned arrival time")
    departure: datetime = Field(..., description="Planned departure time")
    drive_minutes: int = Field(..., description="Drive time to this stop")
    drive_distance_km: float = Field(..., description="Drive distance to this stop")
    sequence_number: int = Field(..., description="Order in the route (1-based)")


class Break(BaseModel):
    """Break information."""
    start: datetime = Field(..., description="Break start time")
    end: datetime = Field(..., description="Break end time")
    location: Optional[str] = Field(None, description="Break location description")


class OptimizedSchedule(BaseModel):
    """Complete optimized schedule for a trip."""
    trip_id: str = Field(..., description="Trip identifier")
    visit_date: DateType = Field(..., description="Date of visits")
    stops: List[ScheduleStop] = Field(..., description="Ordered list of destination visits")
    total_drive_km: float = Field(..., description="Total driving distance")
    total_drive_minutes: int = Field(..., description="Total driving time")
    break_info: Break = Field(..., description="Break details")
    excluded_destinations: List[str] = Field(
        default_factory=list, 
        description="Destination IDs excluded due to time constraints"
    )


class RouteOptimizeResponse(BaseModel):
    """Response from route optimization."""
    success: bool = Field(..., description="Whether optimization succeeded")
    schedule: Optional[OptimizedSchedule] = Field(None, description="Optimized schedule if successful")
    quota_remaining: int = Field(..., description="Remaining daily quota")
    error: Optional[str] = Field(None, description="Error code if failed")
    message: Optional[str] = Field(None, description="Human-readable error message")


class QuotaStatus(BaseModel):
    """Quota usage status."""
    trip_id: str = Field(..., description="Trip identifier")
    date: DateType = Field(..., description="Date for quota tracking")
    used: int = Field(..., description="Number of optimizations used today")
    limit: int = Field(..., description="Daily limit")
    remaining: int = Field(..., description="Remaining optimizations")
    
    @classmethod
    def create(cls, trip_id: str, date: DateType, used: int, limit: int):
        """Create QuotaStatus with calculated remaining quota."""
        remaining = max(0, limit - used)
        return cls(
            trip_id=trip_id,
            date=date,
            used=used,
            limit=limit,
            remaining=remaining
        )


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(..., description="Check timestamp")
    server_info: Optional[dict] = Field(None, description="Server information and component health")