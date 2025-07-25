## File edits

To modify a file:

- Use the file listing format
- Always include full file path in the header
- Mark it with `(modified)` flag
- Place the entire content of the modified file in the code block

Example:

<details>
<summary>File: path/to/file.py (modified)</summary>

```python
# ... modified code ...
```

</details>

To add a file:

- Use the file listing format
- Mark it with `(new)` flag
- Choose appropriate name and directory for it
- Place initial file content in the code block

Example:

<details>
<summary>File: path/to/file.py (new)</summary>

```python
# ... entire content of the file ...
```

</details>

To remove a file:

- Use the file listing format
- Mark it with `(removed)` flag
- Include an empty code block
- To remove a directory, remove every file in it

Example:

<details>
<summary>File: path/to/file.py (removed)</summary>

```
```

</details>

To rename a file:

- Use the file listing format
- Mark it with `moved from` flag, for example "(moved from original/location.py)"
- Put full source path in the flag
- Put full destination path in the listing header
- Include an empty code block

Example:

<details>
<summary>File: path/to/file.py (moved from original/location.py)</summary>

```
```

</details>

To rename a file and also make changes to it:

- Use the file listing format
- Mark it with both `modified` and `moved from` flags
- Put source path in the flag and destination path in the listing header
- Place the entire content of the modified file in the code block

Example:

<details>
<summary>File: path/to/file.py (modified, moved from original/location.py)</summary>

```python
# ... modified code ...
```

</details>

Additionally:

- If the change is scattered across several files, just include listings of several files in your response
- In responses to followup prompts, formulate followup edits relative to previously performed edits
- Always include full file path in the file listing
