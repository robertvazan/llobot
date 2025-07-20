## File flags

File path in file listings may be followed by comma-separated flags in parentheses to attach metadata to the listing. For example:

`path/to/file.py` (new):

```python
# ... python code here ...
```

- Flags can be combined as needed, for example `(modified, moved from 'original/location.py')`.
- If no flag is present, then the enclosed code is the original, unmodified content of the file.

Commonly used flags:

- new: The file is new.
- modified: The file has been modified.
- removed: The file has been removed.
- informative: You do not wish to make any changes. Use this flag when you just want to quote some code or to show possible changes in order to support an explanation or an argument.
- moved from `original/location.py`: The file has been moved or renamed. This flag indicates its original location. It can be combined with `modified` if the file content has also changed.

It is sometimes useful to create a flag-only file listing that does not have any code block. For example:

`path/to/file.py` (removed)

- Flag-only listings are commonly used with the `removed` flag.
- They are also useful for `moved from` flags if no changes have been made in file content.
