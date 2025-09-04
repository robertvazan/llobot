from __future__ import annotations
import json
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.builders import ChatBuilder
from llobot.models.streams import ModelStream
from llobot.chats.binarization import binarize_intent

def format_ollama_name(model: str):
    # This is Ollama protocol, so don't qualify models coming from Ollama registry.
    model = model.removeprefix('ollama/')
    # Bot names are encountered only by listener. We want to expose them under short names.
    model = model.removeprefix('bot/')
    # Everything else remains qualified, although we shouldn't really encounter other registries here.
    # Ollama supports slashes in model names for user-uploaded models, so most model names should be compatible.
    if ':' not in model:
        model += ':latest'
    return model

def encode_ollama_role(intent: ChatIntent) -> str:
    if binarize_intent(intent) == ChatIntent.RESPONSE:
        return 'assistant'
    else:
        return 'user'

def decode_ollama_role(data: str) -> ChatIntent:
    if data == 'user':
        return ChatIntent.PROMPT
    if data == 'assistant':
        return ChatIntent.RESPONSE
    raise ValueError(f"Unknown role: {data}")

def encode_ollama_message(message: ChatMessage) -> dict:
    return {
        'role': encode_ollama_role(message.intent),
        'content': message.content
    }

def decode_ollama_message(data: dict) -> ChatMessage:
    return ChatMessage(decode_ollama_role(data['role']), data['content'])

def encode_ollama_chat(branch: ChatBranch) -> list:
    return [encode_ollama_message(message) for message in branch]

def decode_ollama_chat(data: list) -> ChatBranch:
    chat = ChatBuilder()
    for item in data:
        chat.add(decode_ollama_message(item))
    return chat.build()

def encode_ollama_content_event(model: str, token: str) -> dict:
    return {
        'model': format_ollama_name(model),
        'message': {
            'role': encode_ollama_role(ChatIntent.RESPONSE),
            'content': token
        },
        'done': False
    }

def encode_ollama_done_event(model: str) -> dict:
    return {
        'model': format_ollama_name(model),
        'done': True
    }

def decode_ollama_event(data: dict) -> str | None:
    return data.get('message', {}).get('content')

def format_ollama_stream(model: str, stream: ModelStream) -> Iterator[str]:
    for item in stream:
        if isinstance(item, str):
            yield json.dumps(encode_ollama_content_event(model, item))
    yield json.dumps(encode_ollama_done_event(model))

def parse_ollama_stream(lines: Iterator[str]) -> Iterator[str]:
    for line in lines:
        if not line:
            continue
        data = json.loads(line)
        if data.get('done'):
            break
        content = decode_ollama_event(data)
        if content:
            yield content

def encode_ollama_request(model: str, options: dict, prompt: ChatBranch) -> dict:
    return {
        'model': format_ollama_name(model),
        'options': options,
        'messages': encode_ollama_chat(prompt)
    }

def decode_ollama_request(data: dict) -> (str, dict, ChatBranch):
    return format_ollama_name(data['model']), data['options'], decode_ollama_chat(data['messages'])

def encode_ollama_model_listing(model: str) -> dict:
    return {
        'name': format_ollama_name(model),
        'model': format_ollama_name(model)
    }

def encode_ollama_list(models: Iterable[str]) -> dict:
    return {
        'models': [encode_ollama_model_listing(model) for model in models]
    }

__all__ = [
    'format_ollama_name',
    'encode_ollama_role',
    'decode_ollama_role',
    'encode_ollama_message',
    'decode_ollama_message',
    'encode_ollama_chat',
    'decode_ollama_chat',
    'encode_ollama_content_event',
    'encode_ollama_done_event',
    'decode_ollama_event',
    'format_ollama_stream',
    'parse_ollama_stream',
    'encode_ollama_request',
    'decode_ollama_request',
    'encode_ollama_model_listing',
    'encode_ollama_list',
]
