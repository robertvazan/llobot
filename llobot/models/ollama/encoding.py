from __future__ import annotations
import json
from llobot.chats import ChatIntent, ChatMessage, ChatBranch, ChatBuilder
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

def encode_role(intent: ChatIntent) -> str:
    if intent.binarize() == ChatIntent.RESPONSE:
        return 'assistant'
    else:
        return 'user'

def decode_role(data: str) -> ChatIntent:
    if data == 'user':
        return ChatIntent.PROMPT
    if data == 'assistant':
        return ChatIntent.RESPONSE
    raise ValueError(f"Unknown role: {data}")

def encode_message(message: ChatMessage) -> dict:
    return {
        'role': encode_role(message.intent),
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

def encode_content_event(model: str, token: str) -> dict:
    return {
        'model': format_name(model),
        'message': {
            'role': encode_role(ChatIntent.RESPONSE),
            'content': token
        },
        'done': False
    }

def encode_done_event(model: str) -> dict:
    return {
        'model': format_name(model),
        'done': True
    }

def decode_event(data: dict) -> str | None:
    return data.get('message', {}).get('content')

def format_stream(model: str, stream: ModelStream) -> Iterator[str]:
    for token in stream:
        yield json.dumps(encode_content_event(model, token))
    yield json.dumps(encode_done_event(model))

def parse_stream(lines: Iterator[str]) -> Iterator[str]:
    for line in lines:
        if not line:
            continue
        data = json.loads(line)
        if data.get('done'):
            break
        content = decode_event(data)
        if content:
            yield content

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
