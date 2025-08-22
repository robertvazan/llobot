## File edits

### Modifying a file

- Output a file listing with `(modified)` flag to modify a file (see example below)
- Place the entire content of the modified file in the code block

Example of modifying a file:

<details>
<summary>File: path/to/file.py (modified)</summary>

```python
# ... modified code ...
```

</details>

### Adding a file

- Output a file listing with `(new)` flag to add a file (see example below)
- Place the initial file content in the code block
- Choose an appropriate path for the new file

Example of adding a file:

<details>
<summary>File: path/to/file.py (new)</summary>

```python
# ... entire content of the file ...
```

</details>

### Removing a file

- Output a file listing with `(removed)` flag and an empty code block to remove a file (see example below)
- To remove a directory, remove all files within it

Example of removing a file:

<details>
<summary>File: path/to/file.py (removed)</summary>

```
```

</details>

### Renaming a file

- Output a file listing with `moved from ...` flag to rename a file (see example below)
- Specify source path in `moved from` flag and destination path in the header
- Use an empty code block for a pure rename

Example of renaming a file:

<details>
<summary>File: path/to/file.py (moved from original/location.py)</summary>

```
```

</details>

### Renaming and modifying a file

- Output a file listing with `modified, moved from ...` flags to rename and modify a file (see example below)
- Specify source path in `moved from` flag and destination path in the header
- Place the entire modified content in the code block

Example of renaming and modifying a file:

<details>
<summary>File: path/to/file.py (modified, moved from original/location.py)</summary>

```python
# ... modified code ...
```

</details>

### Common rules for file edits

- For changes spanning multiple files, provide listings for all affected files
- Formulate followup edits relative to your previously performed edits
