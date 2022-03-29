from collections.abc import Mapping
from typing import Dict, Final, Generator, List, Optional, Tuple, Type

from _common.session import Session, get_session

Instance = Type["Instance"]  # cannot import from boto3
_FILTERS: Final[Dict[str, str]] = dict(states="instance-state-name", names="tag:Name")


class InstanceMapping(Mapping):
    def __init__(self, **kwargs: str):
        self._session = get_session(kwargs)
        self._client = self._session.client("ec2")
        self._resource = self._session.resource("ec2")
        self._filters = self._build_filters(kwargs)

    @property
    def session(self) -> Session:
        return self._session

    def _build_filters(self, kwargs: dict) -> dict:
        filters = []
        for name, values in kwargs.items():
            if name in _FILTERS:
                filters.append(
                    dict(
                        Name=_FILTERS[name],
                        Values=values.split(",") if str == type(values) else values,
                    )
                )
        return dict(Filters=filters) if filters else dict()

    def _get_instances(
        self, filters: Optional[List[Dict[str, List[str]]]] = None
    ) -> Generator[Instance, None, None]:
        instances = self._client.describe_instances(
            **(filters if filters else self._filters)
        )
        for reservation in instances.Reservations:
            for instance in reservation.Instances:
                yield self._resource.Instance(instance.InstanceId)

    def __getitem__(self, instance_name: str) -> Instance:
        try:
            return next(
                self._get_instances(self._build_filters(dict(names=instance_name)))
            )
        except StopIteration:
            raise KeyError(instance_name)

    def __iter__(self) -> Generator[str, None, None]:
        return self.keys()

    def __len__(self) -> int:
        return sum(1 for instance in self._get_instances())

    def _get_instance_name(self, instance: Instance) -> str:
        try:
            return next(t for t in instance.tags if t.Key == "Name").Value
        except StopIteration:
            return ""

    def keys(self) -> Generator[str, None, None]:
        for instance in self._get_instances():
            yield self._get_instance_name(instance)

    def values(self) -> Generator[Instance, None, None]:
        return self._get_instances()

    def items(self) -> Generator[Tuple[str, Instance], None, None]:
        for instance in self._get_instances():
            yield self._get_instance_name(instance), instance
