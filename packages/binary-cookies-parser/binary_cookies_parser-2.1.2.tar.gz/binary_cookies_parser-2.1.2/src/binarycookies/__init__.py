import warnings

DEPRECATION_MESSAGE ="The package 'binary-cookies-parser' is deprecated and has been renamed to 'binarycookies'. Please install the new package instead: pip install binarycookies"

warnings.warn(
    DEPRECATION_MESSAGE,
    DeprecationWarning,
    stacklevel=2,
)

from binarycookies._deserialize import load, loads
from binarycookies._serialize import dump, dumps

__all__ = ["dump", "dumps", "load", "loads"]
