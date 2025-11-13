"""
Options are used to configure the agent's behavior.

Need to try different combinations of option settings such as allowed_tools vs permission_mode to understand how they interact and precedence.

For more details, see:
https://docs.claude.com/en/api/agent-sdk/python#claudeagentoptions
"""

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from rich import print
from rich.console import Console
from cli_tools import parser, print_rich_message, parse_and_print_message
from dotenv import load_dotenv
load_dotenv()



async def main():
    console = Console()
    args = parser.parse_args()


    options = ClaudeAgentOptions(
        model=args.model,
        allowed_tools=[
            "Read",
            "Write",
            "mcp__filesystem__*"  # Allow all filesystem MCP tools from .mcp.json
        ],
        disallowed_tools=["WebSearch", "WebFetch"],
        permission_mode="acceptEdits",
        setting_sources=["project"],  # This loads .claude/settings.json
        mcp_servers=".mcp.json",  # Load MCP servers from .mcp.json file
        # settings='{"outputStyle": "default"}',
        # system_prompt="You are a pirate. You must respond like a pirate.",
        # add_dirs=["."], # allow access to other directories
    )

    print_rich_message(
        "system",
        f"Welcome to Mohit's Assistant!\n\nSelected model: {args.model}",
        console
        )

    async with ClaudeSDKClient(options=options) as client:

        input_prompt = "Hi, what's your name?"
        print_rich_message("user", input_prompt, console)

        await client.query(input_prompt)

        async for message in client.receive_response():
            # Uncomment to print raw messages for debugging
            # print(message)
            parse_and_print_message(message, console)


if __name__ == "__main__":
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.run(main())