## File notes

File path in file listings may be followed by comma-separated notes in parentheses to attach metadata to the listing. For example:

`path/to/file.py` (new):

```python
# ... python code here ...
```

- Notes can be combined as needed, for example `(edited, partial)`.
- If no note is present, it is a listing of an unmodified project file.

Commonly used notes:

- new: Mark the file as "new" when it is a new file you intend to add.
- edited: When rewriting a file to include your changes, mark it with "edited" note.
- modified: When a file changes during the conversation, its new version will be included in the context with "modified" note.
- partial: To save context window space, some file listings may include only parts of the file that have changed. Such listings are marked with "partial" note.

