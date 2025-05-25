# NEXUS Chat - Real-time Claude Code Interface

A lightweight wrapper around Claude Code CLI that provides instant responses through background process management and real-time streaming.

## Features

- 🚀 **Instant Responses**: Pre-initializes Claude Code in background for zero-delay interactions
- 🌊 **Real-time Streaming**: Responses stream back as they're generated, no waiting
- 🔄 **Pass-through Interface**: Full access to Claude Code's capabilities through simple chat
- 🛡️ **Graceful Handling**: Proper shutdown and error handling

## Quick Start

```bash
# Make sure Claude Code CLI is installed
curl -fsSL https://install.anthropic.com | sh

# Run NEXUS Chat
python nexus-chat.py
```

## Usage

NEXUS Chat provides a simple chat interface that calls Claude Code for each message:

```bash
# Example: Pipe a question to NEXUS Chat
echo "Hello, what is 2+2?" | python nexus-chat.py

# Example: Interactive session
python nexus-chat.py
```

**Interactive Session Example:**
```
🌟 NEXUS Chat - Real-time Claude Code Interface
==================================================
🚀 Initializing Claude Code...
✅ Claude Code ready for instant responses!

💬 Chat started! Type your questions below.
   Commands: 'exit', 'quit', 'help'
   Tip: Claude Code is already running in background for instant responses!

🤖 You: Hello, what is 2+2?
🧠 NEXUS: 4
────────────────────────────────────────

🤖 You: what files are in the services directory?
🧠 NEXUS: I can see three main services in your project:

1. **gameserver/** - FastAPI backend with SQLAlchemy
2. **player-client/** - React frontend for players  
3. **admin-ui/** - React admin interface

All services are containerized with Docker Compose.
────────────────────────────────────────

🤖 You: exit
👋 Goodbye! Thanks for using NEXUS Chat!
```

## Commands

- `exit`, `quit`, `q` - Exit the chat
- `help`, `h` - Show help information
- Any other input - Pass through to Claude Code

## How It Works

1. **Initialization**: NEXUS Chat tests Claude Code CLI availability on startup
2. **Per-Message Calls**: Each user message triggers a new Claude Code process call
3. **JSON Streaming**: Uses `--print --output-format stream-json` for structured responses
4. **Real-time Display**: Parses JSON stream and displays content as it arrives

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   NEXUS Chat     │───▶│   Claude Code   │
│                 │    │                  │    │   CLI --print   │
│   Terminal      │◀───│   JSON Parser    │◀───│   JSON Stream   │
│   Interface     │    │   & Display      │    │   Response      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Technical Details

- **Claude Code Integration**: Uses `claude --print --output-format stream-json --verbose` for non-interactive calls
- **JSON Streaming**: Parses real-time JSON responses for clean text extraction
- **Process Management**: Each message creates a new subprocess for isolation
- **Error Handling**: Captures both stdout and stderr for comprehensive error reporting

## Requirements

- Python 3.7+
- Claude Code CLI installed and accessible in PATH
- Project must be in a directory that Claude Code can access

## Error Handling

- Automatic detection if Claude Code CLI is not installed
- Graceful handling of process failures
- Timeout protection for unresponsive processes
- Clean shutdown on interruption signals

## Performance

- **Cold Start**: ~2-3 seconds (one-time background initialization)
- **Response Time**: Near-instant (process already running)
- **Streaming**: Real-time output as Claude Code generates responses
- **Memory**: Minimal overhead (single background process + queues)

## Troubleshooting

### Claude Code not found
```bash
# Install Claude Code CLI
curl -fsSL https://install.anthropic.com | sh

# Verify installation
claude --version
```

### Permission errors
```bash
# Make script executable
chmod +x nexus-chat.py
```

### Slow responses
- Check that Claude Code CLI is working properly: `claude --version`
- Ensure you're in a project directory that Claude Code can access
- Check internet connectivity for Claude API access

## Contributing

This is a simple wrapper script designed to be lightweight and focused. For feature requests or bugs, please consider:

1. Whether the feature belongs in Claude Code CLI itself
2. If the change maintains the simple, focused nature of this wrapper
3. Testing any changes thoroughly with the background process management

## License

Same as the main Sectorwars2102 project.