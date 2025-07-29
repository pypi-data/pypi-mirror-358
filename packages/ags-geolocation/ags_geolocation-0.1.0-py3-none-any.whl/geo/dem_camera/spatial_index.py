"""A spatial index for efficiently finding which DEM file contains a given coordinate."""

from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from rtree.index import Index

from .models import WGS84Coordinate

__all__ = [
    "SpatialIndex",
]


class SpatialIndex:
    """A 2D spatial index using an R-tree for fast bounding box lookups."""

    def __init__(self) -> None:
        self._index = Index()
        self._file_map: List[Path] = []

    def build_from_paths(self, paths: Iterable[Tuple[Path, Tuple[float, float, float, float]]]) -> None:
        """
        Builds the index from an iterable of file paths and their bounding boxes.

        Args:
            paths: An iterable where each item is a tuple containing:
                   - A Path object for the file.
                   - A tuple representing the bounding box (left, bottom, right, top).
        """
        for i, (path, bounds) in enumerate(paths):
            self._file_map.append(path)
            self._index.insert(i, bounds)

    def find_path(self, coord: WGS84Coordinate) -> Optional[Path]:
        """
        Finds the file path that contains the given coordinate.

        Args:
            coord: The WGS84Coordinate to look up.

        Returns:
            The Path to the file containing the coordinate, or None if no file is found.
        """
        point = (coord.lon, coord.lat, coord.lon, coord.lat)
        try:
            match_id = next(self._index.intersection(point))
            return self._file_map[match_id]
        except StopIteration:
            return None
