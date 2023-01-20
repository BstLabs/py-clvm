import subprocess
import sys
from plt import _get_hw

_OS, _ = _get_hw()
_CMD = "aws.exe" if _OS == "Windows" else "aws"

def aws(**kwargs: str):
    """
    Login to AWS console

    Args:
        **kwargs (str): (optional) classifiers:

    Returns:
        None
    """
    profile_name = kwargs.get("profile", "default")
    print(
        f'\n------\nPlease, fix your AWS credentials and back again. Profile name "{profile_name}"\n'
    )
    subprocess.run(
        [
            _CMD,
            "configure",
            f"--profile={profile_name}",
        ],
        check=True,
    )
    sys.exit(0)
