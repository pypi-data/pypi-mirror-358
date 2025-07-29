"""Pytest fixtures and helpers for testing the dem_camera module."""

import tempfile
from pathlib import Path
from typing import Generator

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

__all__ = [
    "dem_test_data_dir",
    "create_synthetic_dem",
]


@pytest.fixture(scope="session")
def dem_test_data_dir() -> Generator[Path, None, None]:
    """Creates a temporary directory to store synthetic DEM test files."""
    with tempfile.TemporaryDirectory() as temp_dir_str:
        yield Path(temp_dir_str)


def create_synthetic_dem(
    directory: Path,
    filename: str,
    *,
    width: int,
    height: int,
    top_left_lon: float,
    top_left_lat: float,
    cell_size: float,
    elevation: float,
    crs: str = "EPSG:4326",
) -> Path:
    """
    Creates a simple GeoTIFF file with a constant elevation value.

    Args:
        directory: The directory where the file will be saved.
        filename: The name of the TIFF file.
        width: The width of the raster in pixels.
        height: The height of the raster in pixels.
        top_left_lon: The longitude of the top-left corner.
        top_left_lat: The latitude of the top-left corner.
        cell_size: The size of each pixel in geographic degrees.
        elevation: The constant elevation value for all pixels.
        crs: The coordinate reference system.

    Returns:
        The path to the newly created GeoTIFF file.
    """
    file_path = directory / filename
    transform = from_origin(top_left_lon, top_left_lat, cell_size, cell_size)
    data = np.full((height, width), elevation, dtype=rasterio.float32)

    with rasterio.open(
        file_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=rasterio.float32,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(data, 1)

    return file_path 