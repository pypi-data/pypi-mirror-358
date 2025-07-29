"""Advanced Geolocation Service root package.

This package is designed to act as a single import namespace (``geo``) whose
sub-packages represent feature modules.  Only the public API of each feature
is re-exported here to keep the surface area deliberate and stable.
"""

from importlib import metadata

# Import public faces of core utilities
from .core import coords, io  # noqa: F401 (re-exported)

# Import first feature module public API under a concise alias
# from .dem_camera import processor as dem_cam  # removed during refactor

__all__ = [
    "coords",
    "io",
    "__version__",
]

try:
    __version__ = metadata.version(__name__)
except metadata.PackageNotFoundError:
    # Local dev editable install or package not yet built.
    __version__ = "0.0.0" 