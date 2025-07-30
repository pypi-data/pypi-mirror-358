from typing import Any, Dict

from mistune.core import BlockState
from mistune.renderers.markdown import MarkdownRenderer


class TelegramMarkdownRenderer(MarkdownRenderer):
    """Markdown to Telegram Markdown converter."""

    NAME = "telegram_markdown"

    def heading(self, token: Dict[str, Any], state: BlockState) -> str:
        """Convert Markdown heading to Telegram Markdown format."""
        return "*" + self.render_children(token, state) + "*\n\n"

    def strong(self, token: Dict[str, Any], state: BlockState) -> str:
        """Convert Markdown bold to Telegram Markdown format."""
        return "*" + self.render_children(token, state) + "*"

    def emphasis(self, token: Dict[str, Any], state: BlockState) -> str:
        """Convert Markdown italic to Telegram Markdown format."""
        return "_" + self.render_children(token, state) + "_"

    def thematic_break(self, token: Dict[str, Any], state: BlockState) -> str:
        """Convert Markdown thematic break to Telegram Markdown format."""
        return "\n"


__all__ = ["TelegramMarkdownRenderer"]
