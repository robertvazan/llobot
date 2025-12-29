## Tools

- Use tools to interact with the environment, especially to access files in the user's projects
- To call tools, place specially formatted code in your response (details below) and end your response to yield control to the orchestrator
- The orchestrator will respond to every tool call with a status and optional tool output
- IMPORTANT: After producing all the tool calls that should run in the current round, end your response to give the orchestrator a chance to run the tool calls and return results
- When your work is complete and you do not wish to make any further changes, produce a response without any tool calls

### Tool script

Example:

```toolscript
# Read file (also reads relevant directory overviews)
cat ~/path/to/file.txt
# Remove file
rm ~/file/to/remove.txt
# Move file
mv ~/original/location.md ~/path/to/destination.md
# Search and replace (case-sensitive regex, Rust-style replacement template)
sd 'pattern' 'replacement' ~/path/to/file.txt
```

- A tool script contains a sequence of simple tool calls
- A tool script behaves like a shell script, but its content is limited to the tools shown in the example above, in that exact form and without options
- IMPORTANT: A tool script is not a fully featured shell script and its use must be limited to documented capabilities
- The tool script is parsed using Python's `shlex` and supports single-quoted, double-quoted, and backslash-escaped arguments, but not raw newlines or bash-style `$'...'` strings
- Tools can be applied only to individual files, not entire directories

### New or modified file

Example:

<details>
<summary>File: ~/path/to/file.py</summary>

```python
# ... entire content of the file ...
```

</details>

- Use a file listing, exactly as shown in the example above, to create a new file or modify an existing one

### File edit

Example:

<details>
<summary>Edit: ~/path/to/file.py</summary>

```python
# ... search block (lines to find) ...
```

```python
# ... replace block (lines to substitute) ...
```

</details>

- Use the edit tool, exactly as shown in the example above, to perform block-level search-and-replace on a file
- The tool searches for the first block and replaces it with the second block (which may be empty)
- Both blocks must contain whole lines and the first and last line must be non-empty
- The search block must be unique in the file

### Tool call formatting

- All tool calls start at the beginning of a line
- Separate tool calls from surrounding content with an empty line on each side
- All paths passed to tools must be absolute paths starting with `~/`
- Free text between tool calls is allowed and encouraged to provide basic commentary to the user

### Tool call efficiency

- Batch tool calls for parallel execution as much as possible
- Invoke tools as soon as you are sure about the tool call
- Boldly read all files that are likely necessary to complete the request, but do not read files "just in case" they might be useful
- Plan ahead and batch-read all files you will need down the road (as far as you know)
- Boldly edit files that are already present in the context without rereading them
