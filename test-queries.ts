#!/usr/bin/env node

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";

async function runQueries() {
  console.log("🚀 Starting custom MCP queries...\n");

  // Spawn the MCP server
  const serverProcess = spawn("node", ["dist/index.js"], {
    stdio: ["pipe", "pipe", "pipe"],
  });

  const transport = new StdioClientTransport({
    command: "node",
    args: ["dist/index.js"],
  });

  const client = new Client(
    {
      name: "test-queries",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  await client.connect(transport);
  console.log("✅ Connected to MCP server\n");

  // Query 1: Search for parameter link functions in ReaScript
  console.log("📍 Query 1: Searching for parameter link (plink) functions...");
  const plinkSearch = await client.callTool({
    name: "search_functions",
    arguments: {
      api: "reascript",
      query: "plink",
      limit: 5,
    },
  });
  console.log(plinkSearch.content[0].text);
  console.log("\n" + "=".repeat(80) + "\n");

  // Query 2: Get info on TrackFX_SetNamedConfigParm
  console.log("📍 Query 2: Getting TrackFX_SetNamedConfigParm details...");
  const setNamedConfig = await client.callTool({
    name: "get_function_info",
    arguments: {
      api: "reascript",
      function_name: "TrackFX_SetNamedConfigParm",
    },
  });
  console.log(plinkSearch.content[0].text);
  console.log("\n" + "=".repeat(80) + "\n");

  // Query 3: Search ReaWrap container methods
  console.log("📍 Query 3: Searching ReaWrap for container methods...");
  const containerSearch = await client.callTool({
    name: "search_functions",
    arguments: {
      api: "reawrap",
      query: "container",
      limit: 10,
    },
  });
  console.log(containerSearch.content[0].text);
  console.log("\n" + "=".repeat(80) + "\n");

  // Query 4: Get specific ReaWrap method - get_parent_container
  console.log("📍 Query 4: Getting TrackFX:get_parent_container details...");
  const getParent = await client.callTool({
    name: "get_function_info",
    arguments: {
      api: "reawrap",
      class_name: "track_fx",
      function_name: "get_parent_container",
    },
  });
  console.log(getParent.content[0].text);
  console.log("\n" + "=".repeat(80) + "\n");

  // Query 5: Search JSFX slider functions
  console.log("📍 Query 5: Searching JSFX for slider-related functions...");
  const sliderSearch = await client.callTool({
    name: "search_functions",
    arguments: {
      api: "jsfx",
      query: "slider",
      limit: 5,
    },
  });
  console.log(sliderSearch.content[0].text);
  console.log("\n" + "=".repeat(80) + "\n");

  // Query 6: Read parameter modulation resource
  console.log("📍 Query 6: Reading parameter modulation documentation...");
  const resources = await client.listResources();
  const plinkResource = resources.resources.find(r =>
    r.uri === "reascript://parameter-modulation"
  );
  if (plinkResource) {
    const content = await client.readResource({ uri: plinkResource.uri });
    const text = content.contents[0].text as string;
    // Show first 1000 chars
    console.log(text.substring(0, 1000) + "...\n[truncated]");
  }
  console.log("\n" + "=".repeat(80) + "\n");

  console.log("✅ All queries completed!");

  await client.close();
  serverProcess.kill();
}

runQueries().catch(console.error);
