## Code review

- When asked for code review, enumerate issues in the code under review
- If review scope is not specified, review changes made in the current session
- Check that the modified code is complete, correct, and clean, and that it satisfies requirements, adheres to guidelines, and follows conventions
- Treat the project as read-only during code review and do not try to implement any fixes or changes yourself
- When reviewing changes made in the current session and it looks like some information is missing from the context, just point it out instead of trying to retrieve the information yourself
- Do not comment the task itself and do not expand task scope during code review
- Simplicity is also a goal, so refrain from nitpicking that is not supported by any expressly stated requirements, especially if it would result in unnecessarily verbose or complicated code
- Report only issues and refrain from commenting on correct code
- Number review comments for easy reference and use Markdown formatting to make them skimmable
- It is okay to say that everything looks correct, so do not report issues just so that the list of issues is non-empty

### Self-review

- Perform a self-review after completing the current task, usually in the last response that does not include any tool calls
- Apply the above review guidelines to the self-review process accordingly
- If you identify issues during self-review, proceed to fix them immediately

### Responding to code review

- When asked to address/accept/implement issues identified in a code review, make changes accordingly
- When responding to code review performed by the user, who is a human, trust the review unless you are 100% sure the user is wrong
- When responding to a review made by another LLM that joined the chat temporarily, be especially careful and suspicious, because other LLMs might know even less than you do
- Only accept parts of another LLM's code review that you agree with and that you think the user would agree with too
- Reject parts of another LLM's code review that contradict requirements or guidelines, introduce scope creep or unnecessary complexity, or degrade code clarity or quality
- For every rejected review point, explain your reasoning in your response
