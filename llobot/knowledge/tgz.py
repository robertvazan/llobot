from pathlib import Path
import io
import tarfile
from llobot.knowledge import Knowledge
import llobot.fs

SUFFIX = '.tar.gz'

def serialize(knowledge: Knowledge) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as tar:
        for path in knowledge.keys().sorted():
            content = knowledge[path].encode('utf-8')
            info = tarfile.TarInfo(path.as_posix())
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return buffer.getvalue()

def deserialize(buffer: bytes) -> Knowledge:
    knowledge = {}
    with tarfile.open(fileobj=io.BytesIO(buffer), mode='r:gz') as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            content = tar.extractfile(member).read().decode('utf-8')
            knowledge[Path(member.name)] = content
    return Knowledge(knowledge)

def save(path: Path, knowledge: Knowledge):
    llobot.fs.write_bytes(path, serialize(knowledge))

def load(path: Path) -> Knowledge:
    return deserialize(path.read_bytes())

__all__ = [
    'SUFFIX',
    'serialize',
    'deserialize',
    'save',
    'load',
]

