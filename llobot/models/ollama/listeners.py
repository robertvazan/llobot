from __future__ import annotations
import traceback
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from llobot.models.catalogs import ModelCatalog
from llobot.models.listeners import ModelListener, create_listener
from llobot.models.ollama.encoding import (
    encode_ollama_list,
    decode_ollama_request,
    format_ollama_name,
    format_ollama_stream,
)

_logger = logging.getLogger(__name__)

def _handler(models: ModelCatalog) -> type:
    class OllamaHttpHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/api/tags':
                data = encode_ollama_list([model.name for model in models])
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(data), "utf-8"))
            else:
                self.send_error(404)
        def do_POST(self):
            if self.path == '/api/chat':
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if not content_length:
                        raise ValueError('No Content-Length header.')
                    name, _, prompt = decode_ollama_request(json.loads(self.rfile.read(content_length)))
                    model = next((model for model in models if format_ollama_name(model.name) == name), None)
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
                    for line in format_ollama_stream(name, stream):
                        self.wfile.write(bytes(line+'\n', "utf-8"))
                except Exception as ex:
                    traceback.print_exception(ex)
                    raise ex
            else:
                self.send_error(404)
    return OllamaHttpHandler

def ollama_listener(models: ModelCatalog, *, host: str = '127.0.0.1', port: int = 11434) -> ModelListener:
    def listen():
        _logger.info(f'Serving {len(models)} models via Ollama protocol on port {port}.')
        ThreadingHTTPServer((host, port), _handler(models)).serve_forever()
    return create_listener(listen)

__all__ = [
    'ollama_listener',
]
