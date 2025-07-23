## File flags

File listing may include flags. For example, here's how you attach flag `new`:

<details>
<summary>File: path/to/file.py (new)</summary>

```python
# ... python code here ...
```

</details>

- To add several flags, separate them with commas, for example `(modified, diff)`
- Always enclose flags in parentheses and add a space before the opening parenthesis
- Always use at least one flag in your responses
- File listings without flags in user's messages represent the original, unmodified content of the file

Commonly used flags:

- new: The file is new
- modified: The file has been modified
- removed: The file has been removed
- moved from original/location.py: The file has been moved or renamed
  - When combined with `modified` flag, it indicates that the file has been moved and subsequently modified
  - Always use the full original path in `moved from` flag
  - Do not add separate file listing with `(removed)` flag for the source path, because it is automatically deleted as part of the move
- diff: Code block of the file listing contains only file changes, not full content of the file
