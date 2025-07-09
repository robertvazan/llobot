## File edits

To add a file:

- Use whole file listing format.
- Mark it with "(new)" note.
- Choose appropriate name and directory for it.

`path/to/file.py` (new):

```python
# ... entire content of the file
```

To remove a file:

- Use note-only listing format.
- Mark it with "(delete)" note.

`path/to/file.py` (delete)

To modify a file:

- Use whole file listing format.
- Mark it with "(edit)" note.

`path/to/file.py` (edit):

```python
# ... changed code
```

To rename a file:

- Use note-only listing format.
- Mark it with "(moved from `original/location.py`)" note.
- Put source path in the note and destination path in header path.

`path/to/file.py` (moved from `original/location.py`)

To rename a file and also make changes to it:

- Use whole file listing format.
- Mark it with "move" and "edit" notes.
- Put source path in the note and destination path in header path.
- Place new content in the code block.

`MyClass.java` (edit, moved from `OriginalClass.java`):

```java
class MyClass {
    // ... the rest of the code
}
```

Additionally:

- You can include listings of several files in your response if the change is scattered across several files.

