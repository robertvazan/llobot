## File edits

To add a file:

- Use whole file listing format.
- Mark it with "(new)" flag.
- Choose appropriate name and directory for it.

`path/to/file.py` (new):

```python
# ... entire content of the file
```

To remove a file:

- Use flag-only listing format.
- Mark it with "(removed)" flag.
- You cannot remove directories. Remove individual files in the instead.

`path/to/file.py` (removed)

To modify a file:

- Use whole file listing format.
- Mark it with "(modified)" flag.

`path/to/file.py` (modified):

```python
# ... changed code
```

To rename a file:

- Use flag-only listing format.
- Mark it with "(moved from `original/location.py`)" flag.
- Put source path in the flag and destination path in header path.
- The original location is presumed to be deleted. You don't have to add separate deletion.

`path/to/file.py` (moved from `original/location.py`)

To rename a file and also make changes to it:

- Use whole file listing format.
- Mark it with "move" and "modified" flags.
- Put source path in the flag and destination path in header path.
- Place new content in the code block.

`MyClass.java` (modified, moved from `OriginalClass.java`):

```java
class MyClass {
    // ... the rest of the code
}
```

Additionally:

- You can include listings of several files in your response if the change is scattered across several files.
- In responses to followup prompts, assume your prior edits became part of the knowledge base and formulate followup edits relative to them. Do not repeat prior edits.
