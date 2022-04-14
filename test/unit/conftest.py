import os

import boto3
import pytest
from moto import mock_ec2

from ._common import create_instances


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def get_instance_id():
    with mock_ec2():
        instance_count = 1
        image_id = "ami-03cf127a"
        create_instances("us-east-1", image_id, instance_count)
        client = boto3.client("ec2", region_name="us-east-1")
        instances = client.describe_instances()["Reservations"][0]["Instances"]
        yield instances[0]["InstanceId"]


@pytest.fixture
def get_instance_info():
    with mock_ec2():
        instance_count = 1
        image_id = "ami-03cf127a"
        create_instances("us-east-1", image_id, instance_count)
        client = boto3.client("ec2", region_name="us-east-1")
        yield client.describe_instances()["Reservations"][0]["Instances"]
