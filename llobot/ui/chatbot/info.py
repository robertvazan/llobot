from __future__ import annotations
from textwrap import dedent
from llobot.projects import Project
from llobot.models import Model
from llobot.models.catalogs import ModelCatalog
from llobot.models.streams import ModelStream
from llobot.knowledge import Knowledge
from llobot.knowledge.deltas import KnowledgeDelta
from llobot.chats import ChatBranch, ChatIntent
import llobot.ui.chatbot.requests
from llobot.ui.chatbot.requests import ChatbotRequest
import llobot.time
import llobot.text
import llobot.models.streams
import llobot.formatters.envelopes

def format_prompt_structure(chat: ChatBranch) -> str:
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

def render_config(request: ChatbotRequest) -> str:
    chatbot = request.chatbot
    return dedent(f'''\
        Configuration:

        - Role: `{chatbot.role.name}`
        - Model: `@{request.model.name}`
        - Cutoff: `:{llobot.time.format(request.cutoff)}`''')

def _render_model(model: Model) -> str:
    aliases = list(model.aliases)
    if aliases:
        aliases = ', '.join([f'`@{alias}`' for alias in aliases])
        aliases = f' ({aliases})'
    else:
        aliases = ''
    return f'`@{model.name}`{aliases}'

def render_model_details(model: Model) -> str:
    return dedent(f'''
        Model:

        - Name: `@{model.name}`
        - Options: `{model.options}`
        - Aliases: {', '.join([f'`@{alias}`' for alias in model.aliases]) if model.aliases else '-'}
        - Context budget: {model.context_budget / 1000:,.0f} KB''')

def _render_project_knowledge_summary(name: str, knowledge: Knowledge) -> str:
    return dedent(f'''
        - Name: `~{name}`
        - Knowledge: {len(knowledge):,} documents, {knowledge.cost / 1000:,.0f} KB''')

def render_project(project: Project, knowledge: Knowledge) -> str:
    info = "Project knowledge:\n\n" + _render_project_knowledge_summary(project.root.name, knowledge)
    if project.is_subproject:
        info += "\n\nSubproject knowledge:\n\n" + _render_project_knowledge_summary(project.name, knowledge & project.subset)
    return info

def render_assembled_prompt(assembled: ChatBranch) -> str:
    return dedent(f'''
        Assembled prompt:

        - Size: {len(assembled):,} messages, {assembled.pretty_cost}
        - Structure: {format_prompt_structure(assembled)}''')

def render_help() -> str:
    return dedent('''
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

def _format_project_listing(project: Project) -> str:
    return f'- `~{project.name}`' + ''.join([f'\n  - `~{subproject.name}`\n' for subproject in project.subprojects])

def render_models(models: ModelCatalog) -> str:
    return 'Models:\n\n' + '\n'.join([f'- {_render_model(model)}' for model in models])

def render_projects(projects: list[Project]) -> str:
    return 'Projects:\n\n' + '\n'.join([_format_project_listing(project) for project in projects])

def render_context_knowledge(delta: KnowledgeDelta) -> str:
    if not delta:
        return ''
    paths = delta.full.keys().sorted()
    if not paths:
        return ''
    return 'Context knowledge:\n\n```\n' + '\n'.join([str(p) for p in paths]) + '\n```'

def render_knowledge_listing(project: Project, knowledge: Knowledge) -> str:
    info = ''
    if project.is_subproject:
        info += f'\nSubproject knowledge:\n\n```\n' + '\n'.join([str(path) for path in (knowledge.keys() & project.subset).sorted()]) + '\n```\n'
    info += f'\nProject knowledge:\n\n```\n' + '\n'.join([str(path) for path in knowledge.keys().sorted()]) + '\n```'
    return info.strip()

def render_info(request: ChatbotRequest) -> str:
    chatbot = request.chatbot
    
    sections = [render_config(request), render_model_details(request.model)]
    
    knowledge = request.project.root.knowledge(request.cutoff) if request.project else Knowledge()
    if request.project:
        sections.append(render_project(request.project, knowledge))
    
    assembled = llobot.ui.chatbot.requests.assemble(request)
    sections.append(render_assembled_prompt(assembled))
    
    sections.append(render_help())
    sections.append(render_models(chatbot.models))
    if chatbot.projects:
        sections.append(render_projects(chatbot.projects))

    context_delta = llobot.formatters.envelopes.standard().parse_chat(assembled)
    if context_delta:
        sections.append(render_context_knowledge(context_delta))

    if request.project:
        sections.append(render_knowledge_listing(request.project, knowledge))
        
    return llobot.text.concat(*sections)

def handle_info(request: ChatbotRequest) -> ModelStream:
    return llobot.models.streams.status(render_info(request))

__all__ = [
    'format_prompt_structure',
    'render_config',
    'render_model_details',
    'render_project',
    'render_assembled_prompt',
    'render_help',
    'render_models',
    'render_projects',
    'render_context_knowledge',
    'render_knowledge_listing',
    'render_info',
    'handle_info',
]
