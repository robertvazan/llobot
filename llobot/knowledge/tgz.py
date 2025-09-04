from pathlib import Path
import io
import tarfile
from llobot.knowledge import Knowledge
from llobot.text import normalize_document
from llobot.fs import write_bytes

KNOWLEDGE_TGZ_SUFFIX = '.tar.gz'

def serialize_knowledge_tgz(knowledge: Knowledge) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as tar:
        for path in knowledge.keys().sorted():
            content = knowledge[path].encode('utf-8')
            info = tarfile.TarInfo(path.as_posix())
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return buffer.getvalue()

def deserialize_knowledge_tgz(buffer: bytes) -> Knowledge:
    knowledge = {}
    with tarfile.open(fileobj=io.BytesIO(buffer), mode='r:gz') as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            content = normalize_document(tar.extractfile(member).read().decode('utf-8'))
            knowledge[Path(member.name)] = content
    return Knowledge(knowledge)

def save_knowledge_tgz(path: Path, knowledge: Knowledge):
    write_bytes(path, serialize_knowledge_tgz(knowledge))

def load_knowledge_tgz(path: Path) -> Knowledge:
    return deserialize_knowledge_tgz(path.read_bytes())

__all__ = [
    'KNOWLEDGE_TGZ_SUFFIX',
    'serialize_knowledge_tgz',
    'deserialize_knowledge_tgz',
    'save_knowledge_tgz',
    'load_knowledge_tgz',
]
