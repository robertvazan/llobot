from __future__ import annotations
from datetime import datetime

class ChatMetadata:
    # Role of the bot that handled user's prompt.
    _role: str | None
    # Project upon which the bot operated if any.
    _project: str | None
    # Name of the backend model used to generate response. Roles have a default model, but it can change over time and user can override it.
    _model: str | None
    # Model options, usually defaults, but it's possible to override them for every chat.
    _options: dict | None
    # Time when the chat was recorded, which corresponds to the time when generation completed.
    # Completion time is better than start time, because it can be computed in the function that saves the chat.
    _time: datetime | None
    # Cutoff time for knowledge and examples used to stuff this chat branch.
    _cutoff: datetime | None

    def __init__(self, *,
        role: str | None = None,
        project: str | None = None,
        model: str | None = None,
        options: dict | None = None,
        time: datetime | None = None,
        cutoff: datetime | None = None,
    ):
        self._role = role
        self._project = project
        self._model = model
        self._options = options
        self._time = time
        self._cutoff = cutoff

    @property
    def role(self) -> str | None:
        return self._role

    @property
    def project(self) -> str | None:
        return self._project

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
        return bool(self.role or self.project or self.model or self.options is not None or self.time or self.cutoff)

    def __or__(self, other: ChatMetadata) -> ChatMetadata:
        return ChatMetadata(
            role = other.role or self.role,
            project = other.project or self.project,
            model = other.model or self.model,
            options = self.options | other.options if self.options and other.options else other.options or self.options,
            time = other.time or self.time,
            cutoff = other.cutoff or self.cutoff,
        )
