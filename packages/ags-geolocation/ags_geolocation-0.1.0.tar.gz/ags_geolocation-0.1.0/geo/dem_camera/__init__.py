"""Combine Digital Elevation Model (DEM) data with camera imagery to extract
geospatial insights.

This sub-package exposes its public API via :pyobj:`processor`.  Internals are
kept private to allow us to evolve algorithms without breaking users.

Placeholder for the *DEM + Camera* feature module.

The implementation has been cleared pending a redesigned algorithm.  See
`PLAN.md` in this directory for the current development roadmap.
"""

# from . import processor  # removed during refactor
from .locator import locate_ground_point
from .models import GroundHit, HitQuality, WGS84Coordinate

__all__ = [
    "locate_ground_point",
    "GroundHit", 
    "HitQuality",
    "WGS84Coordinate",
] 