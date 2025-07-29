"""Shared data models for the DEM + Camera module."""
from enum import Enum
from pydantic import BaseModel, Field

__all__ = [
    "WGS84Coordinate",
    "GroundHit",
    "HitQuality",
]


class HitQuality(str, Enum):
    """Quality assessment of the ground intersection."""
    DIRECT = "direct"        # Clean intersection with terrain
    GRAZING = "grazing"      # Ray grazes terrain at very shallow angle
    OFF_GRID = "off_grid"    # Ray does not intersect any DEM data


class WGS84Coordinate(BaseModel):
    """A geographic coordinate in the WGS-84 datum."""

    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees.")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees.")


class GroundHit(BaseModel):
    """Result of a ground intersection calculation."""
    
    lat: float = Field(..., description="Latitude of ground intersection (WGS-84)")
    lon: float = Field(..., description="Longitude of ground intersection (WGS-84)")
    range_m: float = Field(..., ge=0.0, description="3D slant distance from spotter to target (meters)")
    dem_elev_m: float = Field(..., description="DEM elevation at intersection point (meters)")
    quality: HitQuality = Field(..., description="Quality assessment of the intersection")
