from __future__ import annotations
from typing import Iterable
from llobot.chats.message import ChatMessage
from llobot.chats.thread import ChatThread
from llobot.chats.stream import ChatStream
from llobot.formats.mentions import parse_mentions, filter_mentions
from llobot.roles import Role

class Router(Role):
    """
    A role that routes requests to other roles based on mentions in the prompt.

    The router examines the first message of the prompt for mentions of known roles.
    If exactly one known role is mentioned, the request is forwarded to that role
    with the routing mention removed from the first message.
    """
    _name: str
    _roles: dict[str, Role]

    def __init__(self, roles: Iterable[Role], name: str = 'llobot'):
        """
        Initializes the router.

        Args:
            roles: The collection of roles to route to.
            name: The name of the router role itself.

        Raises:
            ValueError: If multiple roles have the same name.
        """
        self._name = name
        self._roles = {}
        for role in roles:
            if role.name in self._roles:
                raise ValueError(f"Duplicate role name: {role.name}")
            self._roles[role.name] = role

    @property
    def name(self) -> str:
        return self._name

    def chat(self, prompt: ChatThread) -> ChatStream:
        """
        Routes the chat prompt to a target role.

        Raises:
            ValueError: If the prompt is empty or if not exactly one target role
                is mentioned in the first message.
        """
        if not prompt:
            raise ValueError("Prompt is empty")

        first_message = prompt[0]
        mentions = parse_mentions(first_message)

        # Identify unique target roles mentioned in the first message.
        target_names = sorted(list(set(m for m in mentions if m in self._roles)))

        if len(target_names) != 1:
            raise ValueError(f"Expected exactly one target role, found {len(target_names)}: {', '.join(target_names)}")

        target_name = target_names[0]
        target_role = self._roles[target_name]

        # Filter the routing mention from the first message.
        new_content = filter_mentions(first_message.content, [target_name])
        new_first_message = ChatMessage(first_message.intent, new_content)

        # Reconstruct the thread with the modified first message.
        new_prompt = ChatThread([new_first_message]) + prompt[1:]

        return target_role.chat(new_prompt)

__all__ = [
    'Router',
]
