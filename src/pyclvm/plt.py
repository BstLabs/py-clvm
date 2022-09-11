"""
change default platform (AWS, GCP, AZURE)
"""


import json
import platform
import sys
from functools import wraps
from os import environ, getenv, makedirs, path
from pathlib import Path
from typing import Any, Set, Union


def _get_os() -> str:
    return platform.system()


def _get_supported_platforms() -> Set:
    return {"AWS", "GCP", "AZURE"}


def _get_cache_path():
    """returns the cache path"""
    return path.join(Path.home(), ".clvm", ".cache.json")


def _create_cache() -> None:
    """creates the cache directory and file if they don't exist"""
    makedirs(
        name=path.join(Path.home(), ".clvm"),
        mode=0o700,
        exist_ok=True,
    )
    with open(_get_cache_path(), "w", encoding="utf8") as cache:
        data = {"platform": "AWS"}
        json.dump(data, cache, indent=4)
    print("Cache file created!")


def check_cache_for_platform(func):
    # This is for preventing multiple cache file hit
    @wraps(func)
    def decorator(cloud_platform):
        if cloud_platform.upper() == getenv("CLVM_DEFAULT_PLATFORM"):
            return
        return func(cloud_platform)

    return decorator


@check_cache_for_platform
def _set_default_platform(cloud_platform: str) -> None:
    """sets the default platform"""
    if cloud_platform in _get_supported_platforms():
        with open(_get_cache_path(), "w", encoding="utf8") as cache:
            data = {"platform": f"{cloud_platform.upper()}"}
            cache.seek(0)
            json.dump(data, cache, indent=4)
            cache.truncate()
            environ["CLVM_DEFAULT_PLATFORM"] = cloud_platform.upper()
        print(f"Default platform is {cloud_platform.upper()}")
    else:
        _unsupported_platform(cloud_platform)


def _default_platform(**kwargs) -> Union[str, Any]:
    """returns the default platform"""

    if not path.exists(_get_cache_path()):
        _create_cache()

    if "platform" in kwargs:
        _set_default_platform(kwargs["platform"].upper())
    elif "platform" not in kwargs:
        with open(_get_cache_path(), "r", encoding="utf-8") as cache:
            cloud_platform = json.load(cache)
        return cloud_platform["platform"]
    cloud_platform = str(kwargs["platform"]).upper()
    if cloud_platform in _get_supported_platforms():
        return cloud_platform
    _unsupported_platform(cloud_platform)


def _unsupported_platform(cloud_platform: Union[str, None]) -> None:
    if cloud_platform:
        cloud_platform = cloud_platform.upper()
    print(
        "Unsupported platform!",
        f"{cloud_platform} is not in the supported platforms list",
        "Supported platforms are: AWS, GCP, AZURE",
        sep="\n",
    )
    sys.exit(-1)


def plt(*cloud_platform: str, **kwargs: str) -> Union[str, None]:
    """
    change default platform (AWS, GCP, AZURE)

    Args:
        **cloud_platform (str): one of the 3 platforms (AWS, GCP, AZURE). Default is AWS.

    Returns:
        None
    """
    default_platform, supported_platforms = (
        _default_platform(**kwargs),
        _get_supported_platforms(),
    )
    if cloud_platform:
        platform_name = cloud_platform[0].upper()
    else:
        print(f"Default platform is {default_platform}")
        return

    if platform_name in supported_platforms:
        _set_default_platform(platform_name)
    else:
        _unsupported_platform(platform_name)
