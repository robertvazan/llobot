from __future__ import annotations
from textwrap import dedent
from llobot.projects import Project
from llobot.models import Model
from llobot.models.catalogs import ModelCatalog
from llobot.models.streams import ModelStream
from llobot.knowledge import Knowledge
from llobot.chats import ChatBranch, ChatIntent
import llobot.ui.chatbot.requests
from llobot.ui.chatbot.requests import ChatbotRequest
import llobot.time
import llobot.text
import llobot.models.streams
import llobot.formatters.envelopes

def prompt_structure(chat: ChatBranch) -> str:
    envelopes = llobot.formatters.envelopes.standard()
    codes = {
        ChatIntent.SYSTEM: 'S',
        ChatIntent.EXAMPLE_PROMPT: 'E',
        ChatIntent.PROMPT: 'P',
        ChatIntent.RESPONSE: 'R',
    }
    s = ''
    for message in chat:
        if message.intent == ChatIntent.SYSTEM and envelopes.parse_message(message.content):
            s += 'K'
        else:
            s += codes.get(message.intent, '')
    return ' '.join(s[i:i+10] for i in range(0, len(s), 10))

def config_section(request: ChatbotRequest) -> str:
    return dedent(f'''\
        Configuration:

        - Role: `{request.chatbot.role.name}`
        - Model: `@{request.model.name}`
        - Cutoff: `:{llobot.time.format(request.cutoff)}`''')

def model_section(model: Model) -> str:
    return dedent(f'''\
        Model:

        - Name: `@{model.name}`
        - Options: `{model.options}`
        - Aliases: {', '.join([f'`@{alias}`' for alias in model.aliases]) if model.aliases else '-'}
        - Context budget: {model.context_budget / 1000:,.0f} KB''')

def _project_section(title: str, name: str, knowledge: Knowledge) -> str:
    return dedent(f'''\
        {title}:

        - Name: `~{name}`
        - Knowledge: {len(knowledge):,} documents, {knowledge.cost / 1000:,.0f} KB''')

def project_section(project: Project, knowledge: Knowledge) -> str:
    return _project_section('Project', project.root.name, knowledge)

def subproject_section(project: Project, knowledge: Knowledge) -> str:
    return _project_section('Subproject', project.name, knowledge & project.subset)

def prompt_section(assembled: ChatBranch, knowledge: Knowledge) -> str:
    section = dedent(f'''\
        Assembled prompt:

        - Size: {len(assembled):,} messages, {assembled.pretty_cost}
        - Structure: {prompt_structure(assembled)}''')
    if knowledge:
        section += f'\n- Knowledge: {len(knowledge):,} documents, {knowledge.cost / 1000:,.0f} KB'
    return section

def help_section() -> str:
    return dedent('''\
        Header help:

        - Structure: `~project:cutoff@model?k1=v1&k2=v2!command`
        - All parts of the header are optional. Defaults will be substituted automatically.
        - Header may be placed at the top or bottom of the prompt (the first message).
        - Command may be specified separately at the top of a later message.

        Command help:

        - `!ok`: Save this chat as an example.
        - `!echo`: Output the assembled prompt instead of sending it to the model.
        - `!info`: Show this message.
        - If no command is given, the prompt is submitted to the model.''')

def _format_model(model: Model) -> str:
    aliases = list(model.aliases)
    if aliases:
        aliases = ', '.join([f'`@{alias}`' for alias in aliases])
        aliases = f' ({aliases})'
    else:
        aliases = ''
    return f'`@{model.name}`{aliases}'

def model_list_section(models: ModelCatalog) -> str:
    return 'Models:\n\n' + '\n'.join([f'- {_format_model(model)}' for model in models])

def _format_project_with_subprojects(project: Project) -> str:
    return f'- `~{project.name}`' + ''.join([f'\n  - `~{subproject.name}`\n' for subproject in project.subprojects])

def project_list_section(projects: list[Project]) -> str:
    return 'Projects:\n\n' + '\n'.join([_format_project_with_subprojects(project) for project in projects])

def _knowledge_section(title: str, knowledge: Knowledge) -> str:
    paths = knowledge.keys().sorted()
    if not paths:
        return ''
    file_list = '\n'.join([str(p) for p in paths])
    return llobot.text.details(title, '', file_list)

def context_knowledge_section(knowledge: Knowledge) -> str:
    return _knowledge_section('Context knowledge', knowledge)

def project_knowledge_section(knowledge: Knowledge) -> str:
    return _knowledge_section('Project knowledge', knowledge)

def subproject_knowledge_section(project: Project, knowledge: Knowledge) -> str:
    return _knowledge_section('Subproject knowledge', knowledge & project.subset)

def render_info(request: ChatbotRequest) -> str:
    chatbot = request.chatbot

    sections = [config_section(request), model_section(request.model)]

    knowledge = request.project.root.knowledge(request.cutoff) if request.project else Knowledge()
    if request.project:
        sections.append(project_section(request.project, knowledge))
        if request.project.is_subproject:
            sections.append(subproject_section(request.project, knowledge))

    assembled = llobot.ui.chatbot.requests.assemble(request)
    context_knowledge = llobot.formatters.envelopes.standard().parse_chat(assembled).full
    sections.append(prompt_section(assembled, context_knowledge))

    sections.append(help_section())
    sections.append(model_list_section(chatbot.models))
    if chatbot.projects:
        sections.append(project_list_section(chatbot.projects))

    if context_knowledge:
        sections.append(context_knowledge_section(context_knowledge))
    if request.project:
        if request.project.is_subproject:
            sections.append(subproject_knowledge_section(request.project, knowledge))
        sections.append(project_knowledge_section(knowledge))

    return llobot.text.concat(*sections)

def handle_info(request: ChatbotRequest) -> ModelStream:
    return llobot.models.streams.status(render_info(request))

__all__ = [
    'prompt_structure',
    'config_section',
    'model_section',
    'project_section',
    'subproject_section',
    'prompt_section',
    'help_section',
    'model_list_section',
    'project_list_section',
    'context_knowledge_section',
    'project_knowledge_section',
    'subproject_knowledge_section',
    'render_info',
    'handle_info',
]
