from __future__ import annotations
import time
import json
from llobot.chats import ChatRole, ChatMessage, ChatBranch, ChatBuilder
from llobot.models.stats import ModelStats
from llobot.models.streams import ModelStream

def format_name(model: str):
    # This is OpenAI protocol, so don't qualify proprietary models released by OpenAI.
    # This will have to be expanded for providers compatible with OpenAI protocol and for local OpenAI-compatible servers.
    model = model.removeprefix('openai/')
    model = model.removeprefix('gemini/')
    # Bot names are encountered only by listener. We want to expose them under short names.
    model = model.removeprefix('expert/')
    # Everything else remains qualified, although we shouldn't really encounter other registries here.
    # It is unclear what model name syntax is supported, but chances are that unmodified model name will work.
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

def encode_stats(stats: ModelStats) -> dict:
    data = {
        'prompt_tokens': stats.prompt_tokens,
        'completion_tokens': stats.response_tokens,
        'total_tokens': stats.total_tokens,
    }
    if stats.cached_tokens is not None:
        data.setdefault('prompt_tokens_details', {})['cached_tokens'] = stats.cached_tokens
    return {key: value for key, value in data.items() if value is not None}

def decode_stats(data: dict) -> ModelStats:
    return ModelStats(
        prompt_tokens = data.get('prompt_tokens', None),
        response_tokens = data.get('completion_tokens', None),
        total_tokens = data.get('total_tokens', None),
        cached_tokens = data.get('prompt_tokens_details', {}).get('cached_tokens', None),
    )

def _encode_event_defaults(model: str) -> dict:
    return {
        "id": "completion",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": format_name(model),
        "choices": []
    }

def encode_role_event(model: str, role: ChatRole) -> dict:
    return _encode_event_defaults(model) | {
        "choices": [{
            "index": 0,
            "delta": {
                "role": encode_role(role),
                "content": ""
            },
            "finish_reason": None
        }]
    }

def encode_content_event(model: str, content: str) -> dict:
    return _encode_event_defaults(model) | {
        "choices": [{
            "index": 0,
            "delta": {
                "content": content
            },
            "finish_reason": None
        }]
    }

def encode_stop_event(model: str) -> dict:
    return _encode_event_defaults(model) | {
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }

def encode_usage_event(model: str, stats: ModelStats) -> dict:
    return _encode_event_defaults(model) | {
        "usage": encode_stats(stats),
    }

def decode_event(data: dict) -> Iterable[str | ModelStats]:
    for choice in data.get("choices", []):
        if choice.get("index", 0) == 0:
            delta = choice.get("delta", {})
            content = delta.get("content")
            if content:
                yield content
    if data.get("usage") is not None:
        yield decode_stats(data["usage"])

def _format_event(data: dict) -> str:
    return f'data: {json.dumps(data)}'

def format_stream(model: str, stream) -> Iterator[str]:
    yield _format_event(encode_role_event(model, ChatRole.ASSISTANT))
    for token in stream:
        yield _format_event(encode_content_event(model, token))
    yield _format_event(encode_stop_event(model))
    yield _format_event(encode_usage_event(model, stream.stats()))
    yield 'data: [DONE]'

def parse_stream(lines: Iterator[str]) -> Iterator[str | ModelStats]:
    for line in lines:
        line = line.strip()
        if line.startswith("data:"):
            data = line[5:].strip()
            if data == "[DONE]":
                break
            yield from decode_event(json.loads(data))

def encode_request(model: str, options: dict, prompt: ChatBranch) -> dict:
    return {
        'model': format_name(model),
        'messages': encode_chat(prompt),
        'stream': True,
        'stream_options': {
            'include_usage': True
        },
        **{key: value for key, value in options.items() if key != 'context_size'}
    }

def decode_request(data: dict) -> (str, dict, ChatBranch):
    model = data['model']
    options = {key: value for key, value in data.items() if key in ('temperature')}
    prompt = decode_chat(data['messages'])
    return model, options, prompt

def encode_model(model: str) -> dict:
    return {
        'id': format_name(model),
        'object': 'model',
        'created': int(time.time()),
        'owned_by': 'llobot'
    }

def decode_model(data: dict) -> str:
    return data['id']

def encode_list(models: Iterable[str]) -> dict:
    return {
        'object': 'list',
        'data': [encode_model(model) for model in models],
    }

def decode_list(data: dict) -> list[str]:
    return [decode_model(item) for item in data['data']]

__all__ = [
    'format_name',
    'encode_role',
    'decode_role',
    'encode_message',
    'decode_message',
    'encode_chat',
    'decode_chat',
    'encode_stats',
    'decode_stats',
    'encode_role_event',
    'encode_content_event',
    'encode_stop_event',
    'encode_usage_event',
    'decode_event',
    'format_stream',
    'parse_stream',
    'encode_request',
    'decode_request',
    'encode_model',
    'decode_model',
    'encode_list',
    'decode_list',
]

