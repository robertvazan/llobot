## Code review

- When asked for code review, enumerate issues in the code under review.
- If review scope is not specified, review changes made in the current session.
- Flag incomplete and incorrect code, unnecessary complexity, inconsistency with requirements, guidelines, and conventions, and failure to run full quality checks (build, tests, ...).
- Treat the project as read-only during code review. Do not implement any changes yourself.
- When reviewing the current session, do not run any tools at all. If information is missing in the context, just point it out.
- Do not comment the task itself and do not expand task scope during code review.
- It is okay to point out minor issues. However, refrain from nitpicking when a fix would add verbosity or complexity.
- In particular, do not demand excessively defensive code, especially in tests.
- Report only issues and refrain from commenting on correct code.
- Number review comments for easy reference and use Markdown formatting to make them skimmable.
- It is okay to say that everything looks correct. Do not report issues just so that the list of issues is non-empty.

### Self-review

- Perform a self-review after completing the current task, usually in the last response that does not include any tool calls.
- Apply the above review guidelines to the self-review process accordingly.
- If you identify issues during self-review, proceed to fix them immediately.

### Responding to code review

- When asked to address issues identified in a code review, take all necessary actions to fully resolve the issues.
- When responding to a review performed by a human user, trust the review unless you are 100% sure the user is wrong.
- When responding to a review written by another LLM, assume the review might be incorrect. Accept only feedback that you wholeheartedly agree with. Disregard everything else.
- Disregard parts of another LLM's review that contradict requirements or guidelines, introduce scope creep, or make the code more verbose or complicated with little benefit.
- For every rejected review point, explain your reasoning in your response.
