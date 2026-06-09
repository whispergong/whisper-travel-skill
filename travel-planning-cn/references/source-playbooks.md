# Source Playbooks

Use the same user intent across sources: departure, destination, transport mode, date range, available days, people, budget, interests, lodging preferences, and hard exclusions.

## Xiaohongshu

小红书是 v1 的高权重攻略来源，尤其适合路线、沿途点、避坑、图片路线图、停车、真实体验和季节性信息。

Use only the local third-party Xiaohongshu project. Do not edit or patch that repository from this skill. The CLI controls a real browser through the XHS Bridge extension in Edge or Chrome; it is not a direct API scraper.

```bash
# Resolve the installed third-party project first.
# Unix/macOS:
cd "$XIAOHONGSHU_SKILLS_HOME"
./.venv/bin/python scripts/cli.py check-login
./.venv/bin/python scripts/cli.py search-feeds --keyword "<关键词>" --sort-by 综合 --note-type 图文
./.venv/bin/python scripts/cli.py get-feed-detail --feed-id <ID> --xsec-token <TOKEN> --keyword "<关键词>"

# Windows PowerShell equivalent:
# Set-Location $env:XIAOHONGSHU_SKILLS_HOME
# .\.venv\Scripts\python.exe scripts\cli.py check-login
```

Rules:

- All Xiaohongshu search/browse operations must go through the local `scripts/cli.py` browser-control entrypoint; do not use other Xiaohongshu MCPs, Go tools, direct HTTP scraping, or remembered external implementations.
- Locate the project first: prefer `XIAOHONGSHU_SKILLS_HOME`, then the `xiaohongshu-skills` path exposed in the current skill list, then `%USERPROFILE%\.codex\skills\xiaohongshu-skills` or `%USERPROFILE%\.agents\skills\xiaohongshu-skills` on Windows, then `$HOME/.codex/skills/xiaohongshu-skills` or `$HOME/.agents/skills/xiaohongshu-skills` on Unix-like setups. If none exist, ask the user for the installed project path.
- Use the project runner that works in that project directory: prefer `.\.venv\Scripts\python.exe scripts\cli.py` on Windows or `./.venv/bin/python scripts/cli.py` on Unix, then `uv run python scripts/cli.py`, then system `python`/`python3 scripts/cli.py`. The command target remains `scripts/cli.py` in that project in every case. Do not run a relative `scripts/cli.py` from the travel skill repository or another cwd.
- Treat the XHS Bridge connected browser session as the source of truth. If `ws://localhost:9333` reports an extension connection, use that connected Edge/Chrome session. If it is not connected, reuse whichever browser the user installed XHS Bridge in; when both Edge and Chrome are known candidates, prefer the installed and logged-in one, with Edge preferred only when both are equivalent. If login, captcha, QR scan, or risk-control prompts appear, stop and let the user complete them in the same browser before continuing.
- Search multiple query classes: full route, one-way route, return route, destination guide, along-the-way stops, road condition, parking, food, lodging areas, seasonal warnings.
- For each core query, start with 3-5 promising notes by title, cover, likes/collects/comments, and relevance.
- Fetch details in groups of at most 3 notes, then wait 10-20 seconds before the next group to reduce risk control. Prefer fewer high-signal notes over broad scraping.
- Record `noteId`, title, author, interaction counts, body/desc, tags, comments, image URLs, and why the note is relevant.
- Only one agent should control Xiaohongshu browser search/detail at a time.

## Reading Images

Images are evidence. Read them whenever they may contain route maps, road signs, scenic maps, menus, parking fees, ticket prices, road conditions, campsite/hotel screenshots, or daily itinerary screenshots.

Process:

1. Extract image URLs from `get-feed-detail` output: `imageList[].urlDefault`.
2. Download selected images to a local temporary run folder such as `travel-planning-cn-workspace/assets/<run-id>/`.
3. Use the current vision-capable agent, `view_image`, or `codex-vision-delegation` to inspect local image files.
4. Summarize visual facts as structured evidence: `source`, `image_index`, `observed_text`, `map_points`, `prices`, `warnings`, `confidence`.
5. Keep source URLs and note IDs; do not claim image facts without a source pointer.

If direct image download fails because the CDN requires headers or login, open the visible note page and capture a screenshot; then inspect the screenshot instead.

## Web and Local-Language Search

Use ordinary web search to corroborate and broaden Xiaohongshu findings.

- China: use Chinese queries such as `广州 自驾 香格里拉 路线`, `广州 香格里拉 自驾 沿途`, `香格里拉 自驾 停车 避坑`.
- Japan: use Japanese queries first, then English fallback.
- Other overseas destinations: use the local language when obvious; otherwise use English plus destination names.
- Prefer official tourism sites, map pages, ticket pages, road/transport notices, and recent high-quality guides.
- For image-heavy web pages, inspect key images or screenshots using the same image-reading process.
- Weighting: Xiaohongshu has high practical-experience weight, but official notices win for closures, tickets, traffic restrictions, and safety.

## AMap MCP / WebService / JS API

Use 高德 for China route verification, route visuals and POI grounding:

- `maps_geo`: resolve departure, destination, daily endpoints, scenic areas, visitor centers, parking lots, stations, ferry/transfer points.
- `maps_direction_driving`: self-driving routes, distance, duration, toll hints when available.
- `maps_direction_walking`: walking feasibility around scenic gates, hotels, parking, visitor centers.
- `maps_direction_transit_integrated`: city-to-city or urban public transit when appropriate.
- `maps_distance`: compare candidate detours or hotel-to-anchor distances.
- `maps_around_search`: find scenic spots, hotels, food, gas stations, parking, visitor centers, viewpoints and service clusters.

When the user provides a 高德开放平台 key or the environment has one, prefer API implementation for route-image work:

- WebService route planning first: use driving route planning with `waypoints` and `show_fields=polyline` when available. Capture distance, duration, steps/roads and the returned polyline.
- Static map second: use 高德静态地图 `paths` to draw the returned route polyline, `markers` to highlight start/recommended waypoints/rest stops/destination, and `labels` to show real place names or short place-name labels. Do not leave the final traveler-facing image with only `A/1/Z`; 高德 `markers.label` is limited to digits, uppercase letters or a single Chinese character, so use single-character marker labels plus `labels`/legend for readable names. If the returned image does not actually show the `labels`, post-process the PNG locally with verified coordinates and draw readable place-name labels before upload.
- Route-image bounds: calculate the map viewport from the full route polyline plus all marker/label coordinates, then add generous padding before rendering. As a practical check, start/end markers, labels and the route line should not sit within roughly 40-60 px of any image edge, and no route segment should be cropped. If the image has a blank white strip, clipped top controls, cut-off labels, or an endpoint pressed against the edge, regenerate with a wider bbox/zoom-out or crop only after preserving full route context.
- JS API screenshot third: if a browser-rendered map is needed, use `AMap.Driving` with the verified points and capture the rendered route.
- Generic web workflow only after API paths fail or permissions are missing: agent in-app Browser -> browser-plugin-controlled Edge/Chrome or current system browser -> standalone Playwright/persistent profile -> Computer Use as the last UI fallback.
- Never commit API keys. Pass keys through runtime environment variables such as `AMAP_KEY` and keep them out of the final Tencent document.
- Keep implementation terms out of traveler-facing captions, image alt text and paragraph copy. The final document may show “D7 大柴旦到茫崖自驾路线图” or “路线示意图”, but should not expose `WebService`, `静态地图`, `含地名标签`, cache status, retry notes or tool names.

Avoid blasting AMap requests in parallel. If the MCP returns `CUQPS_HAS_EXCEEDED_THE_LIMIT`, pause, retry serially, and record the retry in source health instead of treating the map source as fully failed.

For overseas routes, do not pretend 高德 is authoritative. Use it only when it returns reliable coverage and clearly state limitations.

### AMap Route Visuals

AMap MCP route facts should feed the document map assets:

- For the overview route, resolve all overnight anchors and major scenic anchors, then call the relevant route tool segment by segment. Keep a `route_assets` note with coordinates, segment distance/time, major roads and map image status.
- For each day, call the relevant route tool for that day's start/end and planned stops. Generate a daily route map when feasible.
- Preferred visual source: a real AMap route/map screenshot or static map generated from WebService/JS API route polyline, verified coordinates and waypoints.
- Acceptable fallback: an annotated map or route diagram generated from AMap-verified route steps, coordinates and segment metrics, labeled in natural reader-facing language as a route illustration.
- Not acceptable: a decorative route line with no AMap-verified points or a map image that contradicts the route data.
- When using generated images for non-map decoration, explicitly prefer `GPT-IMAGE2`; do not use it to replace required route verification.

## Final Link Presentation

- Xiaohongshu search pages, official ticket pages, AMap POIs, hotel search pages and booking/detail pages must be embedded as descriptive text links in final Tencent documents. Prefer standard Markdown links (`[说明文字](URL)`) for Tencent smartcanvas edits and verify readback keeps the href; avoid custom `<Link>` components when they drop URLs. Avoid visible long URLs because they crowd the guide and look unfinished.
- Put scenic/ticket/reservation links and lodging links inside the relevant daily section when the attraction or overnight stop appears. Only keep a compact whole-trip checklist for hard-to-book or trip-critical items such as 莫高窟, 边境管理区通行证, 独库公路, 那拉提, 赛里木湖 and 喀纳斯.
- If a source only gives a long URL and no title, create a truthful label from the destination and task, such as `莫高窟预约入口`, `水上雅丹位置复核`, or `喀纳斯住宿复核`.

## Travel Skills and Search Tools

Use auxiliary travel sources to cross-check route feasibility, POIs, tickets, packages and transport:

- FlyAI: `keyword_search`, `ai_search`, `search_hotels`, and CLI travel/POI search when available.
- 同程程心: `travel-query.js`, `traffic-query.js`, `scenery-query.js`, `hotel-query.js` depending on the need.
- 携程问道: natural-language travel planning, scenic recommendations, hotels, flights/trains.
- `hotel-search-cn`: only after the broad route and daily lodging anchors are stable.

Keep raw source snippets brief, and always separate third-party claims from verified route facts.
