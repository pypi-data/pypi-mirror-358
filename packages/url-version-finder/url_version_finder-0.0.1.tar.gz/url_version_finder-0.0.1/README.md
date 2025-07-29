# url-version-finder

A minimal decorator to extract version information from a request URL — such as `v1`, `v1.2.3`, or `1.0.0` — and inject it into your Python function or view.

## Features

- Supports `v1`, `1.0`, `v2.5.3`, etc.
- Compatible with Django, FastAPI, Flask, and raw dict requests
- Automatically adds the version as a parameter to your decorated function

## Install

```bash
pip install url-version-finder
```

```python
from url_version_finder.decorators import with_version

@with_version
def my_view(request, version):
    print(f"API version: {version}") # "v1"

```