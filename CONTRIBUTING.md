# How to Contribute to Llobot

Thank you for taking interest in Llobot. This document provides guidance for contributors.

## Repositories

Sources are mirrored on several sites. You can submit issues and pull requests on any of them.

- [llobot @ GitHub](https://github.com/robertvazan/llobot)
- [llobot @ Bitbucket](https://bitbucket.org/robertvazan/llobot)

## Issues

Both bug reports and feature requests are welcome. There is no free support, but it's perfectly reasonable to open issues asking for more documentation or better usability.

## Pull Requests

Pull requests are generally welcome. If you would like to make large or controversial changes, please open an issue first to discuss your idea.

## Development

The easiest way to get started is to build and run the development container. See [`Containerfile`](Containerfile). It creates the venv automatically.

Quality gates that must pass:

- Run `pytest` without parameters to ensure all tests pass.
- Run `pyright` on modified files to check that there are no new type errors (old ones are acceptable).

## Terminology

The following terms are used throughout the code:

- Thread: An immutable sequence of messages represented by `ChatThread`.
- Prompt: The content submitted by the user to a role. This is usually the full thread visible in the client. We sometimes distinguish:
  - Initial prompt: The first message in the thread.
  - Current/last prompt: The last message in the thread.
  - Full prompt: The entire submitted thread.
- Context: The final message sequence assembled by the role and sent to the backend model. It includes the system prompt, knowledge, examples, and user's prompt.
- Session: Persisted state for a conversation. Besides context, session can persist wider environment associated with the conversation. Session ID is a hash of the initial prompt.
- History: An on-disk archive of past sessions managed by `SessionHistory`.
- Example memory: Approved and archived prompt-response message pairs used for few-shot prompting.

The term “chat” is ambiguous and typically refers to either the thread or the full prompt.

## Structure

The project root directory is organized as follows:

- [`llobot/`](llobot/): The main Python package containing all library source code.
- [`scripts/`](scripts/): Helper scripts for development and maintenance.
- [`tests/`](tests/): Unit tests for the library. The directory structure within `tests/` mirrors that of the `llobot/` package.
- [`README.md`](README.md): A general overview of the project, its features, and a getting-started guide.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): This file, containing guidelines for contributors.
- [`Containerfile`](Containerfile): Definition of the development container environment.
- `LICENSE` & `COPYRIGHT`: Project licensing and legal information.
- [`pyproject.toml`](pyproject.toml): Project metadata and dependencies.

## Architecture

Llobot is designed to be modular and configurable with reasonable defaults.

The core interaction is orchestrated by a [`Role`](llobot/roles/__init__.py). When a user sends a prompt (a thread of messages), the `Role` processes it in several stages:

1. **Command Processing**: The role calls functions from the [`commands`](llobot/commands/__init__.py) package to parse `@mentions`. These functions manipulate a shared [`Environment`](llobot/environments/__init__.py), selecting [`Project`s](llobot/projects/__init__.py) and backend [`Model`](llobot/models/__init__.py), retrieving files, etc. The environment is persisted in [`SessionHistory`](llobot/environments/history.py).

2. **Context Stuffing**: The role assembles the context using [`ContextEnv`](llobot/environments/context.py). It uses [`Crammer`s](llobot/crammers/__init__.py) to select relevant information (e.g.,  [`Knowledge`](llobot/knowledge/__init__.py), few-shot examples from [`ExampleMemory`](llobot/memories/examples.py)) that fits within the text length budget. This content is rendered into Markdown by components from the [`formats`](llobot/formats/__init__.py) package.

3. **Generation Loop**: The assembled context, represented as a [`ChatThread`](llobot/chats/thread.py), is sent to the backend [`Model`](llobot/models/__init__.py). The model returns a [`ChatStream`](llobot/chats/stream.py), which is an iterable of text chunks and intent markers.

4. **Tool Execution**: If the model response contains tool calls, the role executes them using the [`tools`](llobot/tools/__init__.py) package. The results are added to the context, and the loop continues, sending the updated context back to the model for further generation, until the model stops calling tools or the autonomy limit is reached.

Finally, the response stream is relayed to the user.

## Conventions

Llobot follows several architectural patterns and conventions:

- **Immutability and Builders**: Core data structures like [`Knowledge`](llobot/knowledge/__init__.py) and [`ChatThread`](llobot/chats/thread.py) are immutable. Some of them have associated mutable `Builder` classes (e.g., [`ChatBuilder`](llobot/chats/builder.py)). Algorithm classes like [`Model`](llobot/models/__init__.py) and [`Role`](llobot/roles/__init__.py) are also immutable.
- **Value Types**: Most classes are immutable value types that inherit from [`ValueTypeMixin`](llobot/utils/values.py). This provides automatic implementations of `__eq__`, `__hash__`, and `__repr__` based on an object's attributes. Aside from benefiting testing and debugging, this importantly enables function caching (e.g., with `@lru_cache` or `@cache`) even when parameters are complex types.
- **Composition**: Many components can be combined using the `|` (`__or__`) operator. This pattern is used in [`KnowledgeSubset`](llobot/knowledge/subsets/__init__.py), [`KnowledgeIndex`](llobot/knowledge/indexes.py), [`Project`](llobot/projects/__init__.py), and many other classes to create composite objects from simpler parts.
- **Coercion Functions**: Functions like [`coerce_subset()`](llobot/knowledge/subsets/__init__.py), [`coerce_index()`](llobot/knowledge/indexes.py), and [`coerce_zoning()`](llobot/utils/zones/__init__.py) provide API flexibility by accepting various input types (e.g., a `str` pattern, a `PurePosixPath`, or a [`Knowledge`](llobot/knowledge/__init__.py) object) and converting them into the required class (e.g., a `KnowledgeSubset`).
- **Standard Factories**: Many components have a `standard_*()` factory function (e.g., [`standard_ranker()`](llobot/knowledge/ranking/rankers.py), [`standard_scorer()`](llobot/knowledge/scores/scorers.py)) that returns a default, shared instance. These are decorated with `@cache`, so that expensive objects are created only once.
- **Encapsulation**: Private variables (starting with `_`) are never accessed outside the class that defines them, not even in tests.
- **Internal Imports**: All internal imports within the [`llobot`](llobot/__init__.py) package are absolute (e.g., `from llobot.chats.messages import ChatMessage`). Submodule symbols are not re-exported from package `__init__.py` files. Code should always import symbols directly from the submodule where they are defined.
- **Docstrings**: All modules, classes, and functions have Google-style docstrings.
- **Backward Compatibility**: Backward compatibility is NOT maintained before the 1.0 release. This applies to API, file formats, and persisted data. Contributors are encouraged to rename and refactor aggressively to improve the codebase.

## License

Your submissions will be distributed under the project's [Apache License 2.0](LICENSE).
