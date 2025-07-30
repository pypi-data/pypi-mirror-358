# datamintapi - Transitional Package

⚠️ **This package is deprecated and should not be used for new projects.**

## Purpose

This package exists for two reasons:
1. **Name Protection**: Prevent malicious name squatting of the `datamintapi` namespace
2. **Migration Aid**: Help existing users transition to the correct `datamint` package

## Migration Instructions

If you're currently using `datamintapi`, please migrate to `datamint`:

```bash
# Remove old package
pip uninstall datamintapi

# Install correct package
pip install datamint
```

Then update your code:

```python
# Old (deprecated)
import datamintapi

# New (correct)
import datamint
```

## About Datamint

- **Official Package**: https://pypi.org/project/datamint/
- **GitHub**: https://github.com/SonanceAI/datamint-python-api