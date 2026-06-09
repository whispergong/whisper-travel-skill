#!/usr/bin/env node
import { execFile } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { promisify } from "node:util";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const execFileAsync = promisify(execFile);

function loadSecrets() {
  const secretsPath = process.env.MCP_SECRETS_FILE || join(homedir(), ".config/mcp/secrets.env");
  if (!existsSync(secretsPath)) return;
  const text = readFileSync(secretsPath, "utf8");
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const match = trimmed.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!match) continue;
    const [, key, rawValue] = match;
    if (process.env[key]) continue;
    process.env[key] = rawValue.replace(/^['"]|['"]$/g, "");
  }
}

function addArg(args, flag, value) {
  if (value === undefined || value === null || value === "") return;
  args.push(flag, String(value));
}

async function runFlyai(args) {
  loadSecrets();
  const flyaiBin = process.env.FLYAI_BIN || "flyai";
  const { stdout, stderr } = await execFileAsync(flyaiBin, args, {
    env: process.env,
    maxBuffer: 1024 * 1024 * 10,
    timeout: 180000
  });
  const output = stdout.trim();
  if (!output) {
    throw new Error(stderr.trim() || "flyai returned empty output");
  }
  try {
    return JSON.parse(output);
  } catch (error) {
    throw new Error(`flyai returned non-JSON output: ${output.slice(0, 500)}`);
  }
}

const server = new McpServer({
  name: "flyai-cli-mcp",
  version: "0.1.0"
});

server.registerTool(
  "search_hotels",
  {
    title: "FlyAI search hotels",
    description: "Search Fliggy/FlyAI hotels via the authenticated flyai CLI.",
    inputSchema: {
      destName: z.string().describe("Destination country/province/city/district"),
      keyWords: z.string().optional().describe("Hotel, area, or keyword filter"),
      poiName: z.string().optional().describe("Nearby POI or attraction"),
      hotelTypes: z.string().optional().describe("酒店, 民宿, or 客栈"),
      sort: z.enum(["distance_asc", "rate_desc", "price_asc", "price_desc", "no_rank"]).optional(),
      checkInDate: z.string().optional().describe("YYYY-MM-DD"),
      checkOutDate: z.string().optional().describe("YYYY-MM-DD"),
      hotelStars: z.string().optional().describe("Comma-separated 1-5"),
      hotelBedTypes: z.string().optional().describe("大床房, 双床房, or 多床房"),
      maxPrice: z.number().int().optional().describe("Max CNY price per night")
    }
  },
  async (input) => {
    const args = ["search-hotel", "--dest-name", input.destName];
    addArg(args, "--key-words", input.keyWords);
    addArg(args, "--poi-name", input.poiName);
    addArg(args, "--hotel-types", input.hotelTypes);
    addArg(args, "--sort", input.sort);
    addArg(args, "--check-in-date", input.checkInDate);
    addArg(args, "--check-out-date", input.checkOutDate);
    addArg(args, "--hotel-stars", input.hotelStars);
    addArg(args, "--hotel-bed-types", input.hotelBedTypes);
    addArg(args, "--max-price", input.maxPrice);
    const result = await runFlyai(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }],
      structuredContent: result
    };
  }
);

server.registerTool(
  "keyword_search",
  {
    title: "FlyAI keyword search",
    description: "Run FlyAI keyword search via the authenticated flyai CLI.",
    inputSchema: {
      query: z.string().describe("Natural-language keyword query")
    }
  },
  async (input) => {
    const result = await runFlyai(["keyword-search", "--query", input.query]);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }],
      structuredContent: result
    };
  }
);

server.registerTool(
  "ai_search",
  {
    title: "FlyAI AI search",
    description: "Run FlyAI semantic AI search via the authenticated flyai CLI.",
    inputSchema: {
      query: z.string().describe("Complete natural-language travel query")
    }
  },
  async (input) => {
    const result = await runFlyai(["ai-search", "--query", input.query]);
    return {
      content: [{ type: "text", text: JSON.stringify(result) }],
      structuredContent: result
    };
  }
);

await server.connect(new StdioServerTransport());
