import boto3
import pytest
from moto import mock_ec2

from ._common import create_instances


@mock_ec2
def test_create_instance(get_instance_info):
    instance_count = 1
    image_id = "ami-03cf127a"
    assert len(get_instance_info) == instance_count
    assert get_instance_info[0]["ImageId"] == image_id
