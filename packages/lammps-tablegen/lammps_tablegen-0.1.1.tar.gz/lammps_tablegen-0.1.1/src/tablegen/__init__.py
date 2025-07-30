from importlib.metadata import version as _v

__all__ = ["__version__"]
__version__ = _v(__name__)
