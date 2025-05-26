from __future__ import annotations
from urllib.parse import urlparse

def proprietary() -> str:
    return 'https://api.openai.com/v1'

def localhost(port: int, *, path: str = '/v1') -> str:
    return f'http://localhost:{port}{path}'

def local(host: str, port: int = 80, *, path: str = '/v1') -> str:
    return f'http://{host}:{port}{path}' if port != 80 else f'http://{host}{path}'

def remote(host: str, *, path: str = '/v1') -> str:
    return f'https://{host}{path}'

def concise(endpoint: str) -> str:
    if endpoint == proprietary():
        return 'proprietary'
    parts = urlparse(endpoint)
    if parts.hostname == 'localhost':
        return f'localhost:{parts.port}'
    if not parts.port:
        return parts.hostname
    return f'{parts.hostname}:{parts.port}'

__all__ = [
    'proprietary',
    'localhost',
    'local',
    'remote',
    'concise',
]

