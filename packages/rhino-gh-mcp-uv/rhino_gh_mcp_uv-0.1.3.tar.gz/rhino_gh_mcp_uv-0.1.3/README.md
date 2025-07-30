# RhinoMCP with UV Package Management

RhinoMCP connects Rhino, Grasshopper and more to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control Rhino + Grasshopper. This version uses UV for modern, fast package management and dependency resolution.

## Features

#### Rhino Integration
- **Two-way communication**: Connect Claude AI to Rhino through a socket-based server
- **Object manipulation and management**: Create and modify 3D objects in Rhino including metadata
- **Layer management**: View and interact with Rhino layers
- **Scene inspection**: Get detailed information about the current Rhino scene (incl. screencapture) 
- **Code execution**: Run arbitrary Python code in Rhino from Claude
 
#### Grasshopper Integration
- **Code execution**: Run arbitrary Python code in Grasshopper from Claude - includes the generation of gh components
- **Canvas inspection**: Get detailed information about your Grasshopper definition, including component graph and parameters
- **Component management**: Update script components, modify parameters, and manage code references
- **External code integration**: Link script components to external Python files for better code organization
- **Real-time feedback**: Get component states, error messages, and runtime information
- **Non-blocking communication**: Stable two-way communication via HTTP server

#### AI Integration
- **Replicate API**: Access thousands of AI models via API, including stable diffusion variants
- **Web search**: Integrated web search capabilities
- **Email integration**: Gmail integration for email search and management

## Architecture

The system consists of three main components:

1. **MCP Server** (`src/rhino_gh_mcp_uv/`): Python server implementing the Model Context Protocol
2. **Rhino Plugin** (`plugins/rhino_mcp_client.py`): Socket server running inside Rhino (port 9876)
3. **Grasshopper Plugin** (`plugins/GHCodeMCP_new.py`): HTTP server running inside Grasshopper (port 9999)

## Installation

### Prerequisites

- Rhino 7 or newer
- Python 3.10 or newer
- UV package manager
- A Replicate API token (optional, for AI-powered features)

### Setting up the Environment

1. **Install UV** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or on Windows:
   # powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone and setup the project**:
   ```bash
   cd rhino_gh_mcp_uv
   uv sync  # This creates a virtual environment and installs all dependencies
   ```

3. **Configure environment variables** (optional):
   ```bash
   cp .env.sample .env
   # Edit .env file with your API tokens
   ```

### Installing the Rhino Plugin

1. Open Rhino 7
2. Open the Python Editor:
   - Click on the "Tools" menu
   - Select "Python Script" -> "Run.."
   - Navigate to and select `plugins/rhino_mcp_client.py`
3. The script will start automatically and you should see these messages in the Python Editor:
   ```
   RhinoMCP script loaded. Server started automatically.
   To stop the server, run: stop_server()
   ```

### Installing the Grasshopper Plugin

1. Open Grasshopper
2. Add a GHPython component to your canvas
3. Open the component editor
4. Load the script from `plugins/GHCodeMCP_new.py`
5. The HTTP server will start automatically on port 9999

### Running the MCP Server

With UV, you can run the server in several ways:

1. **Using the installed script**:
   ```bash
   uv run rhino-gh-mcp-uv
   ```

2. **Using the module directly**:
   ```bash
   uv run python -m rhino_gh_mcp_uv.server
   ```

3. **For development**:
   ```bash
   uv run python src/rhino_gh_mcp_uv/main.py
   ```

### Claude Desktop Integration

To integrate with Claude Desktop, add this configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rhino-gh-mcp-uv": {
      "command": "uv",
      "args": ["run", "rhino-gh-mcp-uv"],
      "cwd": "/path/to/rhino_gh_mcp_uv"
    }
  }
}
```

## Usage

### Starting the Complete System

1. **Start Rhino plugin**:
   - Open Rhino 7
   - Run `plugins/rhino_mcp_client.py` in the Python Editor
   - Verify you see the startup messages

2. **Start Grasshopper plugin** (optional):
   - Open Grasshopper
   - Load `plugins/GHCodeMCP_new.py` in a GHPython component
   - The HTTP server starts automatically

3. **Start Claude Desktop**:
   - Claude will automatically start the MCP server when needed
   - The connection between Claude and Rhino/Grasshopper will be established automatically

### Managing the Connection

- **Stop the Rhino server**: In the Python Editor, type `stop_server()` and press Enter
- **Check server status**: Use the logging output in both Rhino and the MCP server
- **Restart connections**: Simply restart the respective components

## Development

### Project Structure

```
rhino_gh_mcp_uv/
├── src/rhino_gh_mcp_uv/          # Main MCP server package
│   ├── __init__.py
│   ├── server.py                 # Main MCP server
│   ├── rhino_tools.py           # Rhino integration tools
│   ├── grasshopper_tools.py     # Grasshopper integration tools
│   ├── replicate_tools.py       # AI rendering tools
│   ├── utility_tools.py         # Web search and email tools
│   └── main.py                  # Entry point
├── plugins/                      # Rhino/Grasshopper plugins
│   ├── rhino_mcp_client.py      # Rhino socket server
│   ├── GHCodeMCP_new.py         # Grasshopper HTTP server
│   └── *.gh                     # Grasshopper definition files
├── pyproject.toml               # UV project configuration
├── .env.sample                  # Environment variables template
└── README.md                    # This file
```

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade
```

### Running Tests

```bash
# Run the server in development mode
uv run python src/rhino_gh_mcp_uv/main.py

# Test individual components
uv run python -c "from rhino_gh_mcp_uv.rhino_tools import RhinoConnection; print('Import successful')"
```

## Benefits of UV Migration

- **Faster dependency resolution**: UV is significantly faster than pip
- **Better dependency management**: More reliable dependency resolution
- **Lockfile support**: Ensures reproducible builds
- **Modern Python packaging**: Uses the latest Python packaging standards
- **Cross-platform compatibility**: Better support across different operating systems
- **Development workflow**: Streamlined development and deployment process

## Troubleshooting

### Common Issues

1. **UV not found**: Make sure UV is installed and in your PATH
2. **Port conflicts**: Ensure ports 9876 (Rhino) and 9999 (Grasshopper) are available
3. **Connection issues**: Check that both Rhino and Grasshopper plugins are running
4. **Import errors**: Run `uv sync` to ensure all dependencies are installed

### Logging

The system provides comprehensive logging:
- **MCP Server**: Logs to console when running
- **Rhino Plugin**: Logs to Rhino command line and log files
- **Grasshopper Plugin**: Logs to Grasshopper console

Log files are stored in platform-specific locations:
- **macOS**: `~/Library/Application Support/RhinoMCP/logs/`
- **Windows**: `%LOCALAPPDATA%/RhinoMCP/logs/`
- **Linux**: `~/.rhino_mcp/logs/`

## License

MIT License - see LICENSE file for details.