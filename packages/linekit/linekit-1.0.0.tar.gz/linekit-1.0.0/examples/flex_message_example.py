"""Example demonstrating flex message functionality."""

from line_api.flex_messages import (
    FlexBox,
    FlexBubble,
    FlexButton,
    FlexButtonStyle,
    FlexLayout,
    FlexMessage,
    FlexMessageAction,
    FlexSeparator,
    FlexText,
    print_flex_json,
)


def create_welcome_message() -> FlexMessage:
    """Create a welcome flex message with header, body, and footer."""
    # Header
    header = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            FlexText.create(
                text="🎉 Welcome to LINE API!",
                weight="bold",
                size="xl",
                color="#1E3A8A",
                align="center",
            ),
        ],
        background_color="#F1F5F9",
        padding_all="20px",
    )

    # Body
    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            FlexText.create(
                text="Thank you for using our LINE API Integration Library!",
                wrap=True,
                color="#555555",
                align="center",
            ),
            FlexSeparator.create(margin="lg"),
            FlexText.create(
                text="Features:",
                weight="bold",
                size="md",
                color="#1E3A8A",
            ),
            FlexText.create(
                text="• Type-safe Flex Message creation",
                size="sm",
                color="#666666",
            ),
            FlexText.create(
                text="• JSON export for LINE simulator",
                size="sm",
                color="#666666",
            ),
            FlexText.create(
                text="• Pydantic validation",
                size="sm",
                color="#666666",
            ),
        ],
        spacing="sm",
        padding_all="20px",
    )

    # Footer
    footer = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            FlexButton.create(
                action=FlexMessageAction(
                    label="Get Started",
                    text="I want to get started!",
                ),
                style=FlexButtonStyle.PRIMARY,
                color="#1E3A8A",
            ),
            FlexButton.create(
                action=FlexMessageAction(
                    label="Learn More",
                    text="Tell me more about the library",
                ),
                style=FlexButtonStyle.SECONDARY,
            ),
        ],
        spacing="sm",
        padding_all="20px",
    )

    # Create bubble
    bubble = FlexBubble.create(
        header=header,
        body=body,
        footer=footer,
    )

    # Create flex message
    return FlexMessage.create(
        alt_text="Welcome to LINE API Integration Library!",
        contents=bubble,
    )


def create_simple_info_message() -> FlexMessage:
    """Create a simple information flex message."""
    body = FlexBox.create(
        layout=FlexLayout.VERTICAL,
        contents=[
            FlexText.create(
                text="📋 Information",
                weight="bold",
                size="lg",
                color="#1E3A8A",
            ),
            FlexText.create(
                text="This is a simple flex message created with the LINE API Integration Library.",
                wrap=True,
                color="#555555",
            ),
            FlexText.create(
                text="✅ Easy to create",
                size="sm",
                color="#00C851",
            ),
            FlexText.create(
                text="✅ Type-safe",
                size="sm",
                color="#00C851",
            ),
            FlexText.create(
                text="✅ Validated with Pydantic",
                size="sm",
                color="#00C851",
            ),
        ],
        spacing="lg",
        padding_all="20px",
    )

    bubble = FlexBubble.create(body=body)

    return FlexMessage.create(
        alt_text="Simple Information Message",
        contents=bubble,
    )


def main() -> None:
    """Demonstrate flex message functionality."""
    print("🚀 LINE API Integration Library - Flex Message Examples\n")

    # Create welcome message
    welcome_message = create_welcome_message()
    print("1. Welcome Message:")
    print_flex_json(welcome_message, "Welcome Message", copy_to_clipboard=True)

    # Create simple info message
    info_message = create_simple_info_message()
    print("\n2. Simple Info Message:")
    print_flex_json(info_message, "Simple Info Message", copy_to_clipboard=True)

    print("🎉 Flex message examples completed!")
    print("\nYou can copy any of the JSON above and test it in:")
    print("🔗 https://developers.line.biz/flex-simulator/")


if __name__ == "__main__":
    main()
