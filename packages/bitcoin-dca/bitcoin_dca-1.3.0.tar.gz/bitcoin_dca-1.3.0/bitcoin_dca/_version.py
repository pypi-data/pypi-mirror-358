"""Version information for bitcoin-dca package."""

try:
    from importlib.metadata import version
    __version__ = version("bitcoin-dca")
except ImportError:
    # Fallback for Python < 3.8
    from importlib_metadata import version
    __version__ = version("bitcoin-dca")