# Llobot

Llobot is a LLM context stuffing tool and Python library. It sits between LLM frontend (chat UI) and inference engine (which is serving the model), intercepts chat completion requests sent via supported LLM chat protocol (Ollama or OpenAI), and manipulates them in some way, usually by prepending large synthetic context. Synthetic context commonly includes system instructions, documents from knowledge base, examples, and optionally prompt-dependent retrievals. While the whole setup is highly configurable, llobot is currently best suited for stuffing the context with source code in order to create expert chatbots that are knowledgeable about particular codebase. In this sens

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
- **RAG**: Contrary to RAG, which usually retrieves chunks from vector store, context stuffing incorporates wider selection of information (instructions, examples, prompt-independent knowledge). Context stuffing favors predictable retrieval of whole documents by their name, because retrievals in context stuffing mostly just compensate for limited context size.
- **Agents**: Agents populate the context gradually, guided by LLM decisions. This is arguably more powerful, but it's also much slower and more expensive. Since context stuffing ideally prepares the whole prompt in one step, it mostly relies on the fast and cheap input tokens. It therefore produces response in seconds and encourages a very convenient interactive workflow.
- **Reasoning**: Reasoning (or thinking) is fundamentally different from context stuffing in that it can only unpack information that is already in the context. It can however complement context stuffing by analyzing the stuffed context in light of user prompt.
- **Uploads**: File uploads (or attachments, input documents) are the easiest way to supply knowledge to the LLM. [Aider](https://aider.chat/) in particular relies on users manually selecting source files instead of using the more common agentic retrieval. While this saves tokens and makes the context more focused, it is also very laborious, especially in projects with extensive utility code that is used everywhere. Llobot can identify this utility code automatically and populates the context with it. Manual document selection is still possible simply by mentioning the documents in user prompt.

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

# Backend models that respond to the assembled prompt
backend_models = ModelCatalog(
    # This will use qwen2.5-coder:7b on localhost instance of Ollama.
    # Second parameter is context size. This has to be always specified, because Ollama defaults are tiny.
    llobot.models.ollama.create('qwen2.5-coder', 24 * 1024, top_k=1, aliases=['local']),
    # Context size in this case limits spending as llobot would otherwise use the whole supported context window.
    llobot.models.openai.proprietary('gpt4.1-mini', 32 * 1024, 'YOUR_OPENAI_API_KEY', aliases=['cloud']),
)

# Projects that will be used as knowledge bases
projects = [
    llobot.projects.create('llobot', llobot.knowledge.sources.directory(Path.home() / 'Sources' / 'llobot')),
    llobot.projects.create('myproject', llobot.knowledge.sources.directory(Path.home() / 'Sources' / 'myproject')),
]

# Experts determine what goes in the context. This function configures bare expert to serve as a virtual model.
def define_expert(name, expert):
    # This wraps the expert in a virtual model.
    return llobot.models.experts.standard(
        # This adds standard expert functionality like reserved tokens and cache-friendly delta prompts.
        expert | llobot.experts.wrappers.standard(),
        # This determines where the expert will store data (archived chats and examples). We will use defaults.
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

Run this script and add `localhost:11435` as an additional Ollama endpoint to your UI frontend like Open WebUI (which is [no longer open source](https://github.com/open-webui/open-webui/issues/13579), so feel free to look for alternatives). You should now see virtual models `coder`, `python`, and `java` listed in the UI.

## How to use

You should now be able to issue queries against the experts. Select `python` expert and submit this prompt:

> How do I connect to remote Ollama instance?
>
> ~llobot

The last line is a command that tells the expert to use `llobot` project as its knowledge base. If you wanted to work on `myproject`, you would write there `~myproject`. When you submit this prompt, you should get a response like this:

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

Finally, if you are happy with the output, issue command `/ok` after the response you like. Llobot will save it as a correct example. Recent examples are included in the context. LLMs have propensity to imitate what is already in the context, so putting correct examples in the context increases probability that the next response will be correct too. If the response is wrong, you can still show llobot how to do it right. Impersonate the LLM (edit the response, a function that is in Open WebUI but not necessarily in other frontends), put there the correct response, and then issue `/ok` command. While this seems laborious, you usually have the correct response anyway in your code, so this is just about letting lobot know about it.

## Status

Experimental. Undocumented. Untested. Incomplete. Unstable APIs. Likely some bugs. But it works for me and I hope others might find it useful too.

