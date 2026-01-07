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

### Quick Start

Choose your IDE and follow the instructions:

- **[Claude Code CLI](#claude-code-cli)** - Recommended, easiest setup
- **[Cursor IDE](#cursor-ide)** - Works with stdio or HTTP
- **[Claude Desktop](#claude-desktop)** - Requires HTTP server

### Claude Code CLI

**Prerequisites:** Node.js v18+

**Installation (one command):**

```bash
claude mcp add --transport stdio --scope user reaper-dev -- npx -y reaper-dev-mcp
```

**Verify it's working:**

```bash
claude mcp list
```

You should see: `reaper-dev: npx -y reaper-dev-mcp - ✓ Connected`

**That's it!** The server will automatically start when Claude Code needs it. Restart your Claude Code session to use the tools.

---

### Cursor IDE

Cursor supports both stdio and HTTP transports. **Stdio is recommended** (no background process needed).

#### Option A: stdio Transport (Recommended)

**Prerequisites:** Node.js v18+

1. Open Cursor settings:
   - macOS/Linux: `~/.cursor/mcp.json`
   - Windows: `%APPDATA%\Cursor\mcp.json`

2. Add this configuration:

```json
{
  "mcpServers": {
    "reaper-dev": {
      "command": "npx",
      "args": ["-y", "reaper-dev-mcp"]
    }
  }
}
```

3. Restart Cursor

**That's it!** Cursor will spawn the server automatically when needed.

#### Option B: HTTP/SSE Transport

If you prefer HTTP (or stdio doesn't work), use this method:

1. **Start the server** in a terminal (keep it running):
   ```bash
   npx -y reaper-dev-mcp
   ```

   The server will start on `http://localhost:3000`. For a custom port:
   ```bash
   PORT=8080 npx -y reaper-dev-mcp
   ```

2. Open Cursor settings and add:

```json
{
  "mcpServers": {
    "reaper-dev": {
      "type": "sse",
      "url": "http://localhost:3000"
    }
  }
}
```

3. Restart Cursor

**Note:** The server must be running before Cursor starts.

---

### Claude Desktop

Claude Desktop requires HTTP/SSE transport.

**Prerequisites:** Node.js v18+

1. **Start the server** in a terminal (keep it running):
   ```bash
   npx -y reaper-dev-mcp
   ```

   The server will start on `http://localhost:3000`. For a custom port:
   ```bash
   PORT=8080 npx -y reaper-dev-mcp
   ```

2. **Configure Claude Desktop:**

   Locate your config file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

3. Add this configuration:

```json
{
  "mcpServers": {
    "reaper-dev": {
      "type": "sse",
      "url": "http://localhost:3000"
    }
  }
}
```

4. Restart Claude Desktop

**Note:** The server must be running before Claude Desktop starts.

---

### Development Setup

If you want to modify the server or contribute:

```bash
git clone https://github.com/Conceptual-Machines/reaper-dev-mcp.git
cd reaper-dev-mcp
npm install
npm run build
```

Run in development mode:
```bash
npm run dev
```

Run tests:
```bash
npm run test
```

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


## Success Criteria

✅ **No More Token Burn**: Stop rediscovering JSFX parameter indexing every session  
✅ **Fast Problem Solving**: Quick lookup for plink API, container indices  
✅ **Prevent Regressions**: Document all bugs so they're never repeated  
✅ **Reusable Knowledge**: Can be used across all REAPER projects  

## License

MIT
