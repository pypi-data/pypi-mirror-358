`````instructions
<SYSTEM>
You are an AI programming assistant that is specialized in applying code changes to an existing document.
Follow Microsoft content policies.
Avoid content that violates copyrights.
If you are asked to generate content that is harmful, hateful, racist, sexist, lewd, violent, or completely irrelevant to software engineering, only respond with "Sorry, I can't assist with that."
Keep your answers short and impersonal.
The user has a code block that represents a suggestion for a code change and a instructions file opened in a code editor.
Rewrite the existing document to fully incorporate the code changes in the provided code block.
For the response, always follow these instructions:
1. Analyse the code block and the existing document to decide if the code block should replace existing code or should be inserted.
2. If necessary, break up the code block in multiple parts and insert each part at the appropriate location.
3. Preserve whitespace and newlines right after the parts of the file that you modify.
4. The final result must be syntactically valid, properly formatted, and correctly indented. It should not contain any ...existing code... comments.
5. Finally, provide the fully rewritten file. You must output the complete file.
</SYSTEM>

# 🤖 LINE API Integration Library - AI Agent Context

## Project Overview

**LINE API Integration Library** is a comprehensive, type-safe Python library for integrating with LINE's APIs. It provides modern async/await patterns, full Pydantic type safety, and covers all major LINE platform features including Messaging API, Flex Messages, Rich Menus, LINE Login, LIFF, and Mini Apps.

## 🎯 Core Purpose

- **Comprehensive LINE Integration**: One library for all LINE platform APIs
- **Type Safety**: Full Pydantic integration with comprehensive type hints
- **Modern Async**: Built for high-performance async/await operations
- **Developer Experience**: Rich IDE support, auto-completion, and detailed documentation
- **Production Ready**: Comprehensive testing, error handling, and best practices
- **Extensible Architecture**: Modular design for easy feature additions

## 🏗️ Architecture & Tech Stack

### Core Framework

- **Python 3.11+**: Modern Python with enhanced type hints and performance
- **Async-First Design**: All I/O operations use async/await patterns
- **Pydantic 2.x**: Data validation, settings management, and type safety
- **Official LINE SDK**: Built on top of `line-bot-sdk` for reliability
- **HTTPX**: Modern async HTTP client for external API calls

### Dependencies & Package Management

- **Core**: `line-bot-sdk>=3.17.0`, `pydantic>=2.8.0`, `httpx>=0.27.0`
- **Web Framework**: `fastapi>=0.111.0`, `uvicorn>=0.30.0`
- **Development**: `pytest>=8.3.0`, `mypy>=1.11.0`, `ruff>=0.5.0`
- **Package Management**:
  - Using `uv` for fast, reliable Python package management
  - All dependencies managed via `uv sync`
  - Development setup with `uv sync --dev`
  - Virtual environments handled by `uv venv`

### Design Principles

- **Single Responsibility**: Each module has a clear, focused purpose
- **Type Safety**: Full type hints throughout with Pydantic validation
- **Error Handling**: Comprehensive error handling with typed exceptions
- **Async-First**: All I/O operations use async/await patterns
- **Modular Architecture**: Clean separation between different LINE API services

## 📁 Project Structure

```
line-api/
├── .github/copilot-instructions.md # This file - AI agent context
├── README.md                       # User documentation and usage examples
├── pyproject.toml                  # Dependencies and tool configurations
├── line-api.code-workspace         # VS Code workspace configuration
├── line_api/                       # Main package directory
│   ├── core/                       # Core configuration and utilities
│   ├── messaging/                  # LINE Messaging API implementation
│   ├── webhook/                    # Webhook handling and event processing
│   ├── flex_messages/              # Flex Message components and utilities
│   ├── rich_menu/                  # Rich Menu management
│   ├── login/                      # LINE Login OAuth2 integration
│   └── liff/                       # LIFF app lifecycle management
├── tests/                          # 🧪 Comprehensive Test Suite
│   ├── __init__.py
│   ├── test_messaging.py           # Messaging API tests
│   ├── test_webhook.py             # Webhook processing tests
│   ├── test_flex_messages.py       # Flex Messages tests
│   └── ...                         # Additional test modules
├── examples/                       # 📚 Usage Examples
│   ├── webhook_example.py          # FastAPI webhook handler
│   ├── flex_message_example.py     # Flex Message creation
│   └── push_message_example.py     # Basic message sending
├── docs/                           # 📖 Documentation
│   ├── api/                        # API reference documentation
│   ├── guides/                     # Usage guides and tutorials
│   └── examples/                   # Detailed examples
├── scripts/                        # 🔧 Development Scripts
│   └── ...                         # API testing script
└── debug/                          # 🐛 Debug Scripts (gitignored)
    └── ...                         # Temporary debug and investigation scripts
```

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# LINE Bot Configuration (for Messaging API)
LINE_CHANNEL_ACCESS_TOKEN=your_line_bot_token
LINE_CHANNEL_SECRET=your_line_bot_secret

# LINE Login Configuration (optional)
LINE_API_LOGIN_CHANNEL_ID=your_login_channel_id
LINE_API_LOGIN_CHANNEL_SECRET=your_login_channel_secret

# LIFF Configuration (optional)
LINE_API_LIFF_CHANNEL_ID=your_liff_channel_id

# Development Configuration
LINE_API_DEBUG=true
LINE_API_TIMEOUT=30
LINE_API_MAX_RETRIES=3
```

### Configuration Loading

- **Automatic Discovery**: Searches for `.env` file in current directory and parent directories
- **Environment Override**: Environment variables override `.env` file values
- **Pydantic Validation**: All configuration validated with Pydantic models
- **Type Safety**: Full type hints and validation for all settings

## 🚀 Core Modules

### 1. Core Configuration (`core/`)

**Purpose**: Centralized configuration management using Pydantic Settings

**Key Features**:

- Automatic `.env` file discovery and loading
- Environment variable validation with Pydantic
- Type-safe configuration across all services
- Secure credential management

**Usage**:


### 2. Messaging API (`messaging/`)

**Purpose**: Complete LINE Messaging API implementation with webhook support

**Key Features**:

- Full Messaging API coverage (reply, push, multicast, broadcast)
- Webhook parser with signature verification
- User profile management
- Message validation and error handling
- Rate limiting and retry mechanisms

**Usage**:

```python
from line_api import LineMessagingClient, LineAPIConfig, TextMessage

async with LineMessagingClient(LineAPIConfig()) as client:
    await client.push_message("USER_ID", [TextMessage(text="Hello!")])
```

### 3. Webhook Processing (`webhook/`)

**Purpose**: Complete webhook handling for LINE Platform events

**Key Features**:

- Type-safe webhook event models with Pydantic validation
- Signature verification utilities for security
- Flexible event handler system with decorators
- Comprehensive error handling and logging
- Support for all LINE webhook event types

**Usage**:

```python
from line_api.webhook import LineWebhookHandler
from fastapi import FastAPI, Request

handler = LineWebhookHandler(config)

@handler.message_handler
async def handle_message(event: LineMessageEvent) -> None:
    # Process message events
    pass

@app.post("/webhook")
async def webhook(request: Request):
    return await handler.handle_webhook(
        await request.body(),
        request.headers.get("X-Line-Signature"),
        await request.json()
    )
```



### 4. Flex Messages (`flex_messages/`)

**Purpose**: Type-safe Flex Message creation with Pydantic models

**Key Features**:

- Complete Flex Message component support (FlexBox, FlexBubble, FlexText, etc.)
- Type-safe creation with Pydantic validation
- JSON export for LINE simulator testing
- Automatic clipboard copy functionality
- No deprecated components (FlexSpacer removed)
- Custom component creation with factory methods

**Usage**:

```python
from line_api.flex_messages import (
    FlexBox, FlexBubble, FlexLayout, FlexMessage, FlexText,
    print_flex_json, export_flex_json
)

# Create components
title = FlexText.create("Welcome!", weight="bold", size="xl")
body = FlexBox.create(layout=FlexLayout.VERTICAL, contents=[title])
bubble = FlexBubble.create(body=body)
message = FlexMessage.create(alt_text="Welcome", contents=bubble)

# Export for testing
print_flex_json(message, "My Message")  # Auto-copies to clipboard
export_flex_json(message, "welcome.json")  # Save to file
```
### 5. Rich Menu Management (`rich_menu/`)

**Purpose**: Complete Rich Menu lifecycle management

**Key Features**:

- Rich Menu creation and management
- Image upload and validation
- User-specific rich menu assignment
- Template system for common layouts
- Bulk operations for multiple users

**Usage**:



### 6. LINE Login (`login/`)

**Purpose**: OAuth2 authentication and user management

**Key Features**:

- Complete OAuth2 flow implementation
- User profile management
- Token validation and refresh
- Scope management
- Secure token storage patterns

**Usage**:



### 7. LIFF Management (`liff/`)

**Purpose**: LIFF (LINE Front-end Framework) app management

**Key Features**:

- LIFF app creation and management
- View configuration and updates
- App lifecycle management
- Integration with web applications

**Usage**:



## 🧪 Testing Strategy

### Test Infrastructure



## ⚠️ AI Agent File Deletion Limitation

When using AI models such as GPT-4.1, GPT-4o, or any model that cannot directly delete files, be aware of the following workflow limitation:

- **File Deletion Restriction**: The AI model cannot perform destructive actions like deleting files from the filesystem. Its capabilities are limited to editing file contents only.
- **User Action Required**: If you need to remove a file, the AI will provide the appropriate terminal command (e.g., `rm /path/to/file.py`) for you to run manually.
- **Safety Rationale**: This restriction is in place to prevent accidental or unauthorized file deletion and to ensure user control over destructive actions.
- **Workflow Guidance**: Always confirm file removal by running the suggested command in your terminal or file manager.

## � AI Agent Instructions

When working with this project:

1. **Understand the Architecture**: This is a comprehensive LINE API integration library built for production use
2. **Follow Modern Python Patterns**:
   - Use async/await for all I/O operations
   - Full type hints throughout the codebase
   - Pydantic models for data validation
   - Context managers for resource management
3. **Type Safety First**:
   - All functions must have complete type annotations
   - Use Pydantic models for data structures
   - Validate inputs and outputs
   - Leverage IDE type checking support
4. **Error Handling**:
   - Use typed exceptions for different error scenarios
   - Implement proper retry mechanisms
   - Log errors with structured logging
   - Provide helpful error messages
5. **Testing**:
   - Write tests for all new functionality
   - Use async testing patterns
   - Mock external APIs appropriately
   - Include integration tests for critical paths
6. **Documentation**:
   - Comprehensive docstrings for all public functions
   - Include usage examples in docstrings
   - Update README.md for new features
   - Maintain API documentation
7. **Code Quality**:
   - Use `ruff` for linting and formatting
   - Run `mypy` for type checking
   - Follow the existing code style
   - Keep functions focused and small
8. **Performance**:
   - Use async patterns for I/O operations
   - Implement proper rate limiting
   - Cache responses when appropriate
   - Monitor memory usage for large operations
9. **Flex Messages Specific**:
   - Use factory methods (.create()) for all components
   - Never use deprecated FlexSpacer (removed from LINE spec)
   - Always provide alt_text for FlexMessage
   - Use print_flex_json() for testing with auto-clipboard
   - Validate JSON output in LINE Flex Message Simulator
10. **Webhook Processing Specific**:
   - Always verify LINE signatures for security
   - Use decorator-based event handlers for clean code organization
   - Handle all event types gracefully with proper error logging
   - Implement duplicate event detection for reliability
   - Use proper HTTP status codes (200 for success, 401 for invalid signature)
   - Log all webhook events for debugging and monitoring

### Development Guidelines

#### Adding New Features

1. **Plan the API**: Design the public interface first
2. **Write Tests**: Start with test cases for the new feature
3. **Implement**: Create the implementation with full type hints
4. **Document**: Add comprehensive docstrings and examples
5. **Integration**: Update the main `LineAPI` class if needed
6. **Validate**: Run all tests and type checking

#### Code Organization Rules

- **Clean Imports**: All imports at the top of files
- **Debug Scripts**: All debug/investigation scripts MUST go in `/debug` folder (gitignored)
- **Tests**: All pytest tests MUST go in `/tests` folder
- **Examples**: Real-world examples in `/examples` folder
- **Documentation**: API docs and guides in `/docs` folder

#### Error Handling Patterns

```python


### Production Considerations

- **Rate Limiting**: Implement proper rate limiting for all API calls
- **Error Recovery**: Retry mechanisms with exponential backoff
- **Logging**: Structured logging for debugging and monitoring
- **Security**: Secure credential management and validation
- **Performance**: Async operations and connection pooling
- **Monitoring**: Health checks and metrics collection
````
### Commit Message Instructions

1. **Use clear section headers** (e.g., 🎯 New Features, 🛠️ Technical Implementation, 📁 Files Added/Modified, ✅ Benefits, 🧪 Tested)
2. **Summarize the purpose and impact** of the change in the first line
3. **List all new and modified files** with brief descriptions
4. **Highlight user and technical benefits** clearly
5. **Note any testing or validation** performed
6. **Use bullet points** (•) for better readability
7. **Include relevant emojis** for visual organization
8. **Keep descriptions concise** but informative

### Key Files for AI Understanding

- **README.md**: User-facing documentation and usage examples
- **pyproject.toml**: Dependencies and project configuration
- **Module `__init__.py` files**: Public API exports and module structure
- **Test files**: Examples of proper usage and expected behavior
- **Integration guides**: Patterns for using shared tools in services

The shared tools package is the foundation of the StockLatte ecosystem, providing consistent patterns and utilities that enable rapid development of new services while maintaining code quality and consistency across the platform.
`````
