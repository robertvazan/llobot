from __future__ import annotations
from datetime import datetime

class ChatMetadata:
    # Bot that was used to process user's prompt.
    _bot: str | None
    # Project upon which the bot operated if any.
    _project: str | None
    # Subproject within the project the bot operated on. This should be left empty if the bot operated on the whole project.
    _subproject: str | None
    # Name of the backend model used to generate response. Bots have a default model, but it can change over time and user can override it.
    _model: str | None
    # Model options, usually defaults, but it's possible to override them for every chat.
    _options: dict | None
    # Time when the chat was recorded, which corresponds to the time when generation completed.
    # Completion time is better than start time, because it can be computed in the function that saves the chat.
    _time: datetime | None
    # Cutoff time for knowledge and examples used to stuff this chat branch.
    _cutoff: datetime | None

    def __init__(self, *,
        bot: str | None = None,
        project: str | None = None,
        subproject: str | None = None,
        model: str | None = None,
        options: dict | None = None,
        time: datetime | None = None,
        cutoff: datetime | None = None,
    ):
        self._bot = bot
        self._project = project
        self._subproject = subproject
        self._model = model
        self._options = options
        self._time = time
        self._cutoff = cutoff

    @property
    def bot(self) -> str | None:
        return self._bot

    @property
    def project(self) -> str | None:
        return self._project

    @property
    def subproject(self) -> str | None:
        return self._subproject

    @property
    def model(self) -> str | None:
        return self._model

    @property
    def options(self) -> dict | None:
        return self._options

    @property
    def time(self) -> datetime | None:
        return self._time

    @property
    def cutoff(self) -> datetime | None:
        return self._cutoff

    def __str__(self) -> str:
        return str(vars(self))

    def __bool__(self) -> bool:
        return bool(self.bot or self.project or self.subproject or self.model or self.options is not None or self.time or self.cutoff)

    def __or__(self, other: ChatMetadata) -> ChatMetadata:
        return ChatMetadata(
            bot = other.bot or self.bot,
            project = other.project or self.project,
            subproject = other.subproject or self.subproject,
            model = other.model or self.model,
            options = self.options | other.options if self.options and other.options else other.options or self.options,
            time = other.time or self.time,
            cutoff = other.cutoff or self.cutoff,
        )

