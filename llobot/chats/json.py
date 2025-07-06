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
        'bot': metadata.bot,
        'project': metadata.project,
        'subproject': metadata.subproject,
        'model': metadata.model,
        'options': metadata.options,
        'time': encode_time(metadata.time),
        'cutoff': encode_time(metadata.cutoff),
    }
    return json.dumps({key: value for key, value in data.items() if value is not None})

def parse_metadata(serialized: str) -> ChatMetadata:
    data = json.loads(serialized)
    return ChatMetadata(
        bot = data.get('bot'),
        project = data.get('project'),
        subproject = data.get('subproject', data.get('scope')),
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

