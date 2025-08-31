from __future__ import annotations
import traceback
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from llobot.models.catalogs import ModelCatalog
from llobot.models.listeners import ModelListener
import llobot.models.listeners
from llobot.models.openai import encoding

_logger = logging.getLogger(__name__)

def _handler(models: ModelCatalog) -> type:
    class OpenAIHttpHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/v1/models':
                data = encoding.encode_list([model.name for model in models])
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(data), "utf-8"))
            else:
                self.send_error(404)
        def do_POST(self):
            if self.path == '/v1/chat/completions':
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if not content_length:
                        raise ValueError('No Content-Length header.')
                    name, _, prompt = encoding.decode_request(json.loads(self.rfile.read(content_length)))
                    model = next((model for model in models if encoding.format_name(model.name) == name), None)
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
                    for line in encoding.format_stream(name, stream):
                        self.wfile.write(bytes(line + '\n\n', "utf-8"))
                except Exception as ex:
                    traceback.print_exception(ex)
                    raise ex
            else:
                self.send_error(404)
    return OpenAIHttpHandler

def create(port: int, models: ModelCatalog, *, host: str = '127.0.0.1') -> ModelListener:
    def listen():
        _logger.info(f'Serving {len(models)} models via OpenAI protocol on port {port}.')
        ThreadingHTTPServer((host, port), _handler(models)).serve_forever()
    return llobot.models.listeners.create(listen)

__all__ = [
    'create',
]
