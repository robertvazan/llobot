## File deltas

- While plain file listing describes original state of the file, file delta describes changes in the file
- File deltas in user messages describe changes that happened since the file was previously listed
- File deltas in your messages represent your actions

### New, modified, or original file

- A file listing with summary `File: path/to/file.py` represents a new, modified, or original file
- The code block contains the entire content of the file

Example:

<details>
<summary>File: path/to/file.py</summary>

```python
# ... entire content of the file ...
```

</details>

### Removed file

- Format: `` Removed: `path/to/file.py` ``
- Must be on its own line, separated from surrounding content by empty lines
- A directory is removed by removing all files within it

Example:

Removed: `path/to/file.py`

### Moved file

- Format: `` Moved: `original/path.py` => `new/path.py` ``
- Must be on its own line, separated from surrounding content by empty lines
- If a file needs to be moved and also modified, use two separate operations: first move, then modification

Example:

Moved: `original/location.py` => `path/to/file.py`
