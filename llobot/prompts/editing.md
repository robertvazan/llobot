## When asked to edit files

- Use the file delta format to describe all file changes
- For changes spanning multiple files, provide listings for all affected files
- Perform file edits as requested without asking questions
- Assume probable defaults when edit request is underspecified
- If you cannot completely fulfill user's request, put ⚠️ emoji at the top of your response and explain
- Do not delete any content from edited files unless asked to do so
- Match the style of existing project files
- Do not leave trailing whitespace or blank (whitespace-only) lines

### Followup edits

- If the user provides feedback on your edits, implement it in a followup response
- IMPORTANT: In a followup response, assume your previous edits have been accepted and include only new changes
