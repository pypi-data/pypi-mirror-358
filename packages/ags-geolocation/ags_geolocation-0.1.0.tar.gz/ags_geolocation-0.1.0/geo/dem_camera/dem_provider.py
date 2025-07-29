"""Provides a high-level interface for querying elevation data from a directory of DEM files."""

import logging
from pathlib import Path
from typing import Optional

import rasterio
from lru import LRU

from .models import WGS84Coordinate
from .spatial_index import SpatialIndex

__all__ = [
    "DEMProvider",
    "DEMTileNotFoundError",
]

logger = logging.getLogger(__name__)


class DEMTileNotFoundError(Exception):
    """Raised when no DEM tile can be found for a given coordinate."""

    pass


class DEMProvider:
    """
    Manages a collection of DEM files and provides an interface to query elevation
    at specific geographic coordinates.
    """

    def __init__(self, dem_directory: str | Path, *, file_handle_cache_size: int = 10):
        """
        Initializes the provider by scanning a directory and building a spatial index.

        Args:
            dem_directory: Path to the directory containing DEM files (e.g., GeoTIFFs).
            file_handle_cache_size: The number of open file handles to cache in memory.
        """
        self._directory = Path(dem_directory)
        self._index = SpatialIndex()
        self._file_handles = LRU(file_handle_cache_size)

        self._build_index()

    def _build_index(self):
        """Scans the directory for DEMs and builds the spatial index."""
        logger.info(f"Scanning DEM directory: {self._directory}")
        dem_paths = list(self._directory.glob("*.tif"))

        def path_to_bounds_gen():
            for path in dem_paths:
                try:
                    with rasterio.open(path) as src:
                        yield path, src.bounds
                except rasterio.errors.RasterioIOError:
                    logger.warning(f"Could not read bounds from {path}, skipping.")

        self._index.build_from_paths(path_to_bounds_gen())
        logger.info(f"Built spatial index with {len(dem_paths)} DEM files.")

    def get_elevation(self, coord: WGS84Coordinate) -> Optional[float]:
        """
        Gets the elevation at a specific coordinate.

        Args:
            coord: The coordinate to query.

        Returns:
            The elevation in meters as a float, or None if the coordinate is
            outside the data bounds of the DEM tile.

        Raises:
            DEMTileNotFoundError: If no DEM tile in the directory contains the coordinate.
        """
        tile_path = self._index.find_path(coord)
        if not tile_path:
            raise DEMTileNotFoundError(f"No DEM tile found for coordinate {coord}")

        if tile_path not in self._file_handles:
            self._file_handles[tile_path] = rasterio.open(tile_path)

        dataset = self._file_handles[tile_path]
        value = next(dataset.sample([(coord.lon, coord.lat)]))[0]

        # rasterio returns values from the underlying nodata range if a point
        # is outside the data region. We treat this as "no value".
        if dataset.nodatavals and dataset.nodatavals[0] is not None and value <= dataset.nodatavals[0]:
            return None

        return float(value)

    def close(self):
        """Closes all cached file handles."""
        for handle in self._file_handles.values():
            handle.close()
        self._file_handles.clear()

    def __del__(self):
        """Ensures all cached file handles are closed when the object is destroyed."""
        self.close()
