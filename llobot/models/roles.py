from __future__ import annotations
from enum import Enum
from datetime import datetime
from textwrap import dedent
import logging
import re
from llobot.chats import ChatRole, ChatBranch, ChatBuilder, ChatMetadata
from llobot.projects import Project
from llobot.contexts import Context
from llobot.roles import Role
from llobot.models import Model
from llobot.models.catalogs import ModelCatalog
from llobot.models.streams import ModelStream, ModelException
import llobot.time
import llobot.models.streams

_logger = logging.getLogger(__name__)

class _StandardRoleCommand(Enum):
    OK = 'ok'
    ECHO = 'echo'
    INFO = 'info'

class _StandardRoleRequest:
    owner: _StandardRoleModel
    role: Role
    command: _StandardRoleCommand | None
    # Clean user prompt before assembly into the full prompt.
    prompt: ChatBranch
    project: Project | None
    # Cutoff parsed out of the prompt, whether from the header in the first message or from automatic cutoff in the second message.
    given_cutoff: datetime | None
    # Cutoff we have chosen, because there was no cutoff in the prompt.
    generated_cutoff: datetime | None
    # Options have been already applied to the model.
    model: Model

    def __init__(self, owner: _StandardRoleModel, command: _StandardRoleCommand | None, prompt: ChatBranch, project: Project | None, cutoff: datetime | None, model: Model):
        self.owner = owner
        self.role = owner.role
        self.command = command
        self.prompt = prompt
        self.project = project
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
    def budget(self) -> int:
        return self.model.context_budget

    def stuff(self, prompt: ChatBranch | None = None) -> Context:
        prompt = prompt or self.prompt
        return self.role.stuff(
            prompt=prompt,
            project=self.project,
            cutoff=self.cutoff,
            budget=self.budget
        )

    def assemble(self, prompt: ChatBranch | None = None) -> ChatBranch:
        return self.stuff(prompt).chat + (prompt or self.prompt)

    def cutoff_footer(self) -> ModelStream:
        return llobot.models.streams.completed(f'`:{llobot.time.format(self.cutoff)}`')

    def add_metadata(self, chat: ChatBranch) -> ChatBranch:
        return chat.with_metadata(ChatMetadata(
            model=self.model.name,
            options=self.model.options,
            cutoff=self.cutoff
        ))

    def handle_ok(self) -> ModelStream:
        if len(self.prompt) < 3:
            return llobot.models.streams.error('Nothing to save.')
        self.role.save_example(self.add_metadata(self.prompt[:-1]), self.project)
        return llobot.models.streams.ok('Saved.')

    def handle_echo(self) -> ModelStream:
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
    def format_project(project: Project) -> str:
        return f'- `~{project.name}`' + ''.join([f'\n  - `~{subproject.name}`\n' for subproject in project.subprojects])

    def handle_info(self) -> ModelStream:
        info = dedent(f'''\
            Configuration:

            - Role: `{self.role.name}`
            - Model: `@{self.model.name}`
            - Cutoff: `:{llobot.time.format(self.cutoff)}`
        ''')
        info += dedent(f'''
            Model:

            - Name: `@{self.model.name}`
            - Options: `{self.model.options}`
            - Aliases: {', '.join([f'`@{alias}`' for alias in self.model.aliases]) if self.model.aliases else '-'}
            - Context budget: {self.budget / 1024:,.0f} KB
        ''')
        if self.project:
            knowledge = self.project.root.knowledge(self.cutoff)
            info += dedent(f'''
                Project:

                - Name: `~{self.project.root.name}`
                - Knowledge: {len(knowledge):,} documents, {knowledge.cost / 1024:,.0f} KB
            ''')
            if self.project.is_subproject:
                subproject_knowledge = knowledge & self.project.subset
                info += dedent(f'''
                    Subproject:

                    - Name: `~{self.project.name}`
                    - Knowledge: {len(subproject_knowledge):,} documents, {subproject_knowledge.cost / 1024:,.0f} KB
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
        info += dedent(f'''
            Assembled prompt:

            - Size: {len(assembled):,} messages, {assembled.pretty_cost}
            - Structure: {assembled.pretty_structure()}
        ''')
        info += dedent('''
            Header help:

            - Structure: `~project:cutoff@model?k1=v1&k2=v2!command`
            - All parts of the header are optional. Defaults will be substituted automatically.
            - Header may be placed at the top or bottom of the prompt (the first message).
            - Command may be specified separately at the top of a later message.

            Command help:

            - `!ok`: Save this chat as an example.
            - `!echo`: Output the assembled prompt instead of sending it to the model.
            - `!info`: Show this message.
            - If no command is given, the prompt is submitted to the model.
        ''')
        info += '\nModels:\n\n' + '\n'.join([f'- {self.format_model(model)}' for model in self.owner.alternatives]) + '\n'
        if self.owner.projects:
            info += '\nProjects:\n\n' + '\n'.join([self.format_project(project) for project in self.owner.projects]) + '\n'
        if context.knowledge:
            info += '\nKnowledge in context:\n\n' + '\n'.join([f'- `{path}`' for path in context.knowledge.keys().sorted()]) + '\n'
        if self.project:
            # Pack it all into one Markdown code block. This is a workaround for inefficiency in Open WebUI.
            if self.project.is_subproject:
                info += f'\nKnowledge in `~{self.project.name}`:\n\n```\n' + '\n'.join([str(path) for path in (knowledge.keys() & self.project.subset).sorted()]) + '\n```\n'
            info += f'\nKnowledge in `~{self.project.root.name}`:\n\n```\n' + '\n'.join([str(path) for path in knowledge.keys().sorted()]) + '\n```\n'
        return llobot.models.streams.status(info)

    def handle_prompt(self) -> ModelStream:
        assembled = self.assemble()
        output = self.model.generate(assembled)
        save_filter = llobot.models.streams.notify(lambda stream: self.role.save_chat(self.add_metadata(self.prompt + ChatRole.ASSISTANT.message(stream.response())), self.project))
        inner = output | save_filter
        if self.automatic_cutoff:
            inner += self.cutoff_footer()
        return inner | llobot.models.streams.handler(callback=lambda: _logger.error(f'Exception in {self.model.name} model ({self.role.name} role).', exc_info=True))

    def handle(self) -> ModelStream:
        if self.project and len(self.prompt) == 1 and not self.given_cutoff:
            self.project.root.refresh()
        if self.command == _StandardRoleCommand.OK:
            return self.handle_ok()
        elif self.command == _StandardRoleCommand.ECHO:
            return self.handle_echo()
        elif self.command == _StandardRoleCommand.INFO:
            return self.handle_info()
        else:
            return self.handle_prompt()

class _StandardRoleModel(Model):
    role: Role
    backend: Model
    alternatives: ModelCatalog
    projects: list[Project]

    def __init__(self, role: Role, backend: Model, alternatives: ModelCatalog, projects: list[Project]):
        self.role = role
        self.backend = backend
        self.alternatives = alternatives | ModelCatalog(backend)
        self.projects = projects

    @property
    def name(self) -> str:
        return f'bot/{self.role.name}'

    @property
    def context_budget(self) -> int:
        # This doesn't matter. Just propagate one from the primary model.
        return self.backend.context_budget

    HEADER_RE = re.compile(r'(?:~([a-zA-Z0-9_/.-]+))?(?::([0-9-]+))?(?:@([a-zA-Z0-9:/._-]+))?(?:\?([^!\s]+))?(?:!([a-z]+))?')
    CUTOFF_RE = re.compile(r'`:([0-9-]+)`')
    COMMAND_RE = re.compile(r'!([a-z]+)')

    def decode_project(self, name: str) -> Project:
        for project in self.projects:
            found = project.find(name)
            if found:
                return found
        llobot.models.streams.fail(f'No such project: {name}')

    def decode_command(self, name: str) -> _StandardRoleCommand:
        for command in _StandardRoleCommand:
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

    def decode_header_line(self, line: str) -> tuple[Project | None, datetime | None, _StandardRoleCommand | None, Model, dict | None] | None:
        if not line:
            return None
        m = _StandardRoleModel.HEADER_RE.fullmatch(line.strip())
        if not m:
            return None
        project = self.decode_project(m[1]) if m[1] else None
        cutoff = llobot.time.parse(m[2]) if m[2] else None
        model = self.alternatives[m[3]] if m[3] else self.backend
        options = self.decode_options(m[4]) if m[4] else None
        command = self.decode_command(m[5]) if m[5] else None
        return [project, cutoff, command, model, options]

    def decode_message_header(self, message: str) -> tuple[Project | None, datetime | None, _StandardRoleCommand | None, Model, dict | None]:
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
        m = _StandardRoleModel.CUTOFF_RE.fullmatch(lines[-1])
        return llobot.time.parse(m[1]) if m else None

    def decode_command_line(self, line: str) -> _StandardRoleCommand | None:
        m = _StandardRoleModel.COMMAND_RE.fullmatch(line.strip())
        return self.decode_command(m[1]) if m else None

    def decode_command_message(self, message: str) -> _StandardRoleCommand | None:
        lines = message.strip().splitlines()
        if not lines:
            return None
        top = self.decode_command_line(lines[0])
        bottom = self.decode_command_line(lines[-1]) if len(lines) > 1 else None
        if top and bottom:
            llobot.models.streams.fail('Command is both at the top and bottom of the message.')
        return top or bottom

    def decode_chat_header(self, chat: ChatBranch) -> tuple[Project | None, datetime | None, _StandardRoleCommand | None, Model, dict | None]:
        project, cutoff, command, model, options = self.decode_message_header(chat[0].content)
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
        return project, cutoff, command, model, options

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
        m = _StandardRoleModel.CUTOFF_RE.fullmatch(lines[-1])
        if not m:
            return message
        # The rstrip() call here will modify the response if it contains extraneous newlines.
        # We don't care, because cache invalidation at the end of the current chat wouldn't do perceptible harm.
        return '\n'.join(lines[:-1]).rstrip()

    def clean_command_message(self, message: str) -> str:
        lines = message.strip().splitlines()
        if lines and self.decode_command_line(lines[0]):
            lines = lines[1:]
        if lines and self.decode_command_line(lines[-1]):
            lines = lines[:-1]
        return '\n'.join(lines).strip()

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

    def decode_request(self, prompt: ChatBranch) -> _StandardRoleRequest:
        project, cutoff, command, model, options = self.decode_chat_header(prompt)
        clean = self.clean_chat(prompt)
        if options:
            model.validate_options(options)
            model = model.configure(options)
        return _StandardRoleRequest(self, command, clean, project, cutoff, model)

    def generate(self, prompt: ChatBranch) -> ModelStream:
        try:
            return self.decode_request(prompt).handle()
        except ModelException as ex:
            return ex.stream
        except Exception as ex:
            _logger.error(f'Exception in {self.name} model.', exc_info=True)
            return llobot.models.streams.exception(ex)

def standard(*args) -> Model:
    return _StandardRoleModel(*args)

__all__ = [
    'standard',
]

