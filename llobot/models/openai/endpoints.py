from __future__ import annotations
from urllib.parse import urlparse

def proprietary_openai_endpoint() -> str:
    return 'https://api.openai.com/v1'

def localhost_openai_endpoint(port: int, *, path: str = '/v1') -> str:
    return f'http://localhost:{port}{path}'

def local_openai_endpoint(host: str, port: int = 80, *, path: str = '/v1') -> str:
    return f'http://{host}:{port}{path}' if port != 80 else f'http://{host}{path}'

def remote_openai_endpoint(host: str, *, path: str = '/v1') -> str:
    return f'https://{host}{path}'

def concise_openai_endpoint(endpoint: str) -> str:
    if endpoint == proprietary_openai_endpoint():
        return 'proprietary'
    parts = urlparse(endpoint)
    if parts.hostname == 'localhost':
        return f'localhost:{parts.port}'
    if not parts.port:
        return parts.hostname
    return f'{parts.hostname}:{parts.port}'

__all__ = [
    'proprietary_openai_endpoint',
    'localhost_openai_endpoint',
    'local_openai_endpoint',
    'remote_openai_endpoint',
    'concise_openai_endpoint',
]
