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

1. **Start the MCP server** in a terminal:

```bash
npx -y reaper-dev-mcp
```

The server will start on `http://localhost:3000` by default. To use a custom port:

```bash
PORT=8080 npx -y reaper-dev-mcp
```

2. **Configure your MCP client** (see configuration sections below) to connect to the running server.

### Option 2: Install from Git

```bash
git clone https://github.com/Conceptual-Machines/reaper-dev-mcp.git
cd reaper-dev-mcp
npm install
npm run build
```

Then start the server:

```bash
npm start
```

Or with a custom port:

```bash
PORT=8080 npm start
```

Then configure your MCP client to use `http://localhost:3000` (or your custom port).

### Configure MCP Client

#### For Cursor IDE

1. **Start the MCP server** in a terminal (see Option 1 above)

2. Open Cursor Settings (Cmd/Ctrl + ,)
3. Search for "MCP" or navigate to MCP settings
4. Add the following configuration:

```json
{
  "mcpServers": {
    "reaper-dev": {
      "url": "http://localhost:3000"
    }
  }
}
```

5. Restart Cursor

**Note:** The server must be running before Cursor starts, or Cursor won't be able to connect.

#### For Claude Desktop

1. **Start the MCP server** in a terminal (see Option 1 above)

2. Locate your Claude Desktop config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

3. Add the MCP server configuration:

```json
{
  "mcpServers": {
    "reaper-dev": {
      "url": "http://localhost:3000"
    }
  }
}
```

4. Restart Claude Desktop

**Note:** The server must be running before Claude Desktop starts, or it won't be able to connect.

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
