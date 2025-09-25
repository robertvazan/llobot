"""
An Ollama-compatible listener.
"""
from __future__ import annotations
import traceback
import json
import logging
from typing import Iterable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.models import Model
from llobot.models.listeners import ModelListener
from llobot.models.streams import ModelStream

_logger = logging.getLogger(__name__)

def _format_model_name(name: str) -> str:
    if ':' not in name:
        return f'{name}:latest'
    return name

def _decode_role(data: str) -> ChatIntent:
    if data == 'user':
        return ChatIntent.PROMPT
    if data == 'assistant':
        return ChatIntent.RESPONSE
    raise ValueError(f"Unknown role: {data}")

def _decode_message(data: dict) -> ChatMessage:
    return ChatMessage(_decode_role(data['role']), data['content'])

def _decode_chat(data: list) -> ChatBranch:
    chat = ChatBuilder()
    for item in data:
        chat.add(_decode_message(item))
    return chat.build()

def _decode_request(data: dict) -> tuple[str, ChatBranch]:
    return data['model'], _decode_chat(data['messages'])

def _encode_content_event(model: str, token: str) -> dict:
    return {
        'model': _format_model_name(model),
        'message': {
            'role': 'assistant',
            'content': token
        },
        'done': False
    }

def _encode_done_event(model: str) -> dict:
    return {
        'model': _format_model_name(model),
        'done': True
    }

def _format_stream(model: str, stream: ModelStream) -> Iterable[str]:
    for item in stream:
        if isinstance(item, str):
            yield json.dumps(_encode_content_event(model, item))
    yield json.dumps(_encode_done_event(model))

def _encode_model_listing(model: Model) -> dict:
    return {
        'name': _format_model_name(model.name),
        'model': _format_model_name(model.name)
    }

def _encode_list(models: Iterable[Model]) -> dict:
    return {
        'models': [_encode_model_listing(model) for model in models]
    }

class _OllamaServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass, models: dict[str, Model]):
        super().__init__(server_address, RequestHandlerClass)
        self.models = models

class _OllamaHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        models: dict[str, Model] = self.server.models
        if self.path == '/api/tags':
            data = _encode_list(models.values())
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(data), "utf-8"))
        else:
            self.send_error(404)

    def do_POST(self):
        models: dict[str, Model] = self.server.models
        if self.path == '/api/chat':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if not content_length:
                    raise ValueError('No Content-Length header.')
                name, prompt = _decode_request(json.loads(self.rfile.read(content_length)))
                model = models.get(name) or next((m for m in models.values() if _format_model_name(m.name) == name), None)
                if not model:
                    raise ValueError(f'No such model: {name}')
            except Exception as ex:
                traceback.print_exception(ex)
                self.send_error(400, str(ex))
                return
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-ndjson; charset=utf-8')
                self.end_headers()
                stream = model.generate(prompt)
                for line in _format_stream(name, stream):
                    self.wfile.write(bytes(line + '\n', "utf-8"))
            except Exception as ex:
                traceback.print_exception(ex)
                raise ex
        else:
            self.send_error(404)

class OllamaListener(ModelListener):
    """
    A listener that serves models via the Ollama protocol.
    """
    _models: dict[str, Model]
    _host: str
    _port: int

    def __init__(self, *models: Model, host: str = '127.0.0.1', port: int = 11434):
        """
        Initializes the Ollama listener.

        Args:
            *models: `Model` instances to serve.
            host: The host to bind to. Defaults to '127.0.0.1'.
            port: The port to listen on. Defaults to 11434.
        """
        self._models = {model.name: model for model in models}
        self._host = host
        self._port = port

    def listen(self):
        """
        Starts the listener and blocks forever.
        """
        _logger.info(f'Serving {len(self._models)} models via Ollama protocol on port {self._port}.')
        with _OllamaServer((self._host, self._port), _OllamaHttpHandler, self._models) as httpd:
            httpd.serve_forever()

__all__ = [
    'OllamaListener',
]
