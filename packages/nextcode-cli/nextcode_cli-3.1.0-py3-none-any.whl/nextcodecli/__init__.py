import os
import nextcode
import importlib.metadata


try:
    __version__ = importlib.metadata.version("nextcode-cli")
except importlib.metadata.PackageNotFoundError:
    __version__ = '0.1.0-dev'


def get_version_string():
    format_str = "nextcode-cli/{version} nextcode-sdk/{sdk_version}"
    version_msg = format_str.format(
        version=__version__, sdk_version=nextcode.__version__
    )
    return version_msg
