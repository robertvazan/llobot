## Documentation

When adding or modifying code, also add related documentation:

- Prefer machine-readable documentation in the appropriate language-specific format, for example javadoc in Java and docstrings in Python, over informal comments where possible. Fall back to informal comments where necessary, for example to document design choices inside function body.
- Document all internal code, not just public APIs.
- Only add documentation related to added and modified code. Don't add documentation to code that you are not editing at the moment.
- If documenting modified code requires documenting surrounding code, for example when adding a parameter to a so far undocumented function, add the surrounding documentation to the necessary extent.
- If you modify or extend code that is already documented, update and extend the documentation to match code changes.
- Add documentation where you are well positioned to understand the code.
  - If you create utility code to help solve a problem, you know what it does, so document it.
  - If you are modifying code based on instructions in user's prompt, you can trust the prompt and include information sourced from it in the documentation.
  - Earlier messages in the context window might include information about what the code does and why. Use it to improve your documentation effort.
- If you are not sure about something, just omit that part of the documentation. It's better to leave something undocumented than to add incorrect information. This also applies to parts of documentation blocks, for example function parameters you don't understand can be omitted from the documentation.
- Good documentation primarily describes what the code does, but you should also include explanatory information if it is non-trivial and you can source it reliably from user's prompt or other context.
- When you fix a non-obvious bug, add a protective comment explaining the non-obvious rationale for the code, so that the fix is not reverted during later edits.
  - Add such protective comments proactively when you notice that you have almost done it wrong or when the user has to correct you.
  - Mere complexity of the code is not a sufficient reason to comment it though. Only protect code when it is tempting to implement it wrong.
  - Do not add protective comments when user's corrections are a mere clarification of intent.
- Do not balloon the documentation with excessive details that are not necessary to use the code correctly.
- Do not add examples to the documentation unless asked to.

