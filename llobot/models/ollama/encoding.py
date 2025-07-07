from __future__ import annotations
import json
from llobot.chats import ChatRole, ChatMessage, ChatBranch, ChatBuilder
from llobot.models.stats import ModelStats
from llobot.models.streams import ModelStream
import llobot.text

def format_name(model: str):
    # This is Ollama protocol, so don't qualify models coming from Ollama registry.
    model = model.removeprefix('ollama/')
    # Bot names are encountered only by listener. We want to expose them under short names.
    model = model.removeprefix('bot/')
    # Everything else remains qualified, although we shouldn't really encounter other registries here.
    # Ollama supports slashes in model names for user-uploaded models, so most model names should be compatible.
    if ':' not in model:
        model += ':latest'
    return model

def encode_role(role: ChatRole) -> str:
    if role == ChatRole.USER:
        return 'user'
    if role == ChatRole.ASSISTANT:
        return 'assistant'
    raise ValueError

def decode_role(data: str) -> ChatRole:
    return next(role for role in ChatRole if encode_role(role) == data)

def encode_message(message: ChatMessage) -> dict:
    return {
        'role': encode_role(message.role),
        'content': message.content
    }

def decode_message(data: dict) -> ChatMessage:
    return ChatMessage(decode_role(data['role']), data['content'])

def encode_chat(branch: ChatBranch) -> list:
    return [encode_message(message) for message in branch]

def decode_chat(data: list) -> ChatBranch:
    chat = ChatBuilder()
    for item in data:
        chat.add(decode_message(item))
    return chat.build()

def encode_time(seconds: float | None) -> int | None:
    return int(1e9 * seconds) if seconds else None

def decode_time(nanos: int | None) -> float | None:
    return nanos / 1e9 if nanos else None

def encode_stats(stats: ModelStats) -> dict:
    data = {
        'prompt_eval_count': stats.prompt_tokens,
        'eval_count': stats.response_tokens,
        'load_duration': encode_time(stats.load_seconds),
        'prompt_eval_duration': encode_time(stats.prompt_seconds),
        'eval_duration': encode_time(stats.response_seconds),
        'total_duration': encode_time(stats.total_seconds),
    }
    return {key: value for key, value in data.items() if value is not None}

def decode_stats(data: dict) -> ModelStats:
    return ModelStats(
        prompt_tokens = data.get('prompt_eval_count', None),
        response_tokens = data.get('eval_count', None),
        load_seconds = decode_time(data.get('load_duration', None)),
        prompt_seconds = decode_time(data.get('prompt_eval_duration', None)),
        response_seconds = decode_time(data.get('eval_duration', None)),
        total_seconds = decode_time(data.get('total_duration', None)),
    )

def encode_content_event(model: str, role: ChatRole, token: str) -> dict:
    return {
        'model': format_name(model),
        'message': {
            'role': encode_role(role),
            'content': token
        },
        'done': False
    }

def encode_done_event(model: str, stats: ModelStats) -> dict:
    return encode_stats(stats) | {
        'model': format_name(model),
        'done': True
    }

def decode_event(data: dict) -> str | ModelStats:
    return decode_stats(data) if data['done'] else data['message']['content']

MAX_CHUNK_SIZE = 1000

def format_stream(model: str, stream: ModelStream) -> Iterator[str]:
    for token in stream:
        # Chunk long responses. This is a workaround for bad clients that do not like to receive everything at once.
        while token:
            chunk = token[:MAX_CHUNK_SIZE]
            token = token[MAX_CHUNK_SIZE:]
            yield json.dumps(encode_content_event(model, ChatRole.ASSISTANT, chunk))
    yield json.dumps(encode_done_event(model, stream.stats()))

def parse_stream(lines: Iterator[str]) -> Iterator[str | ModelStats]:
    for line in lines:
        if line:
            yield decode_event(json.loads(line))

def encode_request(model: str, options: dict, prompt: ChatBranch) -> dict:
    return {
        'model': format_name(model),
        'options': options,
        'messages': encode_chat(prompt)
    }

def decode_request(data: dict) -> (str, dict, ChatBranch):
    return format_name(data['model']), data['options'], decode_chat(data['messages'])

def encode_model(model: str) -> dict:
    return {
        'name': format_name(model),
        'model': format_name(model)
    }

def encode_list(models: Iterable[str]) -> dict:
    return {
        'models': [encode_model(model) for model in models]
    }

__all__ = [
    'format_name',
    'encode_role',
    'decode_role',
    'encode_message',
    'decode_message',
    'encode_chat',
    'decode_chat',
    'encode_time',
    'decode_time',
    'encode_stats',
    'decode_stats',
    'encode_content_event',
    'encode_done_event',
    'decode_event',
    'format_stream',
    'parse_stream',
    'encode_request',
    'decode_request',
    'encode_model',
    'encode_list',
]

