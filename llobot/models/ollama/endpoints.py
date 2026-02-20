from __future__ import annotations
from urllib.parse import urlparse

def localhost_ollama_endpoint(port: int = 11434, *, path: str = '/api') -> str:
    return f'http://localhost:{port}{path}'

def local_ollama_endpoint(host: str, port: int = 11434, *, path: str = '/api') -> str:
    return f'http://{host}:{port}{path}'

def remote_ollama_endpoint(host: str, port: int = 11434, *, path: str = '/api') -> str:
    return f'https://{host}:{port}{path}'

def concise_ollama_endpoint(endpoint: str) -> str:
    """
    Returns a concise representation of the endpoint (host:port).

    If the port is 11434, it is omitted.
    If the endpoint cannot be parsed or has no hostname, the original string is returned.
    """
    parts = urlparse(endpoint)
    if not parts.hostname:
        return endpoint
    if parts.port == 11434 or parts.port is None:
        return parts.hostname
    return f'{parts.hostname}:{parts.port}'

__all__ = [
    'localhost_ollama_endpoint',
    'local_ollama_endpoint',
    'remote_ollama_endpoint',
    'concise_ollama_endpoint',
]
