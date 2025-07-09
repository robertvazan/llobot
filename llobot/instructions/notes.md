## File notes

File path in file listings may be followed by comma-separated notes in parentheses to attach metadata to the listing. For example:

`path/to/file.py` (new):

```python
# ... python code here ...
```

- Notes can be combined as needed, for example `(edit, moved from 'original/location.py')`.
- If no note is present, then the enclosed code is the original, unmodified content of the file.

Notes commonly used by the user that describe actual changes in the file system:

- modified: File has changed and this is its latest content.
- removed: File has been removed.

Notes you may use to indicate the action you wish to take:

- new: You wish to create the file.
- edit: You wish to replace the file with the enclosed content.
- delete: You wish to remove the file.
- quote: You do not wish to make any changes. You are just quoting a fragment of the file to support an explanation or an argument.
- moved from `original/location.py`: You wish to move or rename the file from the path in the note to the path in the listing header. You can combine "move" note with "edit" note to also make changes in the file.

It is sometimes useful to create note-only file listing that does not have any code block. For example:

`path/to/file.py` (removed)

- Notice there is no colon and no code block.
- Note-only listings are commonly used with "removed" and "delete" notes.
- They are also useful for "move" notes if no changes have been made in file content.

