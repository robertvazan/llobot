from llobot.links import Link
import llobot.links

# This is only intended to work for top-level types. We are assuming that type names are globally unique.
def type_name(name: str) -> Link:
    return llobot.links.filename(f'{name}.java')

__all__ = ['type_name']

