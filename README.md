# Llobot

Llobot is a LLM library and a LLM tool that makes it easy to build simple conversational LLM applications. It's somewhat general-purpose, but it has a particular focus on:

- **Protocol interception**: Llobot can act as a model server, using Ollama or OpenAI protocol, so that you can use it with standard LLM clients.
- **Examples**: When you mark LLM response (or user-provided demonstration) as correct, it will be prepended to future prompts as an example to leverage [in-context learning](https://arxiv.org/abs/2005.14165). Simple LLM applications (translations, conversions) can be built by just accumulating correct examples.
- **Context stuffing**: Instead of letting the LLM fetch one file at a time in an agentic loop, knowledge is stuffed into the context proactively, which is usually cheaper and faster.

Llobot also supports:

- **Repo packing**: Llobot can do any context stuffing, but it has particularly good support for stuffing code repositories. It can be used as a more powerful alternative to [Repomix](https://repomix.com/), [Gitingest](https://gitingest.com/), or [code2prompt](https://github.com/mufeedvh/code2prompt/).
- **System prompts**: You can stuff arbitrary long texts into the context, including dynamically generated ones.
- **Retrievals**: Any files named in the prompt will be preferentially stuffed into the context.

There is currently no support for reasoning models, agentic loops, RAG, uploads, URLs, or actions/approvals, although these features could be added in the future.

Llobot also has some nice features:

- **Protocol implementations**: Llobot can connect to local and cloud models. It can also act as a server and expose virtual models via Ollama and OpenAI protocols.
- **Modular instructions**: You can assemble your system prompt from reusable sections. Llobot includes some predefined sections.
- **Knowledge management**: You can load, filter, transform, and time-travel plaintext knowledge bases and source code.
- **Formatters**: Llobot builds clean prompts consisting of several chat turns using readable Markdown for easier auditing.
- **Scrapers**: Llobot can scrape documents for links and source code for dependencies to build knowledge graph, which is processed with PageRank to prioritize core files for context stuffing.
- **Crammers**: Llobot's crammers fit the most important information in given budget.
- **Scorers**: Llobot can prioritize files in the knowledge base by position in knowledge graph (see scrapers above), file name patterns, selected subproject, and file size. It can also prioritize examples.
- **Cache-friendly prompts**: Prompts are assembled in reproducible order from whole documents to minimize cache invalidations.

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
import llobot.ui.chatbot
import llobot.models.ollama.listeners

# Backend models that respond to the assembled prompt
backend_models = ModelCatalog(
    # This will use qwen2.5-coder:7b on localhost instance of Ollama.
    llobot.models.ollama.create(
        'qwen2.5-coder',
        # Context size has to be always specified, because Ollama defaults are tiny.
        24 * 1024,
        top_k=1,
        aliases=['local']
    ),
    llobot.models.gemini.create(
        'gemini-2.5-flash-preview-05-20',
        # Context budget limits spending.
        context_budget=25_000,
        temperature=0,
        auth='YOUR_GOOGLE_API_KEY',
        aliases=['cloud']
    ),
    llobot.models.anthropic.create(
        'claude-sonnet-4-0',
        context_budget=25_000,
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
# This function configures bare role to serve as a virtual model.
def define_bot(role):
    # This wraps the role in a virtual model.
    return llobot.ui.chatbot.create(
        role,
        # Default backend model.
        backend_models['local'],
        # Alternative backend models.
        backend_models,
        projects)

# Lets use some standard roles that come with llobot.
bots = ModelCatalog(
    define_bot(Coder('coder')),
)

# Backend Ollama listens on 11434, so we will listen on 11435 to avoid conflicts.
llobot.models.ollama.listeners.create(bots, port=11435).listen()
```

Run this script and add `localhost:11435` as an additional Ollama endpoint to your UI frontend (like Open WebUI, which is [no longer open source](https://github.com/open-webui/open-webui/issues/13579), so feel free to look for alternatives). You should now see the virtual model `coder` listed in the UI.

## How to use

You should now be able to issue queries against the bots. Select `coder` bot and submit this prompt:

> How do I connect to remote Ollama instance?
>
> ~llobot

The last line is a command that tells the bot to use `llobot` project as its knowledge base. If you wanted to work on `myproject`, you would write `~myproject` there. When you submit this prompt, you should get a response like this:

> Use `llobot.models.ollama.remote(host, port, path)` to get the endpoint URL, then pass it to `llobot.models.ollama.create()` as the `endpoint` argument. For example:
>
> ```python
> endpoint = llobot.models.ollama.remote('remote.host.com', 11434)
> model = llobot.models.ollama.create('qwen2.5-coder', 24 * 1024, endpoint=endpoint)
> ```
>
> `:20250526-221039`

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
>
> `:20250526-222015`

The last line is a timestamp that the bot uses to stick to particular version of the knowledge base in case you continue the conversation.

The `~llobot` command in the prompt can be more complicated:

- `~myproject!info` to show help, available options, lots of information
- `~myproject@cloud` to run on backend model that we aliased as `cloud` in the above setup script
- `~myproject!echo` to respond with the whole assembled prompt (good to get an idea what goes in there)

If the context does not include the file you need, just mention it in the prompt, for example as `projects.py` or `ollama/listeners.py`, and llobot will include it in the context in preference to default knowledge.

Finally, if you are happy with the output, issue command `!ok` after the response you like. Llobot will save it as a correct example. Recent examples are included in the context. LLMs have propensity to imitate what is already in the context, so putting correct examples in the context increases probability that the next response will be correct too. If the response is wrong, you can still show llobot how to do it right. Impersonate the LLM (edit the response, a function that is in Open WebUI but not necessarily in other frontends), put there the correct response, and then issue `!ok` command. While this seems laborious, you usually have the correct response anyway in your code, so this is just about letting llobot know about it.

## Best practices

Here are some practical tips for using llobot:

- Llobot works best with cloud models, which have plenty of burst compute to handle reprocessing of large prompts. Cloud models are also smart enough to be useful.
- Make every task meaningful on its own. Do not reference prior conversations. This will give llobot freedom to choose examples and their ordering in the prompt.
- If the prompt absolutely depends on the model seeing a particular file, mention it in the prompt as `file.ext` or `path/prefix/file.ext` (in backticks), whichever is sufficiently unique to match only one file. This ensures the document will be added to the assembled prompt regardless of how llobot prioritizes documents for context stuffing.
- Contemporary LLMs are all divergent. Just letting them run alone on a large task will drive them mad. You have to give them a small task, review the response, correct mistakes, and repeat.
- It's not necessary to be excessively precise in your prompts. LLMs are good at filling in the details. Try minimalist prompt first and refine it iteratively.
- If you have modified your code (or other knowledge base) since querying the LLM and you don't want the changes to be visible to the LLM after you edit the prompt, take the timestamp from llobot's response and add it to the command in your prompt, for example `~myproject:20250526-222015`. Llobot will use the unmodified version of the knowledge base to answer the new prompt.
- It is a good idea to standardize on knowledge base organization that prefixes every path with name of the source directory even if there's currently only one. So if you are loading knowledge from directory `myproject`, then path `subdir/file.txt` would be mapped to `myproject/subdir/file.txt` in the knowledge base.
- Finally, do not use LLMs compulsively for everything. Sometimes it's easier to do things by hand in the editor or to use refactoring tools offered by IDEs.

## Status

Experimental. Undocumented. Untested. Incomplete. Unstable APIs. Likely some bugs. But it works for me and I hope others might find it useful too.
