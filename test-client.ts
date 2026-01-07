#!/usr/bin/env node

/**
 * Simple MCP test client to verify the reaper-dev-mcp server works correctly.
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";
import * as path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function testMCP() {
  console.log("🚀 Starting MCP test client...\n");

  // Spawn the MCP server
  const serverPath = path.join(__dirname, "dist", "index.js");
  const serverProcess = spawn("node", [serverPath], {
    stdio: ["pipe", "pipe", "inherit"],
  });

  // Create transport and client
  const transport = new StdioClientTransport({
    command: "node",
    args: [serverPath],
    env: process.env,
  });

  const client = new Client(
    {
      name: "test-client",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  try {
    // Connect to server
    await client.connect(transport);
    console.log("✅ Connected to MCP server\n");

    // Test 1: List resources
    console.log("📚 Test 1: Listing resources...");
    const resources = await client.listResources();
    console.log(`Found ${resources.resources.length} resources:`);
    for (const resource of resources.resources) {
      console.log(`  - ${resource.name}: ${resource.uri}`);
    }
    console.log();

    // Test 2: Read a resource
    console.log("📖 Test 2: Reading a resource...");
    const resource = await client.readResource({
      uri: "reascript://jsfx-fundamentals",
    });
    console.log(`Read resource: ${resource.contents[0].uri}`);
    console.log(`Content length: ${resource.contents[0].text.length} chars\n`);

    // Test 3: List tools
    console.log("🔧 Test 3: Listing tools...");
    const tools = await client.listTools();
    console.log(`Found ${tools.tools.length} tools:`);
    for (const tool of tools.tools) {
      console.log(`  - ${tool.name}: ${tool.description}`);
    }
    console.log();

    // Test 4: Get function info (JSFX)
    console.log("🔍 Test 4: Getting JSFX function info...");
    const jsfxResult = await client.callTool({
      name: "get_function_info",
      arguments: {
        api: "jsfx",
        function_name: "sin",
      },
    });
    console.log("JSFX sin() function:");
    console.log(jsfxResult.content[0].text.substring(0, 200) + "...\n");

    // Test 5: Get function info (ReaScript)
    console.log("🔍 Test 5: Getting ReaScript function info...");
    const reascriptResult = await client.callTool({
      name: "get_function_info",
      arguments: {
        api: "reascript",
        function_name: "TrackFX_GetParam",
      },
    });
    console.log("ReaScript TrackFX_GetParam function:");
    const reascriptData = JSON.parse(reascriptResult.content[0].text);
    console.log(`  Name: ${reascriptData.name}`);
    console.log(`  Available in: ${reascriptData.available_in?.join(", ") || "N/A"}\n`);

    // Test 6: Search functions (ReaWrap)
    console.log("🔍 Test 6: Searching ReaWrap methods...");
    const searchResult = await client.callTool({
      name: "search_functions",
      arguments: {
        api: "reawrap",
        query: "create",
        limit: 5,
      },
    });
    console.log("ReaWrap search results:");
    const searchData = JSON.parse(searchResult.content[0].text);
    for (const result of searchData.slice(0, 3)) {
      console.log(`  - ${result.class}.${result.name}`);
    }
    console.log();

    // Test 7: Get ReaWrap method
    console.log("🔍 Test 7: Getting ReaWrap method info...");
    const reawrapResult = await client.callTool({
      name: "get_function_info",
      arguments: {
        api: "reawrap",
        class_name: "track",
        function_name: "add_fx_by_name",
      },
    });
    console.log("ReaWrap track:add_fx_by_name method:");
    const reawrapText = reawrapResult.content[0].text;
    if (reawrapText.startsWith("ReaWrap method")) {
      console.log(`  ${reawrapText}\n`);
    } else {
      const reawrapData = JSON.parse(reawrapText);
      console.log(`  Class: ${reawrapData.class}`);
      console.log(`  Method: ${reawrapData.name}`);
      console.log(`  Signature: ${reawrapData.signature}\n`);
    }

    console.log("✅ All tests passed!\n");
  } catch (error: any) {
    console.error("❌ Test failed:", error.message);
    if (error.stack) {
      console.error(error.stack);
    }
    process.exit(1);
  } finally {
    await client.close();
    serverProcess.kill();
  }
}

testMCP().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});

