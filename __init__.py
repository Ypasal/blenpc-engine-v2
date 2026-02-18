"""blenpc - Procedural Building Generator for Blender 5.0"""

__version__ = "5.0.1"

# Avoid relative imports at the root level if not being run as a package
try:
    from . import mf_v5
    from . import atoms
    from . import engine
except ImportError:
    import mf_v5
    import atoms
    import engine

__all__ = ["mf_v5", "atoms", "engine"]
