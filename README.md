[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)

# Llobot

Llobot is a Python LLM agent framework. To get started, define roles, start the server, and point [llms.py](https://llmspy.org/) or another frontend to it. Roles have associated models, projects, and tools. A role defines what the LLM sees and what it can do.

## Features

Llobot differs from other LLM frameworks in several ways:

- **Programmable:** While there are example roles bundled with Llobot, the primary use case is defining business-specific roles. Llobot provides basic building blocks as a modular and configurable Python API.
- **Chat UI:** To ease role development, Llobot does not have any user interface. You can talk to roles in any chat UI that supports OpenAI or Ollama protocols. Roles may recognize commands with `@mention` syntax.
- **Projects:** Instead of granting LLMs unrestricted access to your computer, Llobot usually only allows access to projects `@mentioned` in the prompt. Individual projects as well as the Llobot server itself can be sandboxed.
- **Overviews:** By default, roles with file access are instructed to maintain per-directory overview files like `__init__.py` in Python or `README.md`. Judicious use of overview files can replace a lot of specialized LLM configuration (let me count: `AGENTS.md`, memory, skills, source maps, RAG, connectors, MCP servers, and search).
- **Context stuffing:** By default, Llobot provides the model with a list of project files (up to some limit) and root overview files (`README.md`, `CONTRIBUTING.md`, project configuration). You can optionally preload the most referenced files or whole projects.
- **Non-agentic roles:** Besides standard agents with tools, Llobot lets you define non-agentic roles. Plain chatbots just have a custom system prompt. Simple imitator roles have previously approved/corrected examples (input-output pairs) in the context.

## Setup

Llobot is highly configurable, but let's consider a very basic example that mostly relies on defaults. Llobot is a Python library, so we need a short Python script to configure it. The script assumes you have Llobot cloned locally under `~/Sources/llobot`.

```python
import sys
from pathlib import Path

# Llobot is not in PyPI yet, so let's just add the repository to Python's module path.
sys.path.insert(0, str(Path.home() / 'Sources' / 'llobot'))

from llobot.models.anthropic import AnthropicModel
from llobot.models.gemini import GeminiModel
from llobot.models.library.named import NamedModelLibrary
from llobot.models.listeners.ollama import OllamaListener
from llobot.models.ollama import OllamaModel
from llobot.projects.library.home import HomeProjectLibrary
from llobot.roles.chatbot import Chatbot
from llobot.roles.coder import Coder
from llobot.roles.editor import Editor
from llobot.roles.imitator import Imitator
from llobot.roles.models import RoleModel
from llobot.roles.router import Router

# Backend models that respond to the assembled prompt.
# You can @mention them to override the default model.
models = NamedModelLibrary(
    # This will use qwen2.5-coder on localhost instance of Ollama.
    OllamaModel(name='local', model='qwen2.5-coder', num_ctx=24 * 1024),
    GeminiModel(
        name='flash',
        model='gemini-3-flash-preview',
        auth='YOUR_GOOGLE_API_KEY'
    ),
    AnthropicModel(
        name='sonnet',
        model='claude-sonnet-4-6',
        auth='YOUR_ANTHROPIC_API_KEY',
        max_tokens=8_000,
    ),
)
default_model = models['sonnet']

# Projects that will be used as knowledge bases.
# HomeProjectLibrary looks up projects under given directory.
# You can @mention relative paths under this directory as projects.
projects = HomeProjectLibrary('~/Sources')

# Roles determine what goes in the context.
# Let's use some standard roles that come with Llobot.
roles = [
    Coder('coder', default_model, projects=projects, models=models),
    Editor('editor', default_model, projects=projects, models=models),
    Imitator(
        'translator',
        default_model,
        prompt="Respond to every message with its Spanish translation.",
        models=models,
    ),
    Chatbot(
        'summary',
        default_model,
        prompt="Respond with a summary of the provided article. Then answer questions.",
    ),
]

# Router role that dispatches to whichever role you @mention.
router = Router(roles)

# Backend Ollama listens on 11434, so we will listen on 11435 to avoid conflicts.
OllamaListener(RoleModel(router), port=11435).listen()
```

Run this script and add `localhost:11435` as an additional Ollama endpoint to your UI frontend (like [llms.py](https://llmspy.org/). You should now see virtual model `llobot` listed in the UI.

## How to use

In the UI frontend, select the virtual `llobot` model and submit this prompt:

> @coder @llobot How do I connect to remote Ollama instance?

The `@coder` mention selects the `coder` role. The `@llobot` mention selects the `llobot` project, which is resolved to `~/Sources/llobot` per above configuration. Mentions can be placed anywhere in the prompt. After the agent makes a few tool calls, you should get a response like this:

> Use `remote_ollama_endpoint(host, port, path)` from `llobot.models.ollama.endpoints` module to get the endpoint URL, then pass it to the `OllamaModel` constructor as the `endpoint` argument. For example:
>
> ```python
> endpoint = remote_ollama_endpoint('remote.host.com', 11434)
> model = OllamaModel(name='my-remote-model', model='qwen2:7b', num_ctx=24 * 1024, endpoint=endpoint)
> ```

## Commands

Llobot recognizes several commands in the form of `@mentions`. These can be placed anywhere in the prompt.

- **`@<project>`**: Grants the role access to the project. Name is resolved using configured project library. Example: `@myproject`.
- **`@<model>`**: Selects a different backend model for the response. Name is resolved using configured model library. Example: `@gemini`.
- **`@<file>`**: Preloads a specific file to the context. The file must be present in one of the selected projects. Initial path segments can be omitted. Example: `@README.md`, `@src/main.rs`, or `@tests/*.py`.
- **`@autonomy:<profile>`**: Switches to the specified autonomy profile, which limits consecutive tool calls. Default configuration defines `off`, `step`, `low`, or `high` profiles, defaulting to `high`. Example: `@autonomy:step`.
- **`@approve`**: In roles that support examples (approved input-output pairs), this command approves the previous response as a correct example. It will be added to the context in the future. If any content is provided with the command, it is used instead of the last response.
- **`@run`**: Executes the last batch of tool calls proposed by the model. This command is used when autonomy is disabled.

Mentions can be unquoted as in `@lib.rs` or quoted as in `` @`src/**/*.rs` ``. Quoted mentions are useful when including special symbols in the mention.

## Status

Llobot is fully tested, documented, and used in production, but there is no release or backward compatibility yet.

## Feedback

Bug reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is distributed under the [Apache License 2.0](LICENSE).
