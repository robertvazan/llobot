## File deltas

- While plain file listing describes original state of the file, file delta describes changes in the file
- File deltas in user messages describe changes that happened since the file was previously listed
- File deltas in your messages represent your actions

### Modified file

- A file listing with a `(modified)` flag represents a modified file
- The code block contains the entire content of the modified file

Example:

<details>
<summary>File: path/to/file.py (modified)</summary>

```python
# ... modified code ...
```

</details>

### New file

- A file listing with a `(new)` flag represents a new file
- The code block contains the initial content of the new file

Example:

<details>
<summary>File: path/to/file.py (new)</summary>

```python
# ... entire content of the file ...
```

</details>

### Removed file

- A file listing with a `(removed)` flag and an empty code block represents a removed file
- A directory is removed by removing all files within it

Example:

<details>
<summary>File: path/to/file.py (removed)</summary>

```
```

</details>

### Renamed or moved file

- A file listing with a `moved from ...` flag represents a renamed file
- The source path is specified in the `moved from` flag and the destination path is in the listing header
- The `moved from` flag always contains the full original path
- The `moved from` flag implies removal of the source path, so a separate `(removed)` listing is not needed
- A pure rename has an empty code block

Example:

<details>
<summary>File: path/to/file.py (moved from original/location.py)</summary>

```
```

</details>

### Renamed and modified file

- A file listing with `modified, moved from ...` flags represents a file that was renamed and modified
- The source path is specified in the `moved from` flag and the destination path is in the header
- The code block contains the entire modified content of the file

Example:

<details>
<summary>File: path/to/file.py (modified, moved from original/location.py)</summary>

```python
# ... modified code ...
```

</details>
