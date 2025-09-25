"""
An OpenAI-compatible listener.
"""
from __future__ import annotations
import traceback
import json
import logging
import time
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

def _decode_role(data: str) -> ChatIntent:
    if data == 'user':
        return ChatIntent.PROMPT
    if data == 'assistant':
        return ChatIntent.RESPONSE
    raise ValueError(f'Unknown role: {data}')

def _decode_message(data: dict) -> ChatMessage:
    return ChatMessage(_decode_role(data['role']), data['content'])

def _decode_chat(data: list) -> ChatBranch:
    chat = ChatBuilder()
    for item in data:
        chat.add(_decode_message(item))
    return chat.build()

def _decode_request(data: dict) -> tuple[str, ChatBranch]:
    return data['model'], _decode_chat(data['messages'])

def _encode_event_defaults(model: str) -> dict:
    return {
        "id": "completion",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": []
    }

def _encode_role_event(model: str) -> dict:
    return _encode_event_defaults(model) | {
        "choices": [{
            "index": 0,
            "delta": {
                "role": 'assistant',
                "content": ""
            },
            "finish_reason": None
        }]
    }

def _encode_content_event(model: str, content: str) -> dict:
    return _encode_event_defaults(model) | {
        "choices": [{
            "index": 0,
            "delta": {
                "content": content
            },
            "finish_reason": None
        }]
    }

def _encode_stop_event(model: str) -> dict:
    return _encode_event_defaults(model) | {
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }

def _format_event(data: dict) -> str:
    return f'data: {json.dumps(data)}'

def _format_stream(model: str, stream: ModelStream) -> Iterable[str]:
    # The first event must set the role.
    yield _format_event(_encode_role_event(model))
    for item in stream:
        # We only expect string chunks here, because role.chat() returns a single message stream.
        if isinstance(item, str):
            yield _format_event(_encode_content_event(model, item))
    yield _format_event(_encode_stop_event(model))
    yield 'data: [DONE]'

def _encode_model_listing(model: Model) -> dict:
    return {
        'id': model.name,
        'object': 'model',
        'created': int(time.time()),
        'owned_by': 'llobot'
    }

def _encode_list(models: Iterable[Model]) -> dict:
    return {
        'object': 'list',
        'data': [_encode_model_listing(model) for model in models],
    }

class _OpenAIServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass, models: dict[str, Model]):
        super().__init__(server_address, RequestHandlerClass)
        self.models = models

class _OpenAIHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        models: dict[str, Model] = self.server.models
        if self.path == '/v1/models':
            data = _encode_list(models.values())
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(data), "utf-8"))
        else:
            self.send_error(404)
    def do_POST(self):
        models: dict[str, Model] = self.server.models
        if self.path == '/v1/chat/completions':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if not content_length:
                    raise ValueError('No Content-Length header.')
                name, prompt = _decode_request(json.loads(self.rfile.read(content_length)))
                model = models.get(name)
                if not model:
                    raise ValueError(f'No such model: {name}')
            except Exception as ex:
                traceback.print_exception(ex)
                self.send_error(400, str(ex))
                return
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                stream = model.generate(prompt)
                for line in _format_stream(name, stream):
                    self.wfile.write(bytes(line + '\n\n', "utf-8"))
            except Exception as ex:
                traceback.print_exception(ex)
                raise ex
        else:
            self.send_error(404)

class OpenAIListener(ModelListener):
    """
    A listener that serves models via the OpenAI protocol.
    """
    _models: dict[str, Model]
    _host: str
    _port: int

    def __init__(self, *models: Model, host: str = '127.0.0.1', port: int = 8080):
        """
        Initializes the OpenAI listener.

        Args:
            *models: `Model` instances to serve.
            host: The host to bind to. Defaults to '127.0.0.1'.
            port: The port to listen on. Defaults to 8080.
        """
        self._models = {model.name: model for model in models}
        self._host = host
        self._port = port

    def listen(self):
        """
        Starts the listener and blocks forever.
        """
        _logger.info(f'Serving {len(self._models)} models via OpenAI protocol on port {self._port}.')
        with _OpenAIServer((self._host, self._port), _OpenAIHttpHandler, self._models) as httpd:
            httpd.serve_forever()

__all__ = [
    'OpenAIListener',
]
