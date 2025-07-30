from importlib.metadata import PackageNotFoundError, version

from dgcore.helpers import get_logger

LOG = get_logger("root")
try:
    __version__ = version("codeenigma")
except PackageNotFoundError:
    try:
        import tomllib

        with open("pyproject.toml", "rb") as f:
            content = tomllib.load(f)
            __version__ = content["tool"]["poetry"]["version"]
    except FileNotFoundError:
        __version__ = "undefined"
