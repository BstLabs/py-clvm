"""
change default platform (AWS, GCP, AZURE)
"""


import json
from os import makedirs, path
from pathlib import Path
from typing import Any, Set, Union


def _get_supported_platforms() -> Set:
    return {"AWS", "GCP", "AZURE"}


def _get_cache_path():
    """returns the cache path"""
    return path.join(Path.home(), ".clvm", ".cache.json")


def _create_cache() -> None:
    """creates the cache directory and file if they doesn't exist"""
    makedirs(
        name=path.join(Path.home(), ".clvm"),
        mode=0o700,
        exist_ok=True,
    )
    with open(_get_cache_path(), "w", encoding="utf8") as cache:
        data = {"platform": "AWS"}
        json.dump(data, cache, indent=4)
    print("Cache file created!")


def _set_default_platform(platform: str) -> None:
    """sets the default platform"""
    if platform in _get_supported_platforms():
        with open(_get_cache_path(), "w", encoding="utf8") as cache:
            data = {}
            data["platform"] = f"{platform.upper()}"
            cache.seek(0)
            json.dump(data, cache, indent=4)
            cache.truncate()
        print(f"Default platform is {platform.upper()}")
    else:
        _unsupported_platform(platform)


def _default_platform(**kwargs) -> Union[str, Any]:
    """returns the default platform"""

    if not path.exists(_get_cache_path()):
        _create_cache()

    if "platform" in kwargs:
        _set_default_platform(kwargs["platform"].upper())
    elif "platform" not in kwargs:
        with open(_get_cache_path(), "r", encoding="utf-8") as cache:
            platform_ = json.load(cache)
        return platform_["platform"]
    platform_ = str(kwargs["platform"]).upper()
    if platform_ in _get_supported_platforms():
        return platform_.upper()
    else:
        _unsupported_platform(platform_)


def _unsupported_platform(platform: Union[str, None]) -> None:
    if platform:
        platform = platform.upper()
    print(
        "Unsupported platform!",
        f"{platform} is not in the supported platforms list",
        "Supported platforms are: AWS, GCP, AZURE",
        sep="\n",
    )


def plt(*platform: str, **kwargs: str) -> Union[str, None]:
    """
    change default platform (AWS, GCP, AZURE)

    Args:
        **platform (str): one of the 3 platforms (AWS, GCP, AZURE). Default is AWS.

    Returns:
        None
    """
    default_platform, supported_platforms = (
        _default_platform(**kwargs),
        _get_supported_platforms(),
    )
    if platform:
        platform_name = platform[0].upper()
    else:
        print(f"Default platform is {default_platform}")
        return

    if platform_name in supported_platforms:
        _set_default_platform(platform_name)
    else:
        _unsupported_platform(platform_name)
