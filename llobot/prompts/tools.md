## File manipulation tools

- Use tools to perform file modifications
- Tool calls in your messages represent your actions

### Tool script

Example:

```toolscript
rm ~/file/to/remove.txt
mv ~/original/location.md ~/path/to/destination.md
```

- Tool script behaves like a shell script, but its content is limited to commands shown in the above example in that exact form without options
- Tool script is parsed using Python's shlex and it supports single-quoted, double-quoted, and backslash-escaped arguments, but not raw newlines or bash-style `$'...'`
- Tools in a tool script can be applied only to individual files, not whole directories

### New or modified file

Example:

<details>
<summary>File: ~/path/to/file.py</summary>

```python
# ... entire content of the file ...
```

</details>

- Use file listing to create a new file or modify an existing one
- The code block contains the entire content of the file
- IMPORTANT: Provide the entire new content of the file when adding or modifying files rather than just a diff or other partial representation
