from __future__ import annotations
from enum import Enum
from datetime import datetime
from functools import lru_cache
from textwrap import dedent, indent
import logging
import re
from llobot.chats import ChatRole, ChatBranch, ChatBuilder, ChatMetadata
from llobot.projects import Project, Scope
from llobot.contexts import Context
from llobot.experts import Expert
from llobot.experts.requests import ExpertRequest
from llobot.models import Model
from llobot.models.catalogs import ModelCatalog
from llobot.models.streams import ModelStream, ModelException
import llobot.time
import llobot.models.streams

_logger = logging.getLogger(__name__)

class _StandardExpertCommand(Enum):
    HI = 'hi'
    OK = 'ok'
    ECHO = 'echo'
    INFO = 'info'

class _StandardExpertRequest:
    owner: _StandardExpertModel
    expert: Expert
    memory: ExpertMemory
    command: _StandardExpertCommand | None
    # Clean user prompt before assembly into the full prompt.
    prompt: ChatBranch
    scope: Scope | None
    # Cutoff parsed out of the prompt, whether from the header in the first message or from automatic cutoff in the second message.
    given_cutoff: datetime | None
    # Cutoff we have chosen, because there was no cutoff in the prompt.
    generated_cutoff: datetime | None
    # Options have been already applied to the model.
    model: Model

    def __init__(self, owner: _StandardExpertModel, command: _StandardExpertCommand | None, prompt: ChatBranch, scope: Scope | None, cutoff: datetime | None, model: Model):
        self.owner = owner
        self.expert = owner.expert
        self.memory = owner.memory
        self.command = command
        self.prompt = prompt
        self.scope = scope
        self.given_cutoff = cutoff
        self.generated_cutoff = None
        self.model = model

    # Effective cutoff, either the one from the prompt or the one we generated.
    @property
    def cutoff(self) -> datetime:
        if self.given_cutoff:
            return self.given_cutoff
        # Even if we don't generate automatic cutoff into the response, we always use it internally, so that cutoff is never None.
        if not self.generated_cutoff:
            self.generated_cutoff = llobot.time.now()
        return self.generated_cutoff

    # Whether we are sending automatically generated cutoff in the next response.
    @property
    def automatic_cutoff(self) -> bool:
        # We will only generate cutoff into our first response, because that's the only place where we are looking for it.
        # If the user edits it out of the first response, we don't fight it and just use current time.
        return not self.given_cutoff and len(self.prompt) == 1

    @property
    def zone(self) -> str:
        return self.memory.zone_name(self.scope)

    # To make token length reasonably stable, we will cache it for some time.
    # Default @lru_cache has 128 entries, which is plenty even if the user runs several concurrent queries.
    # We will add cutoff to the parameters even though it's not used, because we want to refresh token length when starting a new chat.
    # Cutoff is usually unique enough, but the other two parameters are needed anyway to compute the token length.
    #
    # Note that we cannot have an archive of historical token lengths and just access it by cutoff,
    # because model, model options, expert behavior, and context content might have changed meantime.
    # We always want to use the most recent token length estimate even when reprocessing historical chats.
    @staticmethod
    @lru_cache
    def cached_token_length(model: Model, zone: str, cutoff: datetime) -> int:
        return model.estimate_token_length(zone)

    @property
    def token_length(self) -> int:
        return self.cached_token_length(self.model, self.zone, self.cutoff)

    def estimate_chars(self, tokens: float) -> int:
        return int(tokens * self.token_length)

    def estimate_tokens(self, chars: float) -> int:
        return int(chars / self.token_length)

    @property
    def budget(self) -> int:
        return self.estimate_chars(self.model.context_size)

    def stuff(self, prompt: ChatBranch | None = None) -> Context:
        prompt = prompt or self.prompt
        request = ExpertRequest(memory=self.memory, prompt=prompt[0].content, scope=self.scope, cutoff=self.cutoff, budget=self.budget, cache=self.model.cache)
        return self.expert.stuff(request)

    def assemble(self, prompt: ChatBranch | None = None) -> ChatBranch:
        return self.stuff(prompt).chat + (prompt or self.prompt)

    def warmup(self) -> ModelStream:
        assembled = self.assemble(self.prompt[:-1] + ChatRole.USER.message('Now just respond with "Okay" to confirm you are paying attention. Do not say anything else.'))
        return (self.model.generate(assembled, self.zone)
            | llobot.models.streams.silence()
            | llobot.models.streams.notify(lambda stream: _logger.info(f'Ready: {self.zone} ({stream.stats().prompt_tokens or 0:,} tokens)')))

    def calibrate(self):
        # Loop in case the token estimator needs several rounds to be fully initialized.
        while not self.model.calibrated(self.zone):
            _logger.info(f'Calibrating: {self.zone}')
            self.warmup().receive_all()
            # If we generated cutoff as part of the warmup, clear it,
            # so that the next round of warmup or subsequent prompt assembly use fresh token length.
            self.generated_cutoff = None

    def cutoff_footer(self) -> ModelStream:
        return llobot.models.streams.completed(f'`:{llobot.time.format(self.cutoff)}`')

    def add_metadata(self, chat: ChatBranch) -> ChatBranch:
        return chat.with_metadata(ChatMetadata(
            model=self.model.name,
            options=self.model.options,
            cutoff=self.cutoff
        ))

    def handle_hi(self) -> ModelStream:
        self.calibrate()
        stream = self.warmup() + llobot.models.streams.ok('Ready.')
        if self.automatic_cutoff:
            stream += self.cutoff_footer()
        return stream

    def handle_ok(self) -> ModelStream:
        if len(self.prompt) < 3:
            return llobot.models.streams.error('Nothing to save.')
        self.memory.save_example(self.add_metadata(self.assemble(self.prompt[:-2]) + self.prompt[-2]), self.scope)
        return llobot.models.streams.ok('Saved.')

    def handle_echo(self) -> ModelStream:
        self.calibrate()
        # We don't want any header or cutoff here, because output of echo might be pasted into other chat interfaces.
        return llobot.models.streams.completed(self.assemble().monolithic())

    @staticmethod
    def format_model(model: Model) -> str:
        aliases = list(model.aliases)
        if aliases:
            aliases = ', '.join([f'`@{alias}`' for alias in aliases])
            aliases = f' ({aliases})'
        else:
            aliases = ''
        return f'`@{model.name}`{aliases}'

    @staticmethod
    def format_scope(scope: Scope) -> str:
        return f'- `~{scope.name}`\n' + indent(''.join([_StandardExpertRequest.format_scope(child) for child in scope.children]), '  ')

    def handle_info(self) -> ModelStream:
        self.calibrate()
        info = dedent(f'''\
            Configuration:

            - Expert: {self.memory.name}
            - Model: `@{self.model.name}`
            - Cutoff: `:{llobot.time.format(self.cutoff)}`
        ''')
        model = self.model
        token_length = model.estimate_token_length(self.zone)
        info += dedent(f'''
            Model:

            - Name: `@{model.name}`
            - Options: `{model.options}`
            - Aliases: {', '.join([f'`@{alias}`' for alias in model.aliases]) if model.aliases else '-'}
            - Context window: {model.context_size // 1024:,}K tokens, ~{model.context_size * token_length / 1024:,.0f} KB @ ~{token_length:.1f} token length
        ''')
        if self.scope:
            knowledge = self.scope.project.knowledge(self.cutoff)
            info += dedent(f'''
                Project:

                - Name: `~{self.scope.project.name}`
                - Knowledge: {len(knowledge):,} documents, {knowledge.cost / 1024:,.0f} KB
            ''')
            scope_knowledge = knowledge & self.scope.subset
            info += dedent(f'''
                Scope:

                - Name: `~{self.scope.name}`
                - Knowledge: {len(scope_knowledge):,} documents, {scope_knowledge.cost / 1024:,.0f} KB
                - Ancestor chain: {', '.join([f'`~{ancestor.name}`' for ancestor in self.scope.ancestry])}
            ''')
        context = self.stuff()
        if context:
            context_knowledge = sum(chunk.cost for chunk in context if chunk.knowledge or chunk.deletions)
            context_outdated = sum(chunk.cost for chunk in context if chunk.knowledge and chunk.knowledge != (context.knowledge & chunk.knowledge.keys()) or chunk.deletions)
            context_examples_cost = sum(example.cost for example in context.examples)
            info += dedent(f'''
                Context:

                - Size: {len(context):,} chunks, {context.pretty_cost}
                - Knowledge: {len(context.knowledge):,} documents, {context.knowledge.cost / 1024:,.0f} KB, \
                  {context_knowledge / context.cost:.0%} of context, \
                  {context_outdated / context_knowledge if context_knowledge else 0:.0%} outdated, \
                  {1 - context.knowledge.cost / context.knowledge_cost.total() if context.knowledge_cost else 0:.0%} formatting overhead
                - Examples: {len(context.examples):,} examples, {context_examples_cost / 1024:,.0f} KB, \
                  {context_examples_cost / context.cost:.0%} of context
                - Structure: {context.pretty_structure()}
            ''')
        assembled = self.assemble()
        assembled_chars = assembled.cost
        assembled_tokens = self.estimate_tokens(assembled_chars)
        info += dedent(f'''
            Assembled prompt:

            - Size: {len(assembled):,} messages, {assembled.pretty_cost}, ~{assembled_tokens/ 1024:,.0f}K tokens
            - Structure: {assembled.pretty_structure()}
        ''')
        info += dedent('''
            Header help:

            - Structure: `~scope:cutoff@model?k1=v1&k2=v2!command`
            - All parts of the header are optional. Defaults will be substituted automatically.
            - Header may be placed at the top or bottom of the prompt (the first message).
            - Command may be specified separately at the top of a later message.

            Command help:

            - `!hi`: Warm up the model.
            - `!ok`: Save this chat as an example.
            - `!echo`: Output the assembled prompt instead of sending it to the model.
            - `!info`: Show this message.
            - If no command is given, the prompt is submitted to the model.
        ''')
        info += '\nModels:\n\n' + '\n'.join([f'- {self.format_model(model)}' for model in self.owner.alternatives]) + '\n'
        if self.owner.projects:
            info += '\nProjects:\n\n' + '\n'.join([self.format_scope(project.scope) for project in self.owner.projects]) + '\n'
        if context.knowledge:
            info += '\nKnowledge in context:\n\n' + '\n'.join([f'- `{path}`' for path in context.knowledge.keys().sorted()]) + '\n'
        if self.scope:
            for scope in self.scope.ancestry:
                info += f'\nKnowledge in `~{scope.name}`:\n\n' + '\n'.join([f'- `{path}`' for path in (knowledge.keys() & scope.subset).sorted()]) + '\n'
        return llobot.models.streams.status(info)

    def handle_prompt(self) -> ModelStream:
        self.calibrate()
        assembled = self.assemble()
        output = self.model.generate(assembled, self.zone)
        save_filter = llobot.models.streams.notify(lambda stream: self.memory.save_chat(self.add_metadata(assembled + ChatRole.ASSISTANT.message(stream.response())), self.scope))
        inner = output | save_filter
        if self.automatic_cutoff:
            inner += self.cutoff_footer()
        return inner | llobot.models.streams.handler(callback=lambda: _logger.error(f'Exception in {self.model.name} model ({self.memory.name} expert).', exc_info=True))

    def handle(self) -> ModelStream:
        if self.scope and len(self.prompt) == 1 and not self.given_cutoff:
            self.scope.project.refresh()
        if self.command == _StandardExpertCommand.HI:
            return self.handle_hi()
        elif self.command == _StandardExpertCommand.OK:
            return self.handle_ok()
        elif self.command == _StandardExpertCommand.ECHO:
            return self.handle_echo()
        elif self.command == _StandardExpertCommand.INFO:
            return self.handle_info()
        else:
            return self.handle_prompt()

class _StandardExpertModel(Model):
    expert: Expert
    memory: ExpertMemory
    backend: Model
    alternatives: ModelCatalog
    projects: list[Project]

    def __init__(self, expert: Expert, memory: ExpertMemory, backend: Model, alternatives: ModelCatalog, projects: list[Project]):
        self.expert = expert
        self.memory = memory
        self.backend = backend
        self.alternatives = alternatives | ModelCatalog(backend)
        self.projects = projects

    @property
    def name(self) -> str:
        return f'expert/{self.memory.name}'

    @property
    def context_size(self) -> int:
        # This doesn't matter. Just propagate one from the primary model.
        return self.backend.context_size

    @property
    def estimator(self) -> TokenLengthEstimator:
        return llobot.models.estimators.optimistic()

    HEADER_RE = re.compile(r'(?:~([a-zA-Z0-9_/.-]+))?(?::([0-9-]+))?(?:@([a-zA-Z0-9:/._-]+))?(?:\?(\S+))?(?:!([a-z]+))?')
    CUTOFF_RE = re.compile(r'`:([0-9-]+)`')
    COMMAND_RE = re.compile(r'!([a-z]+)')

    def decode_scope(self, name: str) -> Scope:
        for project in self.projects:
            found = project.find(name)
            if found:
                return found
        llobot.models.streams.fail(f'No such project scope: {name}')

    def decode_command(self, name: str) -> _StandardExpertCommand:
        for command in _StandardExpertCommand:
            if command.value == name:
                return command
        llobot.models.streams.fail(f'Invalid command: {name}')

    def decode_options(self, query: str) -> dict:
        options = {}
        for pair in query.split('&'):
            if '=' not in pair:
                llobot.models.streams.fail(f'Invalid model option: {pair}')
            key, value = pair.split('=', maxsplit=1)
            options[key] = value if value else None
        return options

    def decode_header_line(self, line: str) -> tuple[Scope | None, datetime | None, _StandardExpertCommand | None, Model, dict | None] | None:
        if not line:
            return None
        m = _StandardExpertModel.HEADER_RE.fullmatch(line.strip())
        if not m:
            return None
        scope = self.decode_scope(m[1]) if m[1] else None
        cutoff = llobot.time.parse(m[2]) if m[2] else None
        model = self.alternatives[m[3]] if m[3] else self.backend
        options = self.decode_options(m[4]) if m[4] else None
        command = self.decode_command(m[5]) if m[5] else None
        return [scope, cutoff, command, model, options]

    def decode_message_header(self, message: str) -> tuple[Scope | None, datetime | None, _StandardExpertCommand | None, Model, dict | None]:
        lines = message.strip().splitlines()
        if lines:
            top = self.decode_header_line(lines[0])
            bottom = self.decode_header_line(lines[-1]) if len(lines) > 1 else None
            if top and bottom:
                llobot.models.streams.fail('Command header is both at the top and bottom of the message.')
            if top:
                return top
            if bottom:
                return bottom
        return [None, None, None, self.backend, None]

    def decode_automatic_cutoff(self, message: str) -> datetime | None:
        lines = message.strip().splitlines()
        if not lines:
            return None
        m = _StandardExpertModel.CUTOFF_RE.fullmatch(lines[-1])
        return llobot.time.parse(m[1]) if m else None

    def decode_command_message(self, message: str) -> _StandardExpertCommand | None:
        lines = message.strip().splitlines()
        if not lines:
            return None
        m = _StandardExpertModel.COMMAND_RE.fullmatch(lines[0].strip())
        if not m:
            return None
        for command in _StandardExpertCommand:
            if command.value == m[1]:
                return command
        llobot.models.streams.fail(f'Invalid command: {m[1]}')

    def decode_chat_header(self, chat: ChatBranch) -> tuple[Scope | None, datetime | None, _StandardExpertCommand | None, Model, dict | None]:
        scope, cutoff, command, model, options = self.decode_message_header(chat[0].content)
        # If initial message contains nothing but header (or nothing at all), we implicitly interpret it as warmup request.
        if not command and self.clean_message_header(chat[0].content) == '':
            command = _StandardExpertCommand.HI
            if len(chat) > 1:
                llobot.models.streams.fail('Followup message to an empty initial message.')
        if len(chat) > 1:
            if command:
                llobot.models.streams.fail('Followup message even though command was given.')
            automatic_cutoff = self.decode_automatic_cutoff(chat[1].content)
            if automatic_cutoff:
                if cutoff:
                    llobot.models.streams.fail('Duplicate cutoff.')
                cutoff = automatic_cutoff
            for message in chat[1:-1]:
                if message.role == ChatRole.USER and self.decode_command_message(message.content):
                    llobot.models.streams.fail('Followup message after a command.')
            command = self.decode_command_message(chat[-1].content)
        return scope, cutoff, command, model, options

    def clean_message_header(self, message: str) -> str:
        lines = message.strip().splitlines()
        if lines and self.decode_header_line(lines[0]):
            lines = lines[1:]
        if lines and self.decode_header_line(lines[-1]):
            lines = lines[:-1]
        return '\n'.join(lines).strip()

    def clean_automatic_cutoff(self, message: str) -> str:
        lines = message.strip().splitlines()
        if not lines:
            return message
        m = _StandardExpertModel.CUTOFF_RE.fullmatch(lines[-1])
        if not m:
            return message
        # The rstrip() call here will modify the response if it contains extraneous newlines.
        # We don't care, because cache invalidation at the end of the current chat wouldn't do perceptible harm.
        return '\n'.join(lines[:-1]).rstrip()

    def clean_command_message(self, message: str) -> str:
        lines = message.strip().splitlines()
        if not lines:
            return message
        m = _StandardExpertModel.COMMAND_RE.fullmatch(lines[0].strip())
        if not m:
            return message
        return '\n'.join(lines[1:]).strip()

    def clean_chat(self, chat: ChatBranch) -> ChatBranch:
        clean = ChatBuilder()
        clean.add(chat[0].with_content(self.clean_message_header(chat[0].content)))
        if len(chat) >= 2:
            clean.add(chat[1].with_content(self.clean_automatic_cutoff(chat[1].content)))
        if len(chat) >= 3:
            for message in chat[2:-1]:
                clean.add(message)
            clean.add(chat[-1].with_content(self.clean_command_message(chat[-1].content)))
        return clean.build()

    def decode_request(self, prompt: ChatBranch) -> _StandardExpertRequest:
        scope, cutoff, command, model, options = self.decode_chat_header(prompt)
        clean = self.clean_chat(prompt)
        if options:
            model.validate_options(options)
            model = model.configure(options)
        return _StandardExpertRequest(self, command, clean, scope, cutoff, model)

    def _connect(self, prompt: ChatBranch) -> ModelStream:
        try:
            return self.decode_request(prompt).handle()
        except ModelException as ex:
            return ex.stream
        except Exception as ex:
            _logger.error(f'Exception in {self.name} model.', exc_info=True)
            return llobot.models.streams.exception(ex)

def standard(*args) -> Model:
    return _StandardExpertModel(*args)

__all__ = [
    'standard',
]

