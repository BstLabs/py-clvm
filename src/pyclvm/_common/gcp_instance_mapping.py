# -*- coding: utf-8 -*- #

import os
from typing import Iterator, Iterable, AnyStr

from .session_gcp import get_session
from google.cloud import compute_v1


class GcpComputeAllInstancesData:
    def __init__(self, **kwargs) -> None:
        self.session = get_session(**kwargs)
        self._client = compute_v1.InstancesClient(credentials=self.session.get_credentials())
        self._zone = kwargs.get("zone", os.getenv("CLOUDSDK_COMPUTE_ZONE", "europe-west2-b"))
        self._instances_data = self._instances()

    # ---
    def _instances(self) -> Iterable:
        request = compute_v1.AggregatedListInstancesRequest()
        request.project = self.session.project_id
        # Use the `max_results` parameter to limit the number of results that the API returns per response page.
        # request.max_results = 50
        # _instances = filter(lambda x: (x[0] == f"zones/{self._zone}"),
        #              self._client.aggregated_list(request=request))
        _instances = []
        for zone, instances_in_zone in self._client.aggregated_list(request=request):
            if f"zones/{self._zone}" == zone:
                _instances = instances_in_zone.instances

        return [(
            _instance.id,
            self._get_instance_name(_instance.tags) or _instance.name,
            _instance.status,
        ) for _instance in _instances]

    # ---
    def __iter__(self) -> Iterator:
        yield from self._instances_data

    # ---
    @staticmethod
    def _get_instance_name(_tags: compute_v1.types.compute.Tags) -> AnyStr:
        """
        Returns VM name from a tag
        :params _tags: GCP compute VM tags object
        :return: (str) Name of VM
        """
        try:
            return _tags.name
        except AttributeError:
            pass
