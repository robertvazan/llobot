# Llobot

Llobot is a LLM library and a LLM tool that makes it easier to build simple conversational LLM applications or bots. To get started, define models, roles, and projects and then chat with them in any LLM frontend that supports OpenAI or Ollama protocol. Every role defines what the context looks like, including system prompt, knowledge (project files), and recent history. Recent history can be external (like git log), but llobot has special support for live examples, which are user-approved responses from previous conversations.

Llobot also has some nice features:

- **Protocol implementations**: Llobot can connect to local models (Ollama, OpenAI-compatible) as well as cloud models (OpenAI, Anthropic Claude, Google Gemini, OpenAI-compatible). It can also act as a server and expose virtual models via Ollama and OpenAI protocols.
- **Context stuffing**: Instead of relying on the LLM to fetch the necessary files in an agentic loop, knowledge can be stuffed into the context proactively, which is usually cheaper and faster.
- **Live examples**: When you mark LLM response (or user-provided demonstration) as correct, it will be included in future contexts as an example to leverage [in-context learning](https://arxiv.org/abs/2005.14165). Simple LLM applications (translations, conversions) can be built by just accumulating correct examples.
- **Modular instructions**: You can assemble your system prompt from reusable sections. Llobot includes some predefined sections.
- **Knowledge management**: You can load, filter, transform, and time-travel plaintext knowledge bases and source code.
- **Formatters**: Llobot builds clean prompts consisting of several chat turns using readable Markdown for easier auditing.
- **Crammers**: Llobot's crammers select the most important information that fits in given context budget.
- **Scrapers**: Llobot can scrape documents for links and source code for dependencies to build knowledge graph, which is processed with PageRank to prioritize core files for context stuffing.
- **Scorers**: Llobot can prioritize files in the knowledge base by position in knowledge graph (see scrapers above), file name patterns, selected subproject, and file size.
- **Cache-friendly prompts**: Prompts are assembled in reproducible order from whole documents to minimize cache invalidations.

There is currently no support for agentic loops, RAG, uploads, URLs, or actions/approvals, although these features could be added in the future.

## Setup

Llobot is highly configurable, but let's consider a very basic example that mostly relies on defaults. Llobot is a Python library, so we need a short Python script to configure it. The script assumes you have llobot cloned locally under `~/Sources/llobot`.

```python
import sys
from pathlib import Path

# Llobot is not in pip yet, so let's just add the repository to Python's module path.
sys.path.insert(0, str(Path.home() / 'Sources' / 'llobot'))

from llobot.models.catalogs import ModelCatalog
import llobot.models.ollama
import llobot.models.gemini
import llobot.models.anthropic
import llobot.projects
import llobot.knowledge.sources
from llobot.roles.coder import Coder
from llobot.roles.models import RoleModel
import llobot.models.ollama.listeners

# Backend models that respond to the assembled prompt
models = ModelCatalog(
    # This will use qwen2.5-coder:7b on localhost instance of Ollama.
    llobot.models.ollama.create(
        'qwen2.5-coder',
        # Context size has to be always specified, because Ollama defaults are tiny.
        24 * 1024,
        aliases=['local']
    ),
    llobot.models.gemini.create(
        'gemini-2.5-flash',
        auth='YOUR_GOOGLE_API_KEY',
        aliases=['cloud']
    ),
    llobot.models.anthropic.create(
        'claude-sonnet-4-0',
        auth='YOUR_ANTHROPIC_API_KEY',
        aliases=['claude']
    ),
)

# Projects that will be used as knowledge bases
projects = [
    llobot.projects.create('llobot',
        llobot.knowledge.sources.directory(Path.home() / 'Sources' / 'llobot')),
    llobot.projects.create('myproject',
        llobot.knowledge.sources.directory(Path.home() / 'Sources' / 'myproject')),
]

# Roles determine what goes in the context.
# Lets use some standard roles that come with llobot.
roles = [
    Coder('coder', models['local'], projects=projects),
]

# Create virtual models for all roles.
bots = ModelCatalog(*[RoleModel(role) for role in roles])

# Backend Ollama listens on 11434, so we will listen on 11435 to avoid conflicts.
llobot.models.ollama.listeners.create(bots, port=11435).listen()
```

Run this script and add `localhost:11435` as an additional Ollama endpoint to your UI frontend (like Open WebUI, which is [no longer open source](https://github.com/open-webui/open-webui/issues/13579), so feel free to look for alternatives). You should now see the virtual model `coder` listed in the UI.

## How to use

You should now be able to issue queries against the bots. Select `coder` bot and submit this prompt:

> @llobot How do I connect to remote Ollama instance?

The `@llobot` mention is a command that tells the bot to use the `llobot` project as its knowledge base. If you wanted to work on `myproject`, you would write `@myproject`. The mention can be placed anywhere in the prompt, but it's conventional to put it at the beginning. When you submit this prompt, you should get a response like this:

> Use `llobot.models.ollama.remote(host, port, path)` to get the endpoint URL, then pass it to `llobot.models.ollama.create()` as the `endpoint` argument. For example:
>
> ```python
> endpoint = llobot.models.ollama.remote('remote.host.com', 11434)
> model = llobot.models.ollama.create('qwen2.5-coder', 24 * 1024, endpoint=endpoint)
> ```

NB: Response this informative relies on using a large model and on having prior related conversations with the bot. For comparison, response from 'qwen2.5-coder' without prior conversations is below. It's close, but it's not quite there.

> To connect to a remote Ollama instance, you need to use the `remote()` function from the `ollama/endpoints.py` module. Here's an example of how to do it:
>
> ```python
> from llobot.models.ollama.endpoints import remote
>
> # Replace 'host' and 'port' with the actual host and port of your Ollama instance.
> endpoint = remote(host='your-ollama-host', port=11434)
> ```
>
> This will give you an endpoint string that you can use to interact with the remote Ollama instance.

If the context does not include the file you need, just mention it in the prompt, for example as `projects.py` or `ollama/listeners.py`, and llobot will include it in the context in addition to default knowledge.

## Best practices

Here are some practical tips for using llobot:

- Llobot works best with cloud models, which have plenty of burst compute to handle reprocessing of large prompts. Cloud models are also smart enough to be useful.
- Make every task meaningful on its own. Do not reference prior conversations. This will give llobot freedom to choose how many examples to put in the context.
- If the prompt absolutely depends on the model seeing a particular file, mention it in the prompt as `file.ext` or `path/prefix/file.ext` (in backticks), whichever is sufficiently unique to match only one file. This ensures the document will be added to the assembled prompt regardless of how llobot prioritizes documents for context stuffing.
- It is a good idea to standardize on knowledge base organization that prefixes every path with name of the project even if there's currently only one in the context. So if you are loading knowledge from directory `myproject`, then path `subdir/file.txt` would be mapped to `myproject/subdir/file.txt` in the knowledge base.

## Status

Experimental. Undocumented. Untested. Incomplete. Unstable APIs. Likely some bugs. But it works for me and I hope others might find it useful too.
