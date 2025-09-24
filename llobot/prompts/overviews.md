## Directory overviews

- Directory overviews are special files that have a central role in the directory
- Specialized overview files include `mod.rs`, `package-info.java`, `__init__.py`, `CONTRIBUTING.md`, and many others
- The most common general-purpose overview file is `README.md`
- IMPORTANT: When adding or modifying files, also add or update related directory overviews
- Add missing and update deficient overview files related to the files you edit

### Naming and placement of overview files

- Prefer specialized overview files where possible and fall back to `README.md` otherwise
- If only some content is appropriate for a specialized overview file, write the full version of the overview in an accompanying `README.md`
- Do not create overview files in directories that have trivial, standard, or otherwise predictable structure

### Content of overview files

- Summarize the directory at the top of its overview file
- Describe common patterns, principles, and conventions shared by files under the directory
- Enumerate files and subdirectories and describe each with a few sentences
- Include descriptions for files and directories that are hidden, private, or that represent resources or attachments

### Descriptions of source code files

- If a source code file or a directory represents a single language-specific symbol like a class or a module, use this symbol as the name of the corresponding overview entry
- For every source code file described in the directory overview, enumerate public symbols defined in it
