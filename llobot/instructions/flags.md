## File flags

File listing may include flags. For example, here's how you attach flag `new`:

`path/to/file.py` (new):

```python
# ... python code here ...
```

- To add several flags, separate them with commas, for example `(modified, diff)`
- Always enclose flags in parentheses and leave a space between flags and file path
- Always use at least one flag in your responses
- File listings without flags in user's messages represent the original, unmodified content of the file

In addition to file listings with flags, you can also create flag-only file listings that do not have any code block, for example:

`path/to/file.py` (removed)

- Flag-only listings must have at least one flag
- Flag-only listings are commonly used with `removed` and `moved from` flags
- Never add colon at the end of the header in a flag-only file listing
- If there is any content before or after the flag-only file listing, leave an empty line between the file listing and surrounding content

Commonly used flags:

- new: The file is new
- modified: The file has been modified
- removed: The file has been removed
- informative: Use this flag in your responses when you do not want to make any changes to the file, for example when you just want to quote some code or show possible changes
- moved from `original/location.py`: The file has been moved or renamed
  - When combined with `modified` flag, it indicates that the file has been moved and subsequently modified
  - Always use the full original path in `move from` flag
- diff: Code block of the file listing contains only file changes, not full content of the file
