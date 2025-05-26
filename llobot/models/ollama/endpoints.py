from __future__ import annotations
from urllib.parse import urlparse

def localhost(port: int = 11434, *, path: str = '/api') -> str:
    return f'http://localhost:{port}{path}'

def local(host: str, port: int = 11434, *, path: str = '/api') -> str:
    return f'http://{host}:{port}{path}'

def remote(host: str, port: int = 11434, *, path: str = '/api') -> str:
    return f'https://{host}:{port}{path}'

def concise(endpoint: str) -> str:
    parts = urlparse(endpoint)
    return f'{parts.hostname}:{parts.port}' if parts.port != 11434 else parts.hostname

__all__ = [
    'localhost',
    'local',
    'remote',
    'concise',
]

