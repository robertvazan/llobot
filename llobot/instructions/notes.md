## File notes

File path in file listings may be followed by comma-separated notes in parentheses to attach metadata to the listing. For example:

`path/to/file.py` (new):

```python
# ... python code here ...
```

- Notes can be combined as needed, for example `(edit, delta)`.
- If no note is present, it is a listing of an unmodified project file.

Commonly used notes:

- new: Mark the file as "new" when it is a new file you intend to add.
- edit: When rewriting a file to include your changes, mark it with "edit" note.
- modified: When a file changes during the conversation, its new version will be included in the context with "modified" note.
- delta: To save context window space, some file listings may include only parts of the file that have changed. Such listings are marked with "delta" note.
- quote: When quoting a fragment of a file without modification, for example as part of an explanation or argument, mark it with "quote" note to differentiate it from the original file listing.
- moved from `original/location.py`: When a file is moved or renamed, this note indicates its original location. This note often supplements "edit" and "delta" notes.

