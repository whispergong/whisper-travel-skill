#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const endpoint = process.env.AIGOHOTEL_MCP_URL || "https://mcp.aigohotel.com/mcp";

function loadSecrets() {
  const secretsPath = process.env.MCP_SECRETS_FILE || join(homedir(), ".config/mcp/secrets.env");
  if (!existsSync(secretsPath)) return;
  for (const line of readFileSync(secretsPath, "utf8").split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const match = trimmed.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!match) continue;
    const [, key, rawValue] = match;
    if (!process.env[key]) process.env[key] = rawValue.replace(/^['"]|['"]$/g, "");
  }
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (!arg.startsWith("--")) {
      args._.push(arg);
      continue;
    }
    const key = arg.slice(2);
    const next = argv[index + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
    } else {
      args[key] = next;
      index += 1;
    }
  }
  return args;
}

async function rpc(method, params = {}) {
  loadSecrets();
  const token = process.env.AIGOHOTEL_API_KEY;
  if (!token) throw new Error("AIGOHOTEL_API_KEY is missing");
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream"
    },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params })
  });
  const text = await response.text();
  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    throw new Error(`AIGoHotel returned non-JSON response (${response.status}): ${text.slice(0, 500)}`);
  }
  if (!response.ok || payload.error) {
    throw new Error(payload.error?.message || `AIGoHotel HTTP ${response.status}`);
  }
  return payload.result;
}

function numberOrUndefined(value) {
  if (value === undefined || value === true || value === "") return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0] || "help";

  if (command === "initialize") {
    const result = await rpc("initialize", {
      protocolVersion: "2025-03-26",
      capabilities: {},
      clientInfo: { name: "hotel-search-cn", version: "0.1.0" }
    });
    console.log(JSON.stringify(result));
    return;
  }

  if (command === "tools-list") {
    const result = await rpc("tools/list");
    console.log(JSON.stringify(result));
    return;
  }

  if (command === "search") {
    const argumentsPayload = {
      originQuery: args.query || "酒店搜索",
      place: args.place,
      placeType: args["place-type"] || "详细地址",
      countryCode: args["country-code"] || "CN",
      size: numberOrUndefined(args.size) || 10
    };
    const checkInDate = args["check-in-date"];
    const stayNights = numberOrUndefined(args.nights);
    const adultCount = numberOrUndefined(args.adults);
    if (checkInDate || stayNights || adultCount) {
      argumentsPayload.checkInParam = {};
      if (checkInDate) argumentsPayload.checkInParam.checkInDate = checkInDate;
      if (stayNights) argumentsPayload.checkInParam.stayNights = stayNights;
      if (adultCount) argumentsPayload.checkInParam.adultCount = adultCount;
    }
    const distanceInMeter = numberOrUndefined(args.distance);
    if (distanceInMeter) argumentsPayload.filterOptions = { distanceInMeter };
    const maxPricePerNight = numberOrUndefined(args["max-price"]);
    if (maxPricePerNight) argumentsPayload.hotelTags = { maxPricePerNight };

    const result = await rpc("tools/call", {
      name: "searchHotels",
      arguments: argumentsPayload
    });
    console.log(JSON.stringify(result));
    return;
  }

  if (command === "detail") {
    const argumentsPayload = {
      name: args.name,
      dateParam: {
        checkInDate: args["check-in-date"],
        checkOutDate: args["check-out-date"]
      },
      occupancyParam: {
        adultCount: numberOrUndefined(args.adults) || 2,
        childCount: numberOrUndefined(args.children) || 0,
        roomCount: numberOrUndefined(args.rooms) || 1
      },
      localeParam: {
        countryCode: args["country-code"] || "CN",
        currency: args.currency || "CNY"
      }
    };
    const hotelId = numberOrUndefined(args["hotel-id"]);
    if (hotelId) {
      delete argumentsPayload.name;
      argumentsPayload.hotelId = hotelId;
    }
    const result = await rpc("tools/call", {
      name: "getHotelDetail",
      arguments: argumentsPayload
    });
    console.log(JSON.stringify(result));
    return;
  }

  console.error(`Usage:
  node scripts/aigohotel-mcp.mjs initialize
  node scripts/aigohotel-mcp.mjs tools-list
  node scripts/aigohotel-mcp.mjs search --place 贾登峪 --place-type 详细地址 --check-in-date 2026-06-13 --nights 1 --adults 2 --query "..."
  node scripts/aigohotel-mcp.mjs detail --name 喀纳斯四季休闲酒店 --check-in-date 2026-06-13 --check-out-date 2026-06-14 --adults 2 --rooms 1`);
  process.exit(command === "help" ? 0 : 1);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
