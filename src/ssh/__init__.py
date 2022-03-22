"""start/stop ssh  session"""

def _make_file_name(platform: str, profile: str, instance_name: str) -> str:
    return f'{platform}-{profile}-{instance_name}-ssh'

