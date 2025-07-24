## Code reviews

Keep diffs clean to streamline code reviews:

- Perform only one simple action on every line
- Break multi-line statements into a sequence of one-line statements
- In documentation, break lines at logical boundaries (sentences, clauses) when the text does not fit on one line
- Write well-structured code that is simple and obviously correct
- In inherently complex code, add explanatory comments and full documentation
- When making a small edit, keep line order and variable names the same if possible to minimize diff noise
- Exception: When performing cleanup or refactoring, optimize for clean final code instead of clean diffs

If the user responds to your edits with comments, implement user's feedback in a followup response.

Formulate followup edits relative to already performed edits:

- If a file does not need further changes, leave it out of the followup response
- If a file was new in the previous response, flag it as modified in the followup response
- If a file was moved in the previous response, do not flag it as moved again in the followup response
- If you want to undo adding a file, remove it in the followup response
