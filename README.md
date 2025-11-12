## Prerequisites

Before starting, make sure you have:

- **Python 3.13+** installed on your system
- **Node.js**
- **uv** installed [instructions](https://docs.astral.sh/uv/getting-started/installation/)
- **Claude Code** installed
`npm install -g @anthropic-ai/claude-code`
- **Chrome browser**

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
### 3. Run Your First Module
```bash
uv run 0_querying.py
```
### 4. Configure Local Settings

**Important:** The `.claude/settings.json` file contains system-specific file paths that need to be updated for your local environment.

Edit `.claude/settings.json` and update the sound file paths to match your system. You may also have to update the uv run command path to the absolute path to the python file.

```json
{
  "outputStyle": "Personal Assistant",
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Funk.aiff"
          },
          {
            "type": "command",
            "command": "uv run .claude/hooks/log_agent_actions.py"
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Purr.aiff"
          }
        ]
      }
    ]
  }
}
```