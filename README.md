# Llobot

Llobot is a LLM context stuffing tool and a Python library. It sits between LLM frontend (chat UI) and inference engine (which is serving the model), intercepts chat completion requests sent via supported LLM chat protocol (Ollama or OpenAI), and manipulates them in some way, usually by prepending large synthetic context. Synthetic context commonly includes system instructions, documents from knowledge base, examples, and optionally prompt-dependent retrievals. While the whole setup is highly configurable, llobot is currently best suited for stuffing the context with source code in order to create expert chatbots that are knowledgeable about particular codebase.

## What is context stuffing?

No, it's not RAG. LLM *context stuffing* (or *prompt stuffing*) leverages [in-context learning](https://arxiv.org/abs/2005.14165) to improve LLM performance. It aims to fill the context window (up to some token budget) with relevant information. What you put in the context is somewhat application-dependent, but it usually includes instructions, documents from knowledge base, real examples (from prior tasks), and prompt-dependent retrievals (usually whole documents referenced by name). This can be complemented with LLM-guided agentic retrieval and digested with reasoning (where supported by the model).

Assembled prompt can then look something like this:

- document1
- ...
- documentN
- example1
- ...
- exampleN
- retrieved_document1
- ...
- retrieved_documentN
- user prompt

Model then responds like this:

- optional agentic loop for LLM-guided retrievals
- optional reasoning
- response

Context stuffing differs from other similar techniques:

- **Repo packing**: Tools like [Repomix](https://repomix.com/), [Gitingest](https://gitingest.com/), and [code2prompt](https://github.com/mufeedvh/code2prompt/) are the closest relative of llobot and the best prior example of context stuffing I could find. Llobot can be thought of as repo packing on steroids that features protocol interception, token budget, retrieval, prioritization, sorting, trimming, cache-friendly prompts, and more.
- **RAG**: Contrary to RAG, which usually retrieves chunks from vector store, context stuffing incorporates wider selection of information (instructions, examples, prompt-independent knowledge). RAG can be thought of as a cheap extra attention layer prepended to the LLM. It's a workaround for tiny context windows in early LLMs. Context stuffing instead relies on accurate native attention mechanism built into LLMs to identify relevant information in a large native context window.
- **Agents**: Agents populate the context gradually, guided by LLM decisions. This is arguably more selective, but it's also slower and more expensive. Since context stuffing ideally prepares the whole prompt in one step, it mostly relies on the fast, cheap, and cacheable input tokens. Lower cost has the advantage of much larger prompts for given price. And shorter response time encourages conveniently interactive workflow.
- **Reasoning**: Reasoning (or thinking) is fundamentally different from context stuffing in that it can only unpack information that is already in the context. It can however complement context stuffing by analyzing the stuffed context in light of user prompt.
- **Uploads**: File uploads (or attachments, input documents) are the easiest way to supply knowledge to the LLM. [Aider](https://aider.chat/) in particular relies on users manually selecting source files instead of using the more common agentic retrieval. While this saves tokens and makes the context more focused, it is also very laborious, especially in projects with extensive utility code that is used everywhere. Llobot can identify this utility code automatically and populates the context with it. Manual document selection is still possible simply by mentioning the documents in user prompt.

You might be thinking that it's unreasonable to cram the entire codebase or knowledge base into the context window. That was the original reasoning behind RAG and that's also what motivates agentic retrieval. But context windows keep growing whether you measure them by declared size, actual long-context performance, or by how much context you can get at fixed cost. Prompt caching could definitely be better (long-lived and modular), which is where I expect considerable improvement, especially for local models. Llobot is designed for this future, but it can also deal with present-day limits by prioritizing and trimming content, offering retrieval on top of context stuffing, and assembling cache-friendly prompts.

## Setup

Llobot is highly configurable, but let's consider a very basic example that mostly relies on defaults. Llobot is a Python library, so we need a short Python script to configure it. The script assumes you have llobot cloned locally under `~/Sources/llobot`.

```python
import sys
from pathlib import Path

# Llobot is not in pip yet, so let's just add the repository to Python's module path.
sys.path.insert(0, str(Path.home() / 'Sources' / 'llobot'))

from llobot.models.catalogs import ModelCatalog
import llobot.models.ollama
import llobot.models.openai
import llobot.projects
import llobot.knowledge.sources
import llobot.experts.coders
import llobot.experts.python
import llobot.experts.java
import llobot.experts.wrappers
import llobot.experts.memory
import llobot.models.experts
import llobot.models.ollama.listeners

# Backend models that respond to the assembled prompt
backend_models = ModelCatalog(
    # This will use qwen2.5-coder:7b on localhost instance of Ollama.
    # Context size has to be always specified, because Ollama defaults are tiny.
    llobot.models.ollama.create(
        'qwen2.5-coder', 24 * 1024, top_k=1, aliases=['local']),
    # Context size in this case just limits spending.
    llobot.models.openai.proprietary(
        'gpt4.1-mini', 32 * 1024, 'YOUR_OPENAI_API_KEY', aliases=['cloud']),
)

# Projects that will be used as knowledge bases
projects = [
    llobot.projects.create('llobot',
        llobot.knowledge.sources.directory(Path.home() / 'Sources' / 'llobot')),
    llobot.projects.create('myproject',
        llobot.knowledge.sources.directory(Path.home() / 'Sources' / 'myproject')),
]

# Experts determine what goes in the context.
# This function configures bare expert to serve as a virtual model.
def define_expert(name, expert):
    # This wraps the expert in a virtual model.
    return llobot.models.experts.standard(
        # Standard expert functionality: reserved tokens, cache-friendly prompts
        expert | llobot.experts.wrappers.standard(),
        # This determines where the expert will store data
        # (archived chats and examples). We will use defaults.
        llobot.experts.memory.standard(name),
        # Default backend model.
        backend_models['local'],
        # Alternative backend models.
        backend_models,
        projects)

# Lets use some standard experts that come with llobot.
experts = ModelCatalog(
    define_expert('coder', llobot.experts.coders.standard()),
    define_expert('python', llobot.experts.python.standard()),
    define_expert('java', llobot.experts.java.standard()),
)

# Backend Ollama listens on 11434, so we will listen on 11435 to avoid conflicts.
llobot.models.ollama.listeners.create(experts, port=11435).listen()
```

Run this script and add `localhost:11435` as an additional Ollama endpoint to your UI frontend (like Open WebUI, which is [no longer open source](https://github.com/open-webui/open-webui/issues/13579), so feel free to look for alternatives). You should now see virtual models `coder`, `python`, and `java` listed in the UI.

## How to use

You should now be able to issue queries against the experts. Select `python` expert and submit this prompt:

> How do I connect to remote Ollama instance?
>
> ~llobot

The last line is a command that tells the expert to use `llobot` project as its knowledge base. If you wanted to work on `myproject`, you would write `~myproject` there. When you submit this prompt, you should get a response like this:

> Use `llobot.models.ollama.remote(host, port, path)` to get the endpoint URL, then pass it to `llobot.models.ollama.create()` as the `endpoint` argument. For example:
>
> ```python
> endpoint = llobot.models.ollama.remote('remote.host.com', 11434)
> model = llobot.models.ollama.create('qwen2.5-coder', 24 * 1024, endpoint=endpoint)
> ```
>
> `:20250526-221039`

NB: Response this informative relies on using a large model and on having prior related conversations with the expert. For comparison, response from 'qwen2.5-coder' without prior conversations is below. It's close, but it's not quite there.

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

The last line is a timestamp that the expert uses to stick to particular version of the knowledge base in case you continue the conversation.

The `~llobot` command in the prompt can be more complicated:

- `~myproject/info` to show help, available options, lots of information
- `~myproject@cloud` to run on backend model that we aliased as `cloud` in the above setup script
- `~myproject/echo` to respond with the whole assembled prompt (good to get an idea what goes in there)

If the context does not include the file you need, just mention it in the prompt, for example as `projects.py` or `ollama/listeners.py`, and llobot will include it in the context in preference to default knowledge.

Finally, if you are happy with the output, issue command `/ok` after the response you like. Llobot will save it as a correct example. Recent examples are included in the context. LLMs have propensity to imitate what is already in the context, so putting correct examples in the context increases probability that the next response will be correct too. If the response is wrong, you can still show llobot how to do it right. Impersonate the LLM (edit the response, a function that is in Open WebUI but not necessarily in other frontends), put there the correct response, and then issue `/ok` command. While this seems laborious, you usually have the correct response anyway in your code, so this is just about letting llobot know about it.

## Features

Llobot is not a framework. It's a library. You are in control. Llobot is merely a gallery of functionality, from which you can pick and choose. Defaults are provided for everything, but most of the high-level functions have numerous parameters you can customize. Everything is interface-based, so that you can add your own implementation if necessary. The list below is an overview of llobot's built-in features.

- **Protocols**: Clients and servers are implemented for Ollama and OpenAI protocols. Llobot can intercept these protocols in order to inject additional context.
- **Languages**: Llobot has some built-in intelligence for handling files in several popular programming languages and file formats: Markdown, Python, Java, Rust, shell, XML, JSON, TOML, and others.
- **Knowledge**: Llobot can scan a directory for knowledge using built-in or custom filters. Interface is provided for fetching knowledge from alternative sources.
- **Scorers**: Documents in knowledge base are prioritized by score to select the most important ones that fit in given token budget. PageRank is used to discover utility and base code that is frequently referenced from other files. Project *scopes* can prioritize some subset of the knowledge base. Every expert prioritizes files it is supposed to handle (regular, non-test Java files in Java expert, for example). Document length is incorporated in the score to deprioritize excessively long documents.
- **Examples**: Model outputs or user-provided sample outputs can be marked as correct examples. Recent examples are included in the prompt to support in-context learning.
- **Trimmers**: Some non-essential boilerplate, for example imports and package declarations in Java, can be trimmed to fit more useful content in the context. Llobot can optionally also trim comments, method bodies, and other detail in order to fit more of the high-level code structure in the context.
- **Formatters**: By default, llobot builds clean prompts consisting of several chat turns using readable Markdown. Clean prompts add a bit of overhead, but they are easier to audit by humans.
- **Crammers**: While high-level experts decide what goes in the prompt, it's crammers that actually implement algorithms that apply scorers, trimmers, and formatters to build sections of the prompt for given token budget.
- **Scrapers**: To support prioritization, llobot can scrape documents for links to other documents. In source code, that mainly means import statements. Retrieval also uses scrapers to find document links in user prompt.
- **Archives**: Examples as well as all chats and knowledge base revisions are archived locally to build datasets for later evaluations and fine-tuning.
- **Cache-friendly**: Prompts are assembled in reproducible order from whole documents to minimize cache invalidations. Llobot has cache estimators that predict what is most likely already cached. It constructs delta prompts that try to at least partially reuse already cached prompts.

## Best practices

Llobot works best with cloud models, which have plenty of burst compute to handle reprocessing of large prompts. Cloud models are also smart enough to be useful. Local models will have to wait until some local inference engine implements highly effective prompt cache. If you want to use llobot with local models anyway, prime the cache by issuing `/hi` command, e.g. `~myproject/hi`. If you submit empty prompt with only the command (`~myproject`), then `/hi` is implied. You can compose your prompt while the model is processing the cache priming request.

Make every task meaningful on its own. Do not reference prior conversations. This will give llobot freedom to choose examples and their ordering in the prompt.

If the prompt absolutely depends on the model seeing particular file, mention it in the prompt as `file.ext` or `path/prefix/file.ext`, whichever is sufficiently unique to match only one file. This ensures the document will be added to the assembled prompt regardless of how llobot prioritizes documents for inclusion.

Contemporary LLMs are all divergent. They stray from the correct path and introduce bugs and other flaws. If you don't correct them, this imperfect content will make it back into the prompt, at least when llobot is used to support editing. And LLMs, being dutiful imitators, will multiply the flaws in following output. If you were to let the LLM work autonomously for a long time in some sort of agentic loop, you would likely come back to a repository (or knowledge base) that is an unrecognizable mess and a LLM that has meantime went mad. This is what I mean when I say LLMs are divergent. If we had convergent LLMs, we could fire most people. Divergent LLMs are still useful, but you have to periodically stop them, review changes, and correct mistakes. Llobot encourages this collaborative workflow by eschewing agentic loops in favor of interactive prompt adjustments and visible output waiting for review.

It's not necessary to be excessively precise in your prompts. LLMs are good at filling in the details. Try minimalist prompt first. If the output isn't what you wanted, edit the prompt to clarify the task. Llobot is designed to be used interactively like this. If you have meantime modified your code using the imperfect output, take the timestamp from model's response and add it to the command in your prompt, for example `~myproject:20250526-222015`. Llobot will use the unmodified version of the knowledge base to answer the new prompt.

It is a good idea to standardize on knowledge base organization that prefixes every path with name of the source directory even if there's currently only one. So if you are loading knowledge from directory `myproject`, then path `subdir/file.txt` would be mapped to `myproject/subdir/file.txt` in the knowledge base. `Knowledge` class has some helpful methods for this purpose. This organization has several advantages. You can now disambiguate mentions of files in the root directory, so for example `myproject/README.md` instead of `README.md`, which would also match `myproject/subdir/README.md`. You can add dependencies, sibling projects, and documentation into the knowledge base without causing conflicts with the main project.

Finally, do not use LLMs compulsively for everything. Sometimes it's easier to do things by hand in the editor or to use refactoring tools offered by IDEs.

## Status

Experimental. Undocumented. Untested. Incomplete. Unstable APIs. Likely some bugs. But it works for me and I hope others might find it useful too.

