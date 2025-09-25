from __future__ import annotations
import json
from typing import Iterable
from llobot.chats.intents import ChatIntent
from llobot.chats.messages import ChatMessage
from llobot.chats.branches import ChatBranch
from llobot.chats.binarization import binarize_intent

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

def encode_request(model: str, prompt: ChatBranch) -> dict:
    """
    Encodes a chat request for the OpenAI API.

    Args:
        model: The model ID.
        prompt: The chat branch to send.

    Returns:
        A dictionary representing the JSON request body.
    """
    return {
        'model': model,
        'messages': _encode_chat(prompt),
        'stream': True,
    }

def _decode_event(data: dict) -> Iterable[str]:
    for choice in data.get("choices", []):
        if choice.get("index", 0) == 0:
            delta = choice.get("delta", {})
            content = delta.get("content")
            if content:
                yield content

def parse_stream(lines: Iterable[str]) -> Iterable[str]:
    """
    Parses a server-sent events (SSE) stream from the OpenAI API.

    Args:
        lines: An iterable of strings from the HTTP response.

    Yields:
        String chunks of the response content.
    """
    for line in lines:
        line = line.strip()
        if line.startswith("data:"):
            data = line[5:].strip()
            if data == "[DONE]":
                break
            yield from _decode_event(json.loads(data))

__all__ = [
    'encode_request',
    'parse_stream',
]
