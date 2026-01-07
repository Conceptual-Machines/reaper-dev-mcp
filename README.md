# Reaper Dev MCP Server

[![CI](https://github.com/Conceptual-Machines/reaper-dev-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Conceptual-Machines/reaper-dev-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)

MCP (Model Context Protocol) server providing **reference documentation** for REAPER development, ReaScript API, JSFX programming, and ReaWrap API.

## Purpose

This server provides static reference documentation that serves as a lookup reference for factual information about REAPER development. It helps prevent "token burn" by avoiding the need to rediscover common patterns and pitfalls in every session.

## Features

- **Queryable API Documentation**: Use tools to search and get detailed function information
- **JSFX Fundamentals**: Core concepts and gotchas
- **ReaScript API**: Complete function reference with signatures and parameters (2,282 functions across C, EEL2, Lua, Python)
- **ReaWrap API**: Object-oriented wrapper documentation (14 classes, 736 methods)

## Installation

### Prerequisites

- Node.js (v18 or higher)
- npm or npx

### Option 1: Install via npx (Recommended)

You can use the MCP server directly without cloning:

```bash
# For Cursor or Claude Desktop, use this path in your MCP config:
npx -y @conceptual-machines/reaper-dev-mcp
```

Or if published to npm, configure your MCP client with:

```json
{
  "mcpServers": {
    "reaper-dev": {
      "command": "npx",
      "args": ["-y", "@conceptual-machines/reaper-dev-mcp"]
    }
  }
}
```

### Option 2: Install from Git

```bash
git clone https://github.com/Conceptual-Machines/reaper-dev-mcp.git
cd reaper-dev-mcp
npm install
npm run build
```

Then use the local path in your MCP config:

```json
{
  "mcpServers": {
    "reaper-dev": {
      "command": "node",
      "args": ["/absolute/path/to/reaper-dev-mcp/dist/index.js"]
    }
  }
}
```

### Configure MCP Client

#### For Cursor IDE

1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Search for "MCP" or navigate to MCP settings
3. Add the following configuration:

```json
{
  "mcpServers": {
    "reaper-dev": {
      "command": "node",
      "args": ["/absolute/path/to/reaper-dev-mcp/dist/index.js"]
    }
  }
}
```

Replace `/absolute/path/to/reaper-dev-mcp` with the actual path to this directory.

**Example on macOS:**
```json
{
  "mcpServers": {
    "reaper-dev": {
      "command": "node",
      "args": ["/Users/YourUsername/Code/personal/ReaScript/reaper-dev-mcp/dist/index.js"]
    }
  }
}
```

4. Restart Cursor

#### For Claude Desktop

1. Locate your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:

```json
{
  "mcpServers": {
    "reaper-dev": {
      "command": "node",
      "args": ["/absolute/path/to/reaper-dev-mcp/dist/index.js"]
    }
  }
}
```

Replace `/absolute/path/to/reaper-dev-mcp` with the actual path to this directory.

3. Restart Claude Desktop

### Step 5: Verify Installation

Run the test client to verify everything works:

```bash
npm run test
```

You should see all tests passing.

## MCP Tools

### `get_function_info`

Get detailed information about a function from JSFX, ReaScript, or ReaWrap API.

**Parameters:**
- `api` (string): One of "jsfx", "reascript", "reawrap"
- `function_name` (string): Name of the function to look up
- `class_name` (string, optional): Required for ReaWrap API queries

**Examples:**

```json
// JSFX
{
  "api": "jsfx",
  "function_name": "sin"
}

// ReaScript
{
  "api": "reascript",
  "function_name": "TrackFX_GetParam"
}

// ReaWrap
{
  "api": "reawrap",
  "class_name": "track",
  "function_name": "add_fx_by_name"
}
```

### `search_functions`

Search for functions across JSFX, ReaScript, or ReaWrap APIs.

**Parameters:**
- `api` (string): One of "jsfx", "reascript", "reawrap"
- `query` (string): Search query (function name, description, etc.)
- `limit` (number, optional): Maximum number of results (default: 10)

**Examples:**

```json
{
  "api": "reawrap",
  "query": "create",
  "limit": 5
}
```

## Resources

All documentation is available as MCP resources:

- `reascript://jsfx-fundamentals` - Core JSFX concepts
- `reascript://parameter-system` - REAPER parameter system
- `reascript://parameter-modulation` - Parameter linking (plink API)
- `reascript://fx-containers` - FX container system
- `reascript://reawrap-api` - ReaWrap API reference

## API Coverage

The MCP server provides access to:
- **JSFX API**: 110 functions from official REAPER documentation
- **ReaScript API**: 2,282 functions organized by language (C, EEL2, Lua, Python)
- **ReaWrap API**: 14 classes with 736 methods

## Development

### Running in Development Mode

```bash
npm run dev
```

### Testing

```bash
npm run test
```

## Success Criteria

✅ **No More Token Burn**: Stop rediscovering JSFX parameter indexing every session  
✅ **Fast Problem Solving**: Quick lookup for plink API, container indices  
✅ **Prevent Regressions**: Document all bugs so they're never repeated  
✅ **Reusable Knowledge**: Can be used across all REAPER projects  

## License

MIT
