from datetime import datetime
import json
from llobot.chats import ChatMetadata
import llobot.time

def encode_time(time: datetime | None) -> str | None:
    return llobot.time.format(time) if time else None

def decode_time(node: str | None) -> datetime | None:
    return llobot.time.parse(node) if node else None

def format_metadata(metadata: ChatMetadata) -> str:
    data = {
        'role': metadata.role,
        'project': metadata.project,
        'model': metadata.model,
        'options': metadata.options,
        'time': encode_time(metadata.time),
        'cutoff': encode_time(metadata.cutoff),
    }
    return json.dumps({key: value for key, value in data.items() if value is not None})

def parse_metadata(serialized: str) -> ChatMetadata:
    data = json.loads(serialized)
    return ChatMetadata(
        role = data.get('role', data.get('bot')),
        project = data.get('project'),
        model = data.get('model'),
        options = data.get('options'),
        time = decode_time(data.get('time')),
        cutoff = decode_time(data.get('cutoff', data.get('knowledge'))),
    )

__all__ = [
    'encode_time',
    'decode_time',
    'format_metadata',
    'parse_metadata',
]
