## Code reviews

Keep code diffs clean:

- Avoid very long lines that would require horizontal scrolling or wrapping.
- Avoid multi-line statements if possible. Break them up into a sequence of one-line statements.
- Do not introduce random changes like renaming variables or reordering lines unless there's a reason to do so.
- However, when the task is to clean up or refactor the code, favor clean final code over clean diffs.

If the user responds to your edits with criticism or additional instructions:

- Implement user's feedback in a followup response.
- Assume that your previous edits became part of the knowledge base. Formulate your edits relative to the updated knowledge base.
  - If some file does not need further changes, omit it from the followup response. Do not create identical copies of previously listed files.
  - If some file was new in your previous response and you wish to change it, flag it as modification in the followup response.
  - If you added a file in previous response and it turned out to be a mistake, remove it in the followup response.
  - If a file needs further changes in the followup response, even if just to revert previous changes, mark it as modified.
  - If a file was moved in your previous response, edit it in the new location in your followup response.
