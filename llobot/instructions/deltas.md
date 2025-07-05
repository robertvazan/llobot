## File deltas

To conserve context window space, you may use delta file listing that shows only the relevant parts of the file. For example:

`path/to/file.py` (edit, delta):

```python
def new_function():
    return "new code here"

class ExistingClass:
    # ...

    # add after existing_method()
    def new_method(self):
        return "modified or new method"

    # removed old_method
```

How to create file deltas:

- Mark deltas with "(delta)" note after the file path to differentiate them from whole file listings.
- Most deltas will actually have "(edit, delta)" notes after the file path, because deltas are mainly useful when modifying files.
- Delta content does not have to be machine-readable like a diff. Deltas are intended for an intelligent reader, either the user or a language model. There is no strict format. Just make it clear what changes have been made to the file.
- Skip unmodified sections of the file. Show only added, modified, and replaced code.
- If you need to delete or move part of the file, add a comment that states what has been deleted or moved.
- Use `# ...` or similar language-specific comments to indicate that a class or other code element is incomplete. There's no need to do this on file level, because the "delta" note after the file path implies the file is incomplete.
- Always include enclosing element (namespace, class, etc.) when modifying nested code (methods, members, etc.), even if the enclosing element itself is unchanged. This provides necessary context for understanding where the changes belong.
- When adding new code, use comments to indicate its placement rather than showing surrounding unchanged code. For example: `# add after existing_method()`.
- When renaming methods, functions, classes, or other code elements, include the renamed element under its new name in the delta listing and add a comment that mentions the old name.
- Preserve indentation and structure to make the location clear and to allow for easy copy-n-pasting.

When to use deltas:

- Use deltas when the change is localized and showing the entire file would waste space.
- Use whole file listings for new files, heavily modified and rewritten files, and for scattered changes that are hard to localize.
- If unsure, default to deltas, which should be used for the vast majority of edits.

