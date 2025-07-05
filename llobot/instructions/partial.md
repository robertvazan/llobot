## Partial listings

To conserve context window space, you may use partial source code listings that show only the relevant parts of a file. For example:

`path/to/file.py` (edit, partial):

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

How to create partial source code listings:

- Mark partial listings with "(partial)" note after the file path to differentiate them from whole file listings.
- Most partial listings will actually have "(edit, partial)" note after the file path, because partial listings are mainly useful when modifying files.
- Content of partial listings does not have to be machine-readable like a diff. Partial listings are intended for an intelligent reader, either the user or a language model. There is no strict format. Just make it clear what changes have been made to the file.
- Skip unmodified sections of the file. Show only added, modified, and replaced code.
- If you need to delete or move part of the file, add a comment that states what has been deleted or moved.
- Use `# ...` or similar language-specific comments to indicate that a class or other code element is incomplete. There's no need to do this on file level, because the "partial" note after the file path implies the file is incomplete.
- Always include enclosing element (namespace, class, etc.) when modifying nested code (methods, members, etc.), even if the enclosing element itself is unchanged. This provides necessary context for understanding where the changes belong.
- When adding new code, use comments to indicate its placement rather than showing surrounding unchanged code. For example: `# add after existing_method()`.
- When renaming methods, functions, classes, or other code elements, include the renamed element under its new name in the partial code listing and add a comment that mentions the old name.
- Preserve indentation and structure to make the location clear and to allow for easy copy-n-pasting.

When to use partial listings:

- Use partial listings when the change is localized and showing the entire file would waste space.
- Use whole file listings for new files, heavily modified and rewritten files, and for scattered changes that are hard to localize.
- If unsure, default to partial listings, which should be used for the vast majority of edits.

