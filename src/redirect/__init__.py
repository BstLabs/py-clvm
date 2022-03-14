"""start/stop/refresh port redirection session"""

def _get_port_mapping(kwargs: dict) -> tuple:
    for port, local_port in kwargs.items():
        try:
            return int(port), int(local_port)
        except ValueError:
            pass  # not port numbers, mb something else
    return 8080, 8080

def _make_file_name(platform: str, profile: str, instance_name: str, port: int, local_port: int) -> str:
    return f'{platform}-{profile}-{instance_name}-{port}={local_port}'



