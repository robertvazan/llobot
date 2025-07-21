## Documentation

When adding or modifying code, also add related documentation:

- Add documentation for all new code you write
- If you modify or extend some code, update and extend corresponding documentation too
- Do not document unrelated code that you aren't modifying now
- Document all internal APIs in addition to public APIs
- Write documentation in appropriate machine-readable format, for example javadoc in Java and docstrings in Python
- Fall back to informal comments where necessary, for example to document design choices inside function body
- If the modified code already has informal comments where formal documentation should be, convert them to the appropriate machine-readable documentation format
- Expand existing incomplete documentation in modified code
- Write only what you know, because it's better to have incomplete documentation than incorrect documentation
- Describe what the documented code does and what its parameters mean
- Do not balloon the documentation with excessive details that are not necessary to use the code correctly
- Do not add examples to the documentation
- When you fix a bug, add a protective comment explaining why the code must be the way it is, so that the fix is not reverted during later edits
