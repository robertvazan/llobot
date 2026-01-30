from datetime import datetime
from unittest.mock import patch
from llobot.chats.intent import ChatIntent
from llobot.crammers.date.simple import SimpleDateCrammer
from llobot.environments import Environment
from llobot.environments.context import ContextEnv

def test_simple_date_crammer():
    # Mock current_time to return a fixed date
    # Monday, October 23, 2023
    fixed_time = datetime(2023, 10, 23, 12, 0, 0)

    with patch('llobot.crammers.date.simple.current_time', return_value=fixed_time):
        crammer = SimpleDateCrammer()
        env = Environment()

        crammer.cram(env)

        chat = env[ContextEnv].build()
        assert len(chat) == 1
        assert chat[0].intent == ChatIntent.SYSTEM
        # Default is "full" format in "en" locale: "Monday, October 23, 2023"
        assert chat[0].content == "Today is Monday, October 23, 2023."

def test_custom_template_and_format():
    fixed_time = datetime(2023, 10, 23, 12, 0, 0)

    with patch('llobot.crammers.date.simple.current_time', return_value=fixed_time):
        # Using a custom LDML pattern
        crammer = SimpleDateCrammer(
            template="Date: {date}",
            date_format="yyyy-MM-dd",
            locale="en_US"
        )
        env = Environment()

        crammer.cram(env)

        chat = env[ContextEnv].build()
        assert chat[0].content == "Date: 2023-10-23"

def test_different_locale():
    fixed_time = datetime(2023, 10, 23, 12, 0, 0)

    with patch('llobot.crammers.date.simple.current_time', return_value=fixed_time):
        # Check explicit locale usage (even though guideline said "Always use English",
        # the class supports configuration)
        crammer = SimpleDateCrammer(
            template="{date}",
            date_format="d MMMM yyyy",
            locale="fr"
        )
        env = Environment()

        crammer.cram(env)

        chat = env[ContextEnv].build()
        # French: 23 octobre 2023
        assert chat[0].content == "23 octobre 2023"
