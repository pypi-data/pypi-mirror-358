"""
datamintapi - Transitional Package

This package is deprecated and exists only to prevent name squatting.
Please use 'datamint' instead.

To migrate:
1. pip uninstall datamintapi
2. pip install datamint
3. Update your imports from 'import datamintapi' to 'import datamint'
"""

import warnings
import sys

# Show deprecation warning
warnings.warn(
    "The 'datamintapi' package is deprecated. Please use 'datamint' instead. "
    "To migrate: pip uninstall datamintapi && pip install datamint",
    DeprecationWarning,
    stacklevel=2
)

# Try to import and expose the real datamint package
try:
    import datamint
    # Re-export everything from datamint
    sys.modules[__name__] = datamint
except ImportError:
    raise ImportError(
        "The 'datamintapi' package is deprecated. "
        "Please install 'datamint' instead: pip install datamint"
    )

__version__ = "0.0"
__all__ = []
