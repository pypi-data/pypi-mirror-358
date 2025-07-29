# AGS (Advanced Geolocation Service)

A modular Python library focused on high-accuracy, extensible geolocation workflows.

## Installation
```bash
pip install AGS  # core only
# or, with the DEM + camera processing module
pip install AGS[dem_cam]
```

## Quick example
```python
import geo

# Use core helpers
lat, lon = 40.7128, -74.0060
utm_coords = geo.coords.to_utm(lat, lon)

# Use DEM + camera processing (feature extra)
from geo.dem_camera import locate_ground_point

result = locate_ground_point(
    spotter_llh=(lat, lon, altitude_m),
    azimuth_deg=315.0,       # Northwest bearing
    elevation_deg=-15.0,     # 15° below horizon
    dem_directory="/path/to/dems/"
)

print(f"Target: {result.lat}, {result.lon}")
print(f"Range: {result.range_m}m")
```

## Project structure
See `docs/architecture.md` for an overview of how modules plug into the `geo` namespace.

## License
Apache-2.0 