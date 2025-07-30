import logging
import re
from datetime import datetime
from typing import Any

import polars as pl


class NotionPageContents:
    def __init__(self, contents: list[dict[str, Any]]):
        self._contents = contents

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(blocks={len(self._contents)})"

    def __repr__(self) -> str:
        return f"<{self.__str__()}>"

    @property
    def logger(self) -> logging.Logger:
        """
        Logger for the class.
        """
        return logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def contents(self) -> list[dict[str, Any]]:
        """
        The raw data of the page as returned by the Notion API.
        """
        return self._contents

    def as_plain_text(self) -> str:
        """
        Convert the page contents to a plain text string.
        """
        text_blocks = []
        for block in self._contents:
            block_type = block["type"]
            rich_text = block[block_type].get("rich_text", [])
            if not rich_text:
                text = ""
            else:
                text = "".join(
                    [rt["text"]["content"] for rt in rich_text if "text" in rt]
                )
            text_blocks.append(text)
        return "\n".join(text_blocks)

    def as_markdown(self) -> str:
        """
        Convert the page contents to a Markdown string.
        """
        md_blocks = []
        for block in self._contents:
            block_type = block["type"]
            md_block = self._parse_to_md(block_type, block)
            md_blocks.append(md_block)
        return "\n\n".join(md_blocks)

    def _rich_text_to_md(self, rich_text: list[dict[str, Any]]) -> str:
        """
        Convert a list of rich text objects to a Markdown string.
        """
        text_parts = []
        for part in rich_text:
            text = part.get("text", {}).get("content", "")
            text_link = part.get("text", {}).get("link", {})
            if text_link and text_link.get("url"):
                url = text_link["url"]
                text = f"[{text}]({url})"
            is_bold = part.get("annotations", {}).get("bold", False)
            is_italic = part.get("annotations", {}).get("italic", False)
            is_underline = part.get("annotations", {}).get("underline", False)
            is_strikethrough = part.get("annotations", {}).get("strikethrough", False)
            is_code = part.get("annotations", {}).get("code", False)
            if is_bold:
                text = f"**{text}**"
            if is_italic:
                text = f"*{text}*"
            if is_underline:
                text = f"_{text}_"
            if is_strikethrough:
                text = f"~~{text}~~"
            if is_code:
                text = f"`{text}`"
            text_parts.append(text)
        return "".join(text_parts)

    def _parse_to_md(self, block_type: str, content: dict[str, Any]) -> str:
        """
        Convert the block type and text to a Markdown string.
        """
        heading_regex = re.compile(r"heading_(\d)")
        heading_match = heading_regex.match(block_type)
        block_content = content[block_type]
        rich_text = block_content.get("rich_text", [])
        if not rich_text:
            return ""
        text = self._rich_text_to_md(rich_text)
        if heading_match:
            level = int(heading_match.group(1))
            return "#" * level + " " + text
        match block_type:
            case "paragraph":
                return text
            case "bulleted_list_item":
                return "- " + text
            case "numbered_list_item":
                return "1. " + text
            case "to_do":
                is_marked = block_content["checked"]
                return ("- [x] " if is_marked else "- [ ] ") + text
            case _:
                self.logger.debug(f"Found unknown block type: '{block_type}'")
                return text

    def _parse_dtime(self, dt_str: str) -> datetime:
        """
        Parse a datetime string from the Notion API into a datetime object.
        """
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))

    def as_records(self) -> list[dict[str, Any]]:
        """
        Convert the page contents to a list of dictionaries.
        """
        records = []
        for idx, block in enumerate(self._contents):
            block_type = block["type"]
            block_content = block[block_type]
            rich_text = block_content.get("rich_text", [])
            record = {
                "block_number": idx + 1,
                "id": block["id"],
                "type": block_type,
                "rich_text": block_content.get("rich_text"),
                "plain_text": rich_text[0].get("plain_text") if rich_text else "",
                "created_time": block.get("created_time"),
                "last_edited_time": block.get("last_edited_time"),
                "created_by": block.get("created_by", {}).get("id"),
                "last_edited_by": block.get("last_edited_by", {}).get("id"),
                "color": block_content.get("color"),
                "parent": block.get("parent", {}).get("page_id"),
                "has_children": block.get("has_children"),
                "archived": block.get("archived"),
                "in_trash": block.get("in_trash"),
                "compiled_md": self._parse_to_md(block_type, block),
            }
            if record.get("created_time"):
                record["created_time"] = self._parse_dtime(record["created_time"])
            if record.get("last_edited_time"):
                record["last_edited_time"] = self._parse_dtime(
                    record["last_edited_time"]
                )
            records.append(record)
        return records

    def as_dataframe(self) -> pl.DataFrame:
        """
        Convert the page contents to a Polars DataFrame.
        """
        return pl.from_records(self.as_records())
