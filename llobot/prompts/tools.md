## File manipulation tools

- Use tools to perform file modifications
- Tool calls in your messages represent your actions

### New or modified file

- To create a new file or modify an existing one, use a file listing
- The code block contains the entire content of the file
- IMPORTANT: Provide the entire new content of the file when adding or modifying files rather than just a diff or other partial representation

Example:

<details>
<summary>File: ~/path/to/file.py</summary>

```python
# ... entire content of the file ...
```

</details>

### Removed file

- To remove a file, use the `rm` command in a `tool` code block
- A directory is removed by removing all files within it
- Arguments can be single-quoted, double-quoted, or backslash-escaped
- Raw newlines are not allowed. Bash-style `$'...'` is not supported

Example:

```tool
rm ~/path/to/file.py
```

### Moved file

- To move a file, use the `mv` command in a `tool` code block
- If a file needs to be moved and also modified, use two separate operations: first move, then modification
- Arguments can be single-quoted, double-quoted, or backslash-escaped
- Raw newlines are not allowed. Bash-style `$'...'` is not supported

Example:

```tool
mv ~/original/location.py ~/path/to/file.py
```
