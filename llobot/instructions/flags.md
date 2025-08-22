## File flags

- Add flags to file listings to indicate changes (see example below)
- Separate multiple flags with commas, like `(modified, diff)`
- Enclose flags in parentheses with a leading space
- Use at least one flag in all file listings in your responses
- Assume file listings from the user without flags represent original, unmodified content

Example of a file listing with a flag:

<details>
<summary>File: path/to/file.py (new)</summary>

```python
# ... python code here ...
```

</details>

### Common flags

- Use `new` flag for a new file
- Use `modified` flag for a modified file
- Use `removed` flag for a removed file
- Use `moved from original/location.py` flag for a moved or renamed file
- Use `(modified, moved from ...)` flags when a file is moved and modified
- Always use the full original path in the `moved from` flag
- The `moved from` flag implies removal of the source path, so do not add a separate `(removed)` listing
- Recognize that `diff` flag means the code block contains only file changes, not full content
