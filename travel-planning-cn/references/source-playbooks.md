# Source Playbooks

Use the same user intent across sources: departure, destination, transport mode, date range, available days, people, budget, interests, lodging preferences, and hard exclusions.

## Xiaohongshu

小红书是 v1 的高权重攻略来源，尤其适合路线、沿途点、避坑、图片路线图、停车、真实体验和季节性信息。

Use only the local Xiaohongshu project. The CLI controls a real browser through Chrome/extension/Bridge; it is not a direct API scraper:

```bash
cd /Users/whisper/Desktop/workplace/xiaohongshu-skills
./.venv/bin/python scripts/cli.py check-login
./.venv/bin/python scripts/cli.py search-feeds --keyword "<关键词>" --sort-by 综合 --note-type 图文
./.venv/bin/python scripts/cli.py get-feed-detail --feed-id <ID> --xsec-token <TOKEN> --keyword "<关键词>"
```

Rules:

- All Xiaohongshu search/browse operations must go through the local `scripts/cli.py` browser-control entrypoint; do not use other Xiaohongshu MCPs, Go tools, direct HTTP scraping, or remembered external implementations.
- Use the project runner that works in the environment from `/Users/whisper/Desktop/workplace/xiaohongshu-skills`: prefer `./.venv/bin/python scripts/cli.py`, then `uv run python scripts/cli.py`, then `python3 scripts/cli.py`. The command target remains `scripts/cli.py` in that project in every case. Do not run a relative `scripts/cli.py` from the travel skill repository or another cwd.
- Treat the visible browser session as the source of truth. If login, captcha, QR scan, or risk-control prompts appear, stop and let the user complete them in the browser before continuing.
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

## AMap MCP

Use 高德 for China route verification and POI grounding:

- `maps_geo`: resolve departure, destination, daily endpoints, scenic areas, visitor centers, parking lots, stations, ferry/transfer points.
- `maps_direction_driving`: self-driving routes, distance, duration, toll hints when available.
- `maps_direction_walking`: walking feasibility around scenic gates, hotels, parking, visitor centers.
- `maps_direction_transit_integrated`: city-to-city or urban public transit when appropriate.
- `maps_distance`: compare candidate detours or hotel-to-anchor distances.
- `maps_around_search`: find scenic spots, hotels, food, gas stations, parking, visitor centers, viewpoints and service clusters.

Avoid blasting AMap requests in parallel. If the MCP returns `CUQPS_HAS_EXCEEDED_THE_LIMIT`, pause, retry serially, and record the retry in source health instead of treating the map source as fully failed.

For overseas routes, do not pretend 高德 is authoritative. Use it only when it returns reliable coverage and clearly state limitations.

## Travel Skills and Search Tools

Use auxiliary travel sources to cross-check route feasibility, POIs, tickets, packages and transport:

- FlyAI: `keyword_search`, `ai_search`, `search_hotels`, and CLI travel/POI search when available.
- 同程程心: `travel-query.js`, `traffic-query.js`, `scenery-query.js`, `hotel-query.js` depending on the need.
- 携程问道: natural-language travel planning, scenic recommendations, hotels, flights/trains.
- `hotel-search-cn`: only after the broad route and daily lodging anchors are stable.

Keep raw source snippets brief, and always separate third-party claims from verified route facts.
