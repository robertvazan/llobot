## Directory overviews

- Directory overviews are special files that play a central role in a directory.
- Specialized overview files include `mod.rs`, `package-info.java`, `__init__.py`, and many others.
- The most common general-purpose overview file is `README.md`, found in both the project root and subdirectories. However, technical information at the root is often placed in `CONTRIBUTING.md` instead.
- IMPORTANT: When adding or modifying files, also add or update the related directory overviews.
- Add missing overview files and repair deficient ones related to the files you edit.
- Prefer specialized overview files where possible. Otherwise, fall back to `README.md`.
- Do not create overview files in directories that have a trivial, standard, or otherwise predictable structure (i.e., if there is nothing interesting to write).

### Content of overview files

- Summarize the directory at the top of its overview file.
- Enumerate and briefly describe every file and subdirectory, including hidden, private, resource, and attachment entries.
- If a source code file or a directory represents a single language-specific symbol, such as a class or a module, use this symbol as the name of the corresponding overview entry.
- If a source code file defines a single primary symbol, mention it in its description.
- Describe shared patterns, principles, and conventions unique to the files within the directory.
