from __future__ import annotations
from babel.dates import format_date
from llobot.chats.intent import ChatIntent
from llobot.chats.message import ChatMessage
from llobot.crammers.date import DateCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv
from llobot.utils.time import current_time
from llobot.utils.values import ValueTypeMixin

class SimpleDateCrammer(DateCrammer, ValueTypeMixin):
    """
    A crammer that adds the current date to the context as a system message.
    """
    _template: str
    _date_format: str
    _locale: str

    def __init__(self, *, template: str = "Today is {date}.", date_format: str = "full", locale: str = "en"):
        """
        Creates a new simple date crammer.

        Args:
            template: The template string for the message. Must contain `{date}` placeholder.
            date_format: The format for the date. Can be one of "short", "medium", "long", "full",
                         or a custom LDML pattern.
            locale: The locale identifier to use for formatting (e.g., "en", "en_US").
        """
        self._template = template
        self._date_format = date_format
        self._locale = locale

    def cram(self, env: Environment) -> None:
        """
        Adds the formatted date message to the context.
        """
        now = current_time()
        # babel.dates.format_date accepts datetime objects too.
        date_str = format_date(now, format=self._date_format, locale=self._locale)
        text = self._template.format(date=date_str)

        env[ContextEnv].builder.add(ChatMessage(ChatIntent.SYSTEM, text))

__all__ = [
    'SimpleDateCrammer',
]
