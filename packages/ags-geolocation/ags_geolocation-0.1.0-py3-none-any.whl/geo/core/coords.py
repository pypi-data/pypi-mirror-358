"""Coordinate reference system helpers."""

from typing import Tuple

from pyproj import Transformer

__all__ = [
    "to_utm",
]


_transformers_cache: dict[Tuple[int, int], Transformer] = {}


def _get_transformer(epsg_from: int, epsg_to: int) -> Transformer:
    key = (epsg_from, epsg_to)
    if key not in _transformers_cache:
        _transformers_cache[key] = Transformer.from_crs(epsg_from, epsg_to, always_xy=True)
    return _transformers_cache[key]


def to_utm(lat: float, lon: float) -> Tuple[float, float]:
    """Convert WGS84 lat/lon to UTM coordinates (easting, northing).

    This simple helper chooses the UTM zone based on longitude.  For rigorous
    production use you may need to handle special cases (e.g. Norway, Svalbard).
    """
    zone_number = int((lon + 180) / 6) + 1
    epsg_to = 32600 + zone_number  # WGS84 northern hemisphere
    transformer = _get_transformer(4326, epsg_to)
    x, y = transformer.transform(lon, lat)
    return x, y 