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

Once started, NEXUS Chat provides a simple interface:

```
🌟 NEXUS Chat - Real-time Claude Code Interface
==================================================
🚀 Initializing Claude Code in background...
✅ Claude Code ready for instant responses!

💬 Chat started! Type your questions below.
   Commands: 'exit', 'quit', 'help'
   Tip: Claude Code is already running in background for instant responses!

🤖 You: what files are in the services directory?
🧠 NEXUS: Looking at the services directory, I can see three main subdirectories:

1. **admin-ui** - The admin interface for game administration
2. **gameserver** - The core game logic and API server  
3. **player-client** - The web interface for players

Each service is containerized and can be run independently via Docker Compose.

🤖 You: help me fix the linting errors in player-client
🧠 NEXUS: I'll check for linting errors in the player-client service...
[Streams response in real-time as Claude Code processes the request]
```

## Commands

- `exit`, `quit`, `q` - Exit the chat
- `help`, `h` - Show help information
- Any other input - Pass through to Claude Code

## How It Works

1. **Background Initialization**: When started, NEXUS Chat immediately launches Claude Code CLI in a background thread
2. **Message Queue**: User messages are queued and sent to the Claude Code process
3. **Real-time Streaming**: Responses are captured and streamed back to the user as they're generated
4. **Intelligent Completion**: Uses heuristics to detect when Claude Code has finished responding

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   NEXUS Chat     │───▶│   Claude Code   │
│                 │    │                  │    │   CLI Process   │
│   Terminal      │◀───│   Real-time      │◀───│   Background    │
│   Interface     │    │   Streaming      │    │   Thread        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Technical Details

- **Process Management**: Uses `subprocess.Popen` with line-buffered I/O for real-time communication
- **Threading**: Background thread manages Claude Code process while main thread handles user interaction
- **Queue-based Communication**: Thread-safe queues for message passing between UI and Claude Code
- **Graceful Shutdown**: Proper signal handling and process cleanup

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