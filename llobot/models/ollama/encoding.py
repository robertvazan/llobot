from __future__ import annotations
import json
from typing import Iterable
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.binarization import binarize_intent

def _format_model_name(name: str) -> str:
    if ':' not in name:
        return f'{name}:latest'
    return name

def _encode_role(intent: ChatIntent) -> str:
    if binarize_intent(intent) == ChatIntent.RESPONSE:
        return 'assistant'
    else:
        return 'user'

def _encode_message(message: ChatMessage) -> dict:
    return {
        'role': _encode_role(message.intent),
        'content': message.content
    }

def _encode_chat(branch: ChatBranch) -> list:
    return [_encode_message(message) for message in branch]

def encode_request(model: str, options: dict, prompt: ChatBranch) -> dict:
    """
    Encodes a chat request for the Ollama API.

    Args:
        model: The model ID.
        options: A dictionary of Ollama options.
        prompt: The chat branch to send.

    Returns:
        A dictionary representing the JSON request body.
    """
    return {
        'model': _format_model_name(model),
        'options': options,
        'messages': _encode_chat(prompt)
    }

def _decode_event(data: dict) -> str | None:
    return data.get('message', {}).get('content')

def parse_stream(lines: Iterable[str]) -> Iterable[str]:
    """
    Parses a stream of newline-delimited JSON objects from the Ollama API.

    Args:
        lines: An iterable of strings from the HTTP response.

    Yields:
        String chunks of the response content.
    """
    for line in lines:
        if not line:
            continue
        data = json.loads(line)
        if data.get('done'):
            break
        content = _decode_event(data)
        if content:
            yield content

__all__ = [
    'encode_request',
    'parse_stream',
]
