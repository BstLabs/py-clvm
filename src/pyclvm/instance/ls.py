from typing import Dict, Final

from rich import print

from ._mapping import InstanceMapping

_STATE_COLOR: Final[Dict[int, str]] = {
    0: "bright_yellow",
    16: "bright_green",
    32: "yellow",
    48: "red",
    64: "bright_magneta",
    80: "bright_red",
}


def ls(**kwargs: str) -> None:
    """
    list vm instances

    Args:
        **kwargs (str): (optional) classifiers, at the moment, profile name, instance state, name patterns

    Returns:
        None

    """
    instances = InstanceMapping(**kwargs)
    for name, instance in instances.items():
        print(f"{name} - [{_STATE_COLOR[instance.state.Code]}]{instance.state.Name}")
