"""Tests for the DEMProvider class."""

import pytest
from pathlib import Path

from geo.dem_camera.dem_provider import DEMProvider, DEMTileNotFoundError
from geo.dem_camera.models import WGS84Coordinate
from tests.dem_camera.conftest import create_synthetic_dem


@pytest.fixture(scope="module")
def populated_dem_dir(dem_test_data_dir: Path) -> Path:
    """A fixture that creates a directory with two synthetic DEMs for testing."""
    # Tile 1: Covers a small area around (lon=-74.0, lat=40.0) with elevation 100m
    create_synthetic_dem(
        directory=dem_test_data_dir,
        filename="tile1_100m.tif",
        width=10,
        height=10,
        top_left_lon=-74.0,
        top_left_lat=40.0,
        cell_size=0.001,
        elevation=100.0,
    )
    # Tile 2: Covers a small area around (lon=151.0, lat=-33.0) with elevation 200m
    create_synthetic_dem(
        directory=dem_test_data_dir,
        filename="tile2_200m.tif",
        width=10,
        height=10,
        top_left_lon=151.0,
        top_left_lat=-33.0,
        cell_size=0.001,
        elevation=200.0,
    )
    return dem_test_data_dir


def test_dem_provider_initialization(populated_dem_dir: Path):
    """Verify that the provider initializes and builds its index correctly."""
    provider = DEMProvider(populated_dem_dir)
    # 2 files should be found and indexed
    assert len(provider._index._file_map) == 2
    provider.close()


def test_get_elevation_from_correct_tiles(populated_dem_dir: Path):
    """Verify that the provider can query elevations from the correct tiles."""
    provider = DEMProvider(populated_dem_dir)

    # Coordinate within the first tile
    coord1 = WGS84Coordinate(lat=39.995, lon=-73.995)
    elevation1 = provider.get_elevation(coord1)
    assert elevation1 == pytest.approx(100.0)

    # Coordinate within the second tile
    coord2 = WGS84Coordinate(lat=-33.005, lon=151.005)
    elevation2 = provider.get_elevation(coord2)
    assert elevation2 == pytest.approx(200.0)
    
    provider.close()


def test_get_elevation_outside_all_tiles(populated_dem_dir: Path):
    """Verify that the provider raises an error for a coordinate outside all tiles."""
    provider = DEMProvider(populated_dem_dir)
    
    # Coordinate far from any tile
    coord_outside = WGS84Coordinate(lat=0, lon=0)
    
    with pytest.raises(DEMTileNotFoundError):
        provider.get_elevation(coord_outside)
    
    provider.close()


def test_lru_cache_for_file_handles(populated_dem_dir: Path):
    """Verify that file handles are cached."""
    # Cache size of 1 to easily test eviction
    provider = DEMProvider(populated_dem_dir, file_handle_cache_size=1)
    
    # Access first tile
    coord1 = WGS84Coordinate(lat=39.995, lon=-73.995)
    provider.get_elevation(coord1)
    assert len(provider._file_handles) == 1
    first_handle_path = provider._index.find_path(coord1)
    assert first_handle_path in provider._file_handles

    # Access second tile, which should evict the first
    coord2 = WGS84Coordinate(lat=-33.005, lon=151.005)
    provider.get_elevation(coord2)
    assert len(provider._file_handles) == 1
    second_handle_path = provider._index.find_path(coord2)
    assert second_handle_path in provider._file_handles
    assert first_handle_path not in provider._file_handles
    
    provider.close() 