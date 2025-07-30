"""
Flex message utilities for JSON export, validation, and testing.

This module provides utilities to work with flex messages, including
printing them as JSON for the LINE Flex Message Simulator.
"""

import json
from pathlib import Path
from typing import Any, Optional, Union

from .models import FlexBubble, FlexCarousel, FlexMessage

# Try to import pyperclip for clipboard functionality
_clipboard_available = False
_pyperclip = None
try:
    import pyperclip as _pyperclip

    _clipboard_available = True
except ImportError:
    pass


class FlexMessageJsonPrinter:
    """Service for printing flex messages as JSON format for LINE simulator testing."""

    def __init__(self, indent: int = 2) -> None:
        """
        Initialize the JSON printer.

        Args:
            indent: Number of spaces for JSON indentation

        """
        self.indent = indent

    def print_to_terminal(
        self,
        flex_message: Union[FlexMessage, FlexBubble, FlexCarousel, dict[str, Any]],
        title: Optional[str] = None,
        copy_to_clipboard: bool = True,
    ) -> bool:
        """
        Print flex message as formatted JSON to terminal.

        Args:
            flex_message: Flex message object or dictionary
            title: Optional title to display before JSON
            copy_to_clipboard: Whether to automatically copy JSON to clipboard

        Returns:
            True if successful, False otherwise

        """
        try:
            json_str = self._format_json(flex_message)

            if json_str is None:
                return False

            # Try to copy to clipboard first (if enabled)
            clipboard_success = False
            if copy_to_clipboard:
                clipboard_success = self._copy_to_clipboard(json_str)

            # Print header
            if title:
                print(f"\n{'=' * 60}")
                print(f"📱 FLEX MESSAGE JSON: {title}")
                print(f"{'=' * 60}")
            else:
                print(f"\n{'=' * 60}")
                print("📱 FLEX MESSAGE JSON")
                print(f"{'=' * 60}")

            # Print JSON
            print(json_str)

            # Print footer with enhanced instructions
            print(f"{'=' * 60}")
            print("📋 COPY & PASTE INSTRUCTIONS:")

            if clipboard_success:
                print("✅ JSON copied to clipboard automatically!")
                print("1. Go to: https://developers.line.biz/flex-simulator/")
                print("2. Paste (Cmd+V / Ctrl+V) the JSON in the simulator")
                print("3. Click 'Preview' to test your message")
            else:
                if copy_to_clipboard and not _clipboard_available:
                    print("⚠️  Clipboard not available - manual copy required")
                print("1. Copy the JSON above")
                print("2. Go to: https://developers.line.biz/flex-simulator/")
                print("3. Paste the JSON in the simulator")
                print("4. Click 'Preview' to test your message")

            print(f"{'=' * 60}\n")

            return True

        except Exception as e:
            error_msg = f"Failed to print flex message to terminal: {e}"
            print(f"❌ Error: {error_msg}")
            return False

    def export_to_file(
        self,
        flex_message: Union[FlexMessage, FlexBubble, FlexCarousel, dict[str, Any]],
        filename: str,
        title: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Export flex message JSON to file.

        Args:
            flex_message: Flex message object or dictionary
            filename: Name of the file to create
            title: Optional title to include in file header

        Returns:
            File path if successful, None otherwise

        """
        try:
            json_str = self._format_json(flex_message)

            if json_str is None:
                return None

            # Ensure filename has .json extension
            if not filename.endswith(".json"):
                filename += ".json"

            file_path = Path(filename)

            # Create file content with header
            content: list[str] = []
            if title:
                content.append(f"// FLEX MESSAGE JSON: {title}")
                content.append(f"// Generated on: {self._get_timestamp()}")
                content.append(
                    "// Copy and paste this JSON into LINE Flex Message Simulator",
                )
                content.append("// https://developers.line.biz/flex-simulator/")
                content.append("")

            content.append(json_str)

            # Write to file
            with file_path.open("w", encoding="utf-8") as f:
                f.write("\n".join(content))

            print(f"✅ Flex message exported to: {file_path}")
            return file_path

        except Exception as e:
            error_msg = f"Failed to export flex message to file: {e}"
            print(f"❌ Error: {error_msg}")
            return None

    def validate_flex_message(
        self,
        flex_message: Union[FlexMessage, FlexBubble, FlexCarousel, dict[str, Any]],
    ) -> bool:
        """
        Validate flex message structure.

        Args:
            flex_message: Flex message to validate

        Returns:
            True if valid, False otherwise

        """
        try:
            json_str = self._format_json(flex_message)

            if json_str is None:
                print("❌ Invalid flex message structure")
                return False

            # Basic validation checks
            parsed = json.loads(json_str)

            if not isinstance(parsed, dict):
                print("❌ Flex message must be a dictionary")
                return False

            if "type" not in parsed:
                print("❌ Flex message must have a 'type' field")
                return False

            valid_types = ["bubble", "carousel"]
            if parsed["type"] not in valid_types:
                print(
                    f"❌ Invalid flex message type: {parsed['type']}. Must be one of {valid_types}",
                )
                return False

            print("✅ Flex message is valid!")
            return True

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON structure: {e}")
            return False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False

    def _format_json(
        self,
        flex_message: Union[FlexMessage, FlexBubble, FlexCarousel, dict[str, Any]],
    ) -> Optional[str]:
        """
        Format flex message as JSON string.

        Args:
            flex_message: Flex message to format

        Returns:
            JSON string if successful, None otherwise

        """
        try:
            # Handle FlexMessage wrapper - extract contents
            content_to_format: Any
            if isinstance(flex_message, FlexMessage):
                content_to_format = flex_message.contents
            else:
                content_to_format = flex_message

            # Convert Pydantic model to dict if needed
            if hasattr(content_to_format, "model_dump"):
                message_dict = content_to_format.model_dump(
                    exclude_none=True,
                    by_alias=True,
                )
            elif hasattr(content_to_format, "dict"):
                message_dict = content_to_format.dict(exclude_none=True, by_alias=True)
            else:
                # Assume it's already a dict
                message_dict = content_to_format

            # Format as pretty JSON
            json_str = json.dumps(message_dict, indent=self.indent, ensure_ascii=False)
            return json_str

        except Exception as e:
            print(f"❌ Failed to format JSON: {e}")
            return None

    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _copy_to_clipboard(self, text: str) -> bool:
        """
        Copy text to clipboard with graceful fallback.

        Args:
            text: Text to copy to clipboard

        Returns:
            True if successful, False otherwise

        """
        if not _clipboard_available:
            return False

        try:
            if _pyperclip:
                _pyperclip.copy(text)
                return True
            return False
        except Exception:
            # Graceful fallback if clipboard fails
            return False


# Convenience functions for quick usage
def print_flex_json(
    flex_message: Union[FlexMessage, FlexBubble, FlexCarousel, dict[str, Any]],
    title: Optional[str] = None,
    copy_to_clipboard: bool = True,
) -> bool:
    """
    Quick function to print a flex message as JSON to terminal.

    Args:
        flex_message: Flex message to print
        title: Optional title
        copy_to_clipboard: Whether to automatically copy JSON to clipboard

    Returns:
        True if successful, False otherwise

    """
    printer = FlexMessageJsonPrinter()
    return printer.print_to_terminal(flex_message, title, copy_to_clipboard)


def export_flex_json(
    flex_message: Union[FlexMessage, FlexBubble, FlexCarousel, dict[str, Any]],
    filename: str,
    title: Optional[str] = None,
) -> Optional[Path]:
    """
    Quick function to export a flex message as JSON to file.

    Args:
        flex_message: Flex message to export
        filename: Name of the file
        title: Optional title

    Returns:
        File path if successful, None otherwise

    """
    printer = FlexMessageJsonPrinter()
    return printer.export_to_file(flex_message, filename, title)


def validate_flex_json(
    flex_message: Union[FlexMessage, FlexBubble, FlexCarousel, dict[str, Any]],
) -> bool:
    """
    Quick function to validate a flex message.

    Args:
        flex_message: Flex message to validate

    Returns:
        True if valid, False otherwise

    """
    printer = FlexMessageJsonPrinter()
    return printer.validate_flex_message(flex_message)
