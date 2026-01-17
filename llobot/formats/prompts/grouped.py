"""
Grouped prompt format.
"""
from __future__ import annotations
import html
import re
from llobot.prompts import Prompt
from llobot.formats.prompts import PromptFormat
from llobot.utils.values import ValueTypeMixin

class GroupedPromptFormat(PromptFormat, ValueTypeMixin):
    """
    A prompt format that groups H2 sections into details/summary blocks.

    This format identifies sections starting with `## Title` and wraps them in
    HTML `<details>` elements, using the section title as the summary. Content
    before the first section is left as is.
    """
    _pattern: str

    def __init__(self, pattern: str = r'(?m)^## (.+)$'):
        """
        Creates a new grouped prompt format.

        Args:
            pattern: The regex pattern to identify section headers.
                     Must include one capturing group for the title.
        """
        self._pattern = pattern

    def render(self, prompt: str | Prompt) -> str:
        """
        Renders the prompt by wrapping sections in details/summary blocks.

        Args:
            prompt: The prompt to render.

        Returns:
            The formatted string with grouped sections.
        """
        text = str(prompt)
        parts = re.split(self._pattern, text)

        chunks = []
        # The first part is text before the first header (preamble).
        # We preserve leading whitespace (e.g. indentation) but trim trailing whitespace
        # to ensure clean joining with the first block.
        if parts[0]:
            chunks.append(parts[0].rstrip())

        # Iterate over (title, content) pairs.
        for i in range(1, len(parts), 2):
            title = parts[i]
            content = parts[i+1]

            # Escape title for HTML summary
            summary_title = html.escape(title.strip())

            # Reconstruct the section content.
            full_section = f"## {title}{content}"
            # We only strip the section to avoid excessive whitespace inside details,
            # but we don't normalize internal whitespace to preserve formatting.
            cleaned_section = full_section.strip()

            chunk = f"<details>\n<summary>{summary_title}</summary>\n\n{cleaned_section}\n\n</details>"
            chunks.append(chunk)

        # Join with newlines to separate sections, but respect existing spacing if possible.
        # Since we stripped sections, we add spacing between them.
        return "\n\n".join(chunks).rstrip()

__all__ = [
    'GroupedPromptFormat',
]
