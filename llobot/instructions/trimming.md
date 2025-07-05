## Trimming

To save on tokens and to fit more information in the context window, some parts of source code files might be omitted even in whole file listings:

- import/use/include statements
- namespace/package declarations
- shebang lines from scripts
- copyright/license comments
- other declarative information commonly found at the top of source code files

When you encounter trimmed files:

- Don't worry. It's not a bug.
- Assume the trimmed content is in the actual project file even though you cannot see it.
- When adding or modifying files using whole file listing format, match the trimming level of similar files in the project.
- Find symbol definitions by their (likely globally unique) name rather than by following import statements.
- If the symbol is ambiguous without seeing import statements, make an educated guess about which definition is it referring to.
- Assume that namespace/package declarations can be derived from file path.

