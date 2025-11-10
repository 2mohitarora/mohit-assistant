# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal assistant project built with the Claude Agent SDK. The project uses Python 3.13+ and demonstrates both one-off queries and stateful conversation sessions with Claude.

## Environment Setup

The project uses `uv` for dependency management. To set up the environment:

```bash
uv sync
```

This creates a virtual environment and installs all dependencies including:
- `claude-agent-sdk` - Core SDK for building Claude agents
- `nest-asyncio` - Enables asyncio in interactive environments
- `python-dotenv` - Environment variable management
- `rich` - Terminal formatting

## Running Code

All Python files are executable scripts. Run them with:

```bash
uv run <filename>.py
```

For example:
```bash
uv run 0_querying.py
```

## API Key Configuration (Optional)

The project can work with either:
1. Claude Code authentication (no API key needed)
2. Anthropic API key set in `.env`:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Architecture

The codebase demonstrates two patterns for interacting with Claude:

1. **`query()` function**: For one-off, stateless queries. Each call starts a new session.

2. **`ClaudeSDKClient` class**: For continuous conversations with persistent state. Use context manager pattern for proper connection handling:
   ```python
   async with ClaudeSDKClient(options=options) as client:
       await client.query(prompt)
       async for message in client.receive_response():
           # Process messages
   ```

Use `ClaudeAgentOptions` to configure agent behavior (model selection, etc.).

The SDK requires asyncio event loop. Use `nest_asyncio.apply()` for interactive/Jupyter environments.
