from __future__ import annotations
from textwrap import dedent
from llobot.projects import Project
from llobot.models import Model
from llobot.models.streams import ModelStream
import llobot.ui.chatbot.requests
from llobot.ui.chatbot.requests import ChatbotRequest
import llobot.time
import llobot.models.streams

def _format_model(model: Model) -> str:
    aliases = list(model.aliases)
    if aliases:
        aliases = ', '.join([f'`@{alias}`' for alias in aliases])
        aliases = f' ({aliases})'
    else:
        aliases = ''
    return f'`@{model.name}`{aliases}'

def _format_project(project: Project) -> str:
    return f'- `~{project.name}`' + ''.join([f'\n  - `~{subproject.name}`\n' for subproject in project.subprojects])

def handle_info(request: ChatbotRequest) -> ModelStream:
    chatbot = request.chatbot
    info = dedent(f'''\
        Configuration:

        - Role: `{chatbot.role.name}`
        - Model: `@{request.model.name}`
        - Cutoff: `:{llobot.time.format(request.cutoff)}`
    ''')
    info += dedent(f'''
        Model:

        - Name: `@{request.model.name}`
        - Options: `{request.model.options}`
        - Aliases: {', '.join([f'`@{alias}`' for alias in request.model.aliases]) if request.model.aliases else '-'}
        - Context budget: {request.model.context_budget / 1024:,.0f} KB
    ''')
    if request.project:
        knowledge = request.project.root.knowledge(request.cutoff)
        info += dedent(f'''
            Project:

            - Name: `~{request.project.root.name}`
            - Knowledge: {len(knowledge):,} documents, {knowledge.cost / 1024:,.0f} KB
        ''')
        if request.project.is_subproject:
            subproject_knowledge = knowledge & request.project.subset
            info += dedent(f'''
                Subproject:

                - Name: `~{request.project.name}`
                - Knowledge: {len(subproject_knowledge):,} documents, {subproject_knowledge.cost / 1024:,.0f} KB
            ''')
    context = llobot.ui.chatbot.requests.stuff(request)
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
    assembled = llobot.ui.chatbot.requests.assemble(request)
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
    info += '\nModels:\n\n' + '\n'.join([f'- {_format_model(model)}' for model in chatbot.models]) + '\n'
    if chatbot.projects:
        info += '\nProjects:\n\n' + '\n'.join([_format_project(project) for project in chatbot.projects]) + '\n'
    if context.knowledge:
        info += '\nKnowledge in context:\n\n' + '\n'.join([f'- `{path}`' for path in context.knowledge.keys().sorted()]) + '\n'
    if request.project:
        knowledge = request.project.root.knowledge(request.cutoff)
        # Pack it all into one Markdown code block. This is a workaround for inefficiency in Open WebUI.
        if request.project.is_subproject:
            info += f'\nKnowledge in `~{request.project.name}`:\n\n```\n' + '\n'.join([str(path) for path in (knowledge.keys() & request.project.subset).sorted()]) + '\n```\n'
        info += f'\nKnowledge in `~{request.project.root.name}`:\n\n```\n' + '\n'.join([str(path) for path in knowledge.keys().sorted()]) + '\n```\n'
    return llobot.models.streams.status(info)

__all__ = [
    'handle_info',
]
