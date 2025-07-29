"""I/O helpers for common geospatial data formats."""

from pathlib import Path
from typing import Any

import rasterio

__all__ = [
    "read_dem",
]


def read_dem(path: str | Path) -> Any:
    """Read a DEM (Digital Elevation Model) raster using rasterio.

    Parameters
    ----------
    path
        Path to a DEM GeoTIFF or similar supported raster file.
    Returns
    -------
    rasterio.DatasetReader
        Open dataset handle; caller is responsible for closing it when done.
    """
    dataset = rasterio.open(path)
    return dataset 