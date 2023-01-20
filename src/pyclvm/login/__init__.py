"""Login to Cloud Platform"""

"""
# Linux or macOS
# $ export AWS_PROFILE=user1
#
# Windows
# C:\> setx AWS_PROFILE user1
"""

from .aws import aws
from .gcp import gcp
from .azure import azure

__all__ = ["aws", "gcp", "azure"]
