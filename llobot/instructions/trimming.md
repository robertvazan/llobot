## Trimming

To save on LLM API costs and to fit more information in the context window, some parts of files might be omitted depending:

- import/use/include statements
- namespace/package declarations
- shebang lines from scripts
- copyright/license comments
- other declarative information commonly found at the top of source code files

There is a global trimming configuration that determines what is omitted for different file types. You don't have access to the configuration, but it's easy to infer from files in the context.

When you encounter trimmed files:

- Don't worry. It's not a bug.
- Assume that the trimmed content is in the actual project file even though you cannot see it.
- Find symbol definitions by their (likely globally unique) name rather than by following import statements.
- If the symbol is ambiguous without seeing import statements, make an educated guess about which definition is it referring to.
- Assume that namespace/package declarations can be derived from file path.

When editing or adding files:

- Find similar file in the context and trim your output the same way.
- If there is no similar file in the context, default to no trimming.

