from __future__ import annotations
from urllib.parse import urlparse

def localhost_ollama_endpoint(port: int = 11434, *, path: str = '/api') -> str:
    return f'http://localhost:{port}{path}'

def local_ollama_endpoint(host: str, port: int = 11434, *, path: str = '/api') -> str:
    return f'http://{host}:{port}{path}'

def remote_ollama_endpoint(host: str, port: int = 11434, *, path: str = '/api') -> str:
    return f'https://{host}:{port}{path}'

def concise_ollama_endpoint(endpoint: str) -> str:
    parts = urlparse(endpoint)
    return f'{parts.hostname}:{parts.port}' if parts.port != 11434 else parts.hostname

__all__ = [
    'localhost_ollama_endpoint',
    'local_ollama_endpoint',
    'remote_ollama_endpoint',
    'concise_ollama_endpoint',
]
