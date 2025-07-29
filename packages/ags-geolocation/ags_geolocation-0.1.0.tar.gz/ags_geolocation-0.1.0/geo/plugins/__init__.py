"""Entry point for external plugins.

The `geo.plugins` entry-point group allows third-party packages to attach
additional functionality without modifying the core library.
"""

from importlib import metadata
from types import ModuleType
from typing import Dict, List

__all__ = [
    "discover",
]


_discovered: Dict[str, ModuleType] | None = None


def discover() -> Dict[str, ModuleType]:
    """Discover and import all registered plugins.

    Returns a mapping of plugin names to the imported modules.
    """
    global _discovered  # noqa: PLW0603
    if _discovered is not None:
        return _discovered

    _discovered = {}
    for entry_point in metadata.entry_points(group="geo.plugins"):
        try:
            module = entry_point.load()
        except Exception as exc:  # pragma: no cover – guard against bad plugins
            # Skip plugins that fail to import so core package still works.
            continue
        _discovered[entry_point.name] = module
    return _discovered 