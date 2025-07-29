"""Core ray-tracing algorithm for ground intersection using DEM data."""

import math
from pathlib import Path
from typing import Tuple

import pyproj

from .dem_provider import DEMProvider, DEMTileNotFoundError
from .models import GroundHit, HitQuality, WGS84Coordinate

__all__ = [
    "locate_ground_point",
]


def locate_ground_point(
    spotter_llh: Tuple[float, float, float],
    azimuth_deg: float,
    elevation_deg: float,
    dem_directory: str | Path,
    *,
    step_size_m: float = 10.0,
    max_range_m: float = 20000.0,
) -> GroundHit:
    """
    Locate where a sight-line from a spotter intersects the ground.
    
    Args:
        spotter_llh: Tuple of (latitude, longitude, altitude_meters) for the spotter
        azimuth_deg: Bearing in degrees clockwise from true north (0-360)
        elevation_deg: Elevation angle in degrees above horizon (negative = below)
        dem_directory: Path to directory containing DEM TIFF files
        step_size_m: Distance in meters between ray samples (smaller = more accurate)
        max_range_m: Maximum range to search before giving up
        
    Returns:
        GroundHit with intersection details and quality assessment
    """
    lat, lon, alt = spotter_llh
    
    # Initialize DEM provider
    dem_provider = DEMProvider(dem_directory)
    
    try:
        # Convert to local ENU coordinate system centered at spotter
        transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:4978", always_xy=True)
        spotter_ecef = transformer.transform(lon, lat, alt)
        
        # Build ENU transformer (East-North-Up) at spotter location
        enu_crs = pyproj.CRS.from_proj4(
            f"+proj=tmerc +lat_0={lat} +lon_0={lon} +k=1 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs"
        )
        to_enu = pyproj.Transformer.from_crs("EPSG:4326", enu_crs, always_xy=True)
        from_enu = pyproj.Transformer.from_crs(enu_crs, "EPSG:4326", always_xy=True)
        
        # Convert azimuth and elevation to unit vector in ENU frame
        # Azimuth: 0° = North, 90° = East
        # Convert to radians and adjust for ENU coordinate system
        az_rad = math.radians(azimuth_deg)
        el_rad = math.radians(elevation_deg)
        
        # Unit vector components in ENU frame
        # East component
        dx = math.sin(az_rad) * math.cos(el_rad)
        # North component  
        dy = math.cos(az_rad) * math.cos(el_rad)
        # Up component
        dz = math.sin(el_rad)
        
        # Ray marching: step along the ray until we hit ground
        current_range = 0.0
        
        while current_range < max_range_m:
            # Current position along ray in ENU coordinates
            enu_x = dx * current_range
            enu_y = dy * current_range
            enu_z = dz * current_range
            
            # Convert ENU position back to lat/lon for DEM lookup
            ray_lon, ray_lat = from_enu.transform(enu_x, enu_y)
            ray_coord = WGS84Coordinate(lat=ray_lat, lon=ray_lon)
            
            # Get ground elevation at this position
            try:
                dem_elevation = dem_provider.get_elevation(ray_coord)
                if dem_elevation is None:
                    # Outside DEM bounds, continue stepping
                    current_range += step_size_m
                    continue
                    
                # Current ray altitude (spotter altitude + vertical displacement)
                ray_altitude = alt + enu_z
                
                # Check if ray has intersected ground
                if ray_altitude <= dem_elevation:
                    # Hit! Calculate final result
                    quality = HitQuality.DIRECT
                    
                    # Binary search refinement for more precise intersection
                    # (Optional: could implement for sub-step accuracy)
                    
                    result = GroundHit(
                        lat=ray_lat,
                        lon=ray_lon,
                        range_m=current_range,
                        dem_elev_m=dem_elevation,
                        quality=quality,
                    )
                    
                    return result
                    
            except DEMTileNotFoundError:
                # No DEM coverage at this location, continue searching
                pass
            
            current_range += step_size_m
        
        # No intersection found within max range
        # Return a placeholder result indicating we went off-grid
        return GroundHit(
            lat=lat,  # Return spotter position as fallback
            lon=lon,
            range_m=max_range_m,
            dem_elev_m=0.0,
            quality=HitQuality.OFF_GRID,
        )
        
    finally:
        dem_provider.close() 