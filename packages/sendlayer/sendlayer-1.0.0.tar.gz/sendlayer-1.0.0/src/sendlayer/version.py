import os

_version_path = os.path.join(os.path.dirname(__file__), "VERSION")
try:
    with open(_version_path) as f:
        __version__ = f.read().strip()
except FileNotFoundError:
    raise RuntimeError("Unable to find version string.")