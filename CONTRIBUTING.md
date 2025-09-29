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

## Structure

The project root directory is organized as follows:

- [`llobot/`](llobot/): The main Python package containing all library source code.
- [`tests/`](tests/): Unit tests for the library. The directory structure within `tests/` mirrors that of the `llobot/` package.
- [`README.md`](README.md): A general overview of the project, its features, and a getting-started guide.
- [`CONTRIBUTING.md`](CONTRIBUTING.md): This file, containing guidelines for contributors.
- `LICENSE` & `COPYRIGHT`: Project licensing and legal information.
- [`requirements.txt`](requirements.txt): A list of Python package dependencies for the project.

## Architecture

Llobot is designed to be modular and configurable with reasonable defaults.

The core interaction is orchestrated by a [`Role`](llobot/roles/__init__.py). When a user sends a prompt, the `Role` processes it through a `StepChain`. This chain consists of [`Command`s](llobot/commands/__init__.py) that parse `@mentions` from the prompt and other [`Step`s](llobot/commands/__init__.py) that perform various actions, for example retrieving documents from knowledge base. These steps manipulate a shared [`Environment`](llobot/environments/__init__.py), which is a container for stateful components like the selected [`Project`](llobot/projects/__init__.py), the loaded [`Knowledge`](llobot/knowledge/__init__.py), and the [`ContextEnv`](llobot/environments/context.py) that accumulates chat messages.

The `Role` performs "context stuffing". It uses [`Crammer`s](llobot/crammers/__init__.py) to select the most relevant information (e.g., knowledge documents, few-shot examples from [`ExampleMemory`](llobot/memories/examples.py)) that fits within the [`Model`'s](llobot/models/__init__.py) context budget. This content is rendered into clean, human-readable Markdown by components from the [`formats`](llobot/formats/__init__.py) package.

Finally, the assembled context, represented as a [`ChatBranch`](llobot/chats/branches.py), is sent to the backend [`Model`](llobot/models/__init__.py) (e.g., Ollama, OpenAI) for generation. The response is streamed back to the user.

## Conventions

Llobot follows several architectural patterns and conventions that are important for contributors to understand:

- **Immutability and Builders**: Core data structures like [`Knowledge`](llobot/knowledge/__init__.py) and [`ChatBranch`](llobot/chats/branches.py) are immutable. Some of them have associated mutable `Builder` classes (e.g., [`ChatBuilder`](llobot/chats/builders.py)). Algorithm classes like [`Model`](llobot/models/__init__.py) and [`Role`](llobot/roles/__init__.py) are also immutable.
- **Value Types**: Most classes are immutable value types that inherit from [`ValueTypeMixin`](llobot/utils/values.py). This provides automatic implementations of `__eq__`, `__hash__`, and `__repr__` based on an object's attributes. Aside from benefiting testing and debugging, this importantly enables function caching (e.g., with `@lru_cache` or `@cache`) even when parameters are complex types.
- **Composition**: Many components can be combined using the `|` (`__or__`) operator. This pattern is used in [`KnowledgeSubset`](llobot/knowledge/subsets/__init__.py), [`KnowledgeIndex`](llobot/knowledge/indexes.py), [`Project`](llobot/projects/__init__.py), and many others classes to create composite objects from simpler parts.
- **Coercion Functions**: Functions like [`coerce_subset()`](llobot/knowledge/subsets/__init__.py), [`coerce_index()`](llobot/knowledge/indexes.py), and [`coerce_zoning()`](llobot/utils/zones/__init__.py) provide API flexibility by accepting various input types (e.g., a `str` pattern, a `Path`, or a [`Knowledge`](llobot/knowledge/__init__.py) object) and converting them into the required class (e.g., a `KnowledgeSubset`).
- **Standard Factories**: Many components have a `standard_*()` factory function (e.g., [`standard_ranker()`](llobot/knowledge/ranking/rankers.py), [`standard_scorer()`](llobot/knowledge/scores/scorers.py)) that returns a default, shared instance. These are decorated with `@cache`, so that expensive objects are created only once.
- **Internal Imports**: All internal imports within the [`llobot`](llobot/__init__.py) package are absolute (e.g., `from llobot.chats.messages import ChatMessage`). Submodule symbols are not re-exported from package `__init__.py` files. Code should always import symbols directly from the submodule where they are defined.
- **Docstrings**: All modules, classes, and functions have Google-style docstrings.

## License

Your submissions will be distributed under the project's [Apache License 2.0](LICENSE).
