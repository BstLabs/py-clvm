"""Install CLI"""

"""
# Linux or macOS
# $ export AWS_PROFILE=user1
#
# Windows
# C:\> setx AWS_PROFILE user1
"""

from .aws import aws

__all__ = ["aws"]
