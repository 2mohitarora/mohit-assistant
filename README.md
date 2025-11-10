## Prerequisites

Before starting, make sure you have:

- **Python 3.13+** installed on your system
- **uv** installed [instructions](https://docs.astral.sh/uv/getting-started/installation/)
- **Claude Code** installed
`npm install -g @anthropic-ai/claude-code`
- **Chrome browser**
- **Node.js**

Optional:
You can either use an Anthropic API key or authenticate with Claude Code. If authenticating with Claude Code, you don't need to set an API key.
- **Anthropic API key** (get one at [console.anthropic.com](https://console.anthropic.com))

## Quick Start
### 1. Set Up Environment

Create a virtual environment and install dependencies:

```bash
uv sync
```
### 2. Configure API Key (Optional)

If you are using an Anthropic API key (see prerequisites above),

Create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```
