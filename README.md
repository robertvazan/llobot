[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner2-direct.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md)

# Llobot

Llobot is a LLM library and a LLM tool that makes it easier to build simple conversational LLM applications or bots. To get started, define models, roles, and projects and then chat with them in any LLM frontend that supports OpenAI or Ollama protocol. Every role defines what the context looks like, including system prompt, knowledge (project files), and recent history. Recent history can be external (like git log), but llobot has special support for live examples, which are user-approved responses from previous conversations.

Llobot also has some nice features:

- **Protocol implementations:** Llobot can connect to local models (Ollama) as well as cloud models (OpenAI, Anthropic Claude, Google Gemini). It can also act as a server and expose virtual models via Ollama and OpenAI protocols.
- **Context stuffing:** Instead of relying on the LLM to fetch the necessary files in an agentic loop, knowledge can be stuffed into the context proactively, which has [several advantages](https://blog.machinezoo.com/Why_context_stuffing) over agentic retrieval.
- **Live examples:** When you approve a LLM response (or a user-provided correction), it will be included in future contexts as an example to leverage [in-context learning](https://arxiv.org/abs/2005.14165). Simple LLM applications (translations, conversions) can be built by just accumulating correct examples.
- **Commands and mentions:** Every role can define a set of `@mention` commands that users can add to prompts. Llobot offers built-in commands for project selection (`@project`), file retrieval (`@path/to/file`), and example approval (`@approve`).
- **Modular instructions:** You can assemble your system prompt from reusable sections. Llobot includes some predefined sections.
- **Knowledge management:** You can load, filter and diff plaintext knowledge bases and source code.
- **Context budget:** Llobot can select the most important information that fits in given context budget. Knowledge base can be prioritized using PageRank, file name patterns, and file size.
- **Directory overviews:** Roles capable of editing files are by default instructed to create and maintain directory overview files, including `README.md`, docs in `__init__.py`, `mod.rs`, and similar files, and project information in `CONTRIBUTING.md`, `AGENTS.md`, etc. Overviews are added to the context before covered files to give the model basic understanding of the wider context.
- **Clean context:** Llobot builds clean context consisting of several chat turns using readable Markdown for easier auditing.
- **Cache-friendly:** Context is assembled in reproducible order from whole documents to minimize cache invalidations.

There is currently no support for CLI, agentic loops, RAG, uploads, or URLs, although these features could be added in the future.

## Setup

Llobot is highly configurable, but let's consider a very basic example that mostly relies on defaults. Llobot is a Python library, so we need a short Python script to configure it. The script assumes you have llobot cloned locally under `~/Sources/llobot`.

```python
import sys
from pathlib import Path

# Llobot is not in pip yet, so let's just add the repository to Python's module path.
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

# Backend models that respond to the assembled prompt.
models = NamedModelLibrary(
    # This will use qwen2.5-coder on localhost instance of Ollama.
    OllamaModel('local', model='qwen2.5-coder', num_ctx=24 * 1024),
    GeminiModel(
        'cloud',
        model='gemini-2.5-flash',
        auth='YOUR_GOOGLE_API_KEY'
    ),
    AnthropicModel(
        'frontier',
        model='claude-sonnet-4-5',
        auth='YOUR_ANTHROPIC_API_KEY'
    ),
)
default_model = models['local']

# Projects that will be used as knowledge bases.
# HomeProjectLibrary looks up projects under given directory.
# You can @-mention relative paths under this directory as projects.
projects = HomeProjectLibrary('~/Sources')

# Roles determine what goes in the context.
# Lets use some standard roles that come with llobot.
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
        'reader',
        default_model,
        prompt="Respond with summary of the provided article. Then answer questions.",
    ),
]

# Create virtual models for all roles.
role_models = [RoleModel(role) for role in roles]

# Backend Ollama listens on 11434, so we will listen on 11435 to avoid conflicts.
OllamaListener(*role_models, port=11435).listen()
```

Run this script and add `localhost:11435` as an additional Ollama endpoint to your UI frontend (like Open WebUI, which is [no longer open source](https://github.com/open-webui/open-webui/issues/13579), so feel free to look for alternatives). You should now see virtual models `coder`, `editor`, `translator`, and `reader` listed in the UI.

## How to use

You should now be able to issue queries against the bots. Select `coder` bot and submit this prompt:

> @llobot How do I connect to remote Ollama instance?

The `@llobot` mention is a command that tells the bot to use the `llobot` project as its knowledge base. If you wanted to work on `myproject`, you would write `@myproject`. The mention can be placed anywhere in the prompt. When you submit this prompt, you should get a response like this:

> Use `remote_ollama_endpoint(host, port, path)` from `llobot.models.ollama.endpoints` module to get the endpoint URL, then pass it to the `OllamaModel` constructor as the `endpoint` argument. For example:
>
> ```python
> endpoint = remote_ollama_endpoint('remote.host.com', 11434)
> model = OllamaModel('my-remote-model', model='qwen2:7b', num_ctx=24 * 1024, endpoint=endpoint)
> ```

NB: Response this informative relies on using a large model. For comparison, response from 'qwen2.5-coder'. It's close, but it's not quite there.

> To connect to a remote Ollama instance, you need to use the `remote_ollama_endpoint()` function from the `ollama/endpoints.py` module. Here's an example of how to do it:
>
> ```python
> from llobot.models.ollama.endpoints import remote_ollama_endpoint
>
> # Replace 'host' and 'port' with the actual host and port of your Ollama instance.
> endpoint = remote_ollama_endpoint(host='your-ollama-host', port=11434)
> ```
>
> This will give you an endpoint string that you can use to interact with the remote Ollama instance.

If the context does not already include the file you need, just mention it in the prompt, for example as `@README.md` or `` @`ollama/listeners.py` ``, and llobot will include it in the context in addition to default knowledge.

## Best practices

Here are some practical tips for using llobot:

- Llobot works best with cloud models, which have plenty of burst compute to handle reprocessing of large prompts. Cloud models are also smart enough to be useful.
- Make every task meaningful on its own. Do not reference prior conversations. Even if examples from prior conversations are included in the context, you don't know how many of them actually fit in the context.
- If the prompt absolutely depends on the model seeing a particular file, mention it in the prompt as `@file.ext` or `@path/to/file.ext`, whichever is sufficiently unique to match only one file. This ensures the document will be added to the assembled prompt regardless of how llobot prioritizes documents for context stuffing.
- Instead of one large project, it is better to have several smaller ones. If you need to reference files across projects, just mention multiple projects in the prompt, for example `@project1` and `@project2`. By convention, project name is the first component of the file path.

## Status

Experimental. Partially tested and documented. Unstable APIs. No release. Likely some bugs. But it works for me and I hope others might find it useful too.

## Feedback

Bug reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is distributed under the [Apache License 2.0](LICENSE).
