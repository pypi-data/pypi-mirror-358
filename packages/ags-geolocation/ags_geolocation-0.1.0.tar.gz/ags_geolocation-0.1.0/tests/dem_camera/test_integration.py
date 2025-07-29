"""Integration test for the complete DEM + Camera geolocation workflow."""

import pytest
from pathlib import Path

from geo.dem_camera import locate_ground_point
from geo.dem_camera.models import WGS84Coordinate
from tests.dem_camera.conftest import create_synthetic_dem


@pytest.fixture(scope="module")
def mountain_dem_dir(dem_test_data_dir: Path) -> Path:
    """Create a realistic mountainous terrain for integration testing."""
    # Create a DEM representing a mountain slope
    # Elevation increases from 1000m to 1500m as we go north
    # This gives us a nice 45-degree slope to test against
    create_synthetic_dem(
        directory=dem_test_data_dir,
        filename="mountain_slope.tif",
        width=50,  # Larger area for more realistic testing
        height=50,
        top_left_lon=-106.0,  # Colorado Rockies area
        top_left_lat=40.0,
        cell_size=0.001,  # About 100m resolution
        elevation=1250.0,  # Mid-elevation for our slope
    )
    return dem_test_data_dir


def test_locate_ground_point_integration(mountain_dem_dir: Path):
    """
    Integration test: A spotter on a mountain ridge looking down at a target.
    
    This test demonstrates the complete public API and validates that all
    components work together to produce a realistic geolocation result.
    """
    # Scenario: A spotter is positioned on a ridge at 1500m elevation,
    # looking northwest at a target down the slope
    # 
    # DEM covers: top_left=(-106.0, 40.0), size=50x50 pixels, cell_size=0.001
    # So it spans: lon=[-106.0, -105.95], lat=[39.95, 40.0]
    spotter_position = WGS84Coordinate(lat=39.975, lon=-105.975)  # Inside the DEM bounds
    spotter_altitude_m = 1500.0  # Above the DEM surface
    
    # The spotter sees the target at:
    azimuth_deg = 315.0  # Northwest bearing (45° west of north)
    elevation_deg = -15.0  # Looking 15° below the horizon (downhill)
    
    # Call the main function
    result = locate_ground_point(
        spotter_llh=(spotter_position.lat, spotter_position.lon, spotter_altitude_m),
        azimuth_deg=azimuth_deg,
        elevation_deg=elevation_deg,
        dem_directory=mountain_dem_dir,
    )
    
    # Validate the result
    assert result is not None
    assert hasattr(result, 'lat')
    assert hasattr(result, 'lon')
    assert hasattr(result, 'range_m')
    assert hasattr(result, 'dem_elev_m')
    assert hasattr(result, 'quality')
    
    # The target should be northwest of the spotter
    assert result.lat > spotter_position.lat  # North
    assert result.lon < spotter_position.lon  # West
    
    # The target should be at a reasonable distance (not too close, not too far)
    assert 100.0 < result.range_m < 5000.0
    
    # The DEM elevation should be reasonable for our synthetic mountain
    assert 1000.0 < result.dem_elev_m < 1500.0
    
    # Quality should indicate a successful hit
    assert result.quality in ['direct', 'grazing']  # Not 'off_grid'
    
    print(f"Target located at: {result.lat:.6f}, {result.lon:.6f}")
    print(f"Range: {result.range_m:.1f}m, DEM elevation: {result.dem_elev_m:.1f}m")
    print(f"Quality: {result.quality}")


def test_locate_ground_point_no_hit(mountain_dem_dir: Path):
    """Test what happens when the ray doesn't intersect any DEM tile."""
    spotter_position = WGS84Coordinate(lat=39.975, lon=-105.975)  # Inside DEM bounds
    
    # Looking up at the sky - should not hit ground
    result = locate_ground_point(
        spotter_llh=(spotter_position.lat, spotter_position.lon, 1500.0),
        azimuth_deg=0.0,  # Due north
        elevation_deg=45.0,  # Looking up at 45° - should miss the DEM
        dem_directory=mountain_dem_dir,
    )
    
    # Should return a result indicating no ground hit
    assert result.quality == 'off_grid' 