# Tencent Smart Document Delivery

After the itinerary is stable, create a Tencent smart document (`smartcanvas`) as the shareable final artifact. Use the `tencent-docs` skill exposed in the current session, or `TENCENT_DOCS_SKILL_HOME` when a local path is needed, and follow its `smartcanvas/entry.md` workflow. The document is for travelers, not for agent debugging.

Use the built-in Tencent Docs travel template as the closest local pattern:

```bash
${TENCENT_DOCS_SKILL_HOME}/smartcanvas/template/quanzhou_3_day_travel_guide.mdx
```

It uses a clear title, itinerary card, route overview, daily sections, columns/callouts, lodging/transport guidance and practical tips. Adapt that structure to the destination instead of producing a dense diagnostic report.

## Visual Research Summary

Use these concrete patterns from local Tencent templates, `find-skills` results (`travel-planner`, `itinerary-optimizer`) and public travel itinerary templates:

- Start with a strong visible title and an itinerary card: who it is for, total days, total distance, daily driving pressure, best season/date caveat and one-line route.
- Put the route map near the top. Good travel docs make the path visible before the reader enters day-by-day detail.
- Use daily sections as the main reading unit. Each day should feel like a mini page, not one row in a giant table.
- Use a route flow or timeline inside every day: `出发地 -> 沿途点 -> 核心景点 -> 酒店`. This gives a quick scan path before prose.
- Daily details for a full travel guide must not be carried by one large table. Tables are for overview, lodging summaries and cost summaries; each day needs its own level-2 or level-3 section.
- Use card-like callouts and columns for scenic spots, food/rest stops, parking/altitude/weather notes and hotel candidates.
- Put hotel booking/detail links directly on hotel names when available. A travel doc that cannot take the user to the hotel page feels unfinished.
- Keep internal diagnostics out. Source health checks and tool failures belong in chat, not the shareable user document.

## Preflight

Run:

```bash
mcporter list tencent-docs
```

Confirm the tool list includes `create_smartcanvas_by_mdx`, `manage.create_file`, `smartcanvas.edit` and `upload_image`. If auth fails, token is missing, or the tool reports `400006`, stop and guide the user to finish Tencent Docs authorization before creating the final document.

## Quota-Aware Editing

Prefer Tencent Docs MCP/skill when it is available, but treat every document read, image upload and edit as quota-bearing:

- Read once, plan locally. Use `get_content` for quick plain-text inspection or paged `smartcanvas.read` when block IDs are needed. Cache the block map locally for the current edit pass.
- Generate the full MDX patch locally before writing. Do not make exploratory one-line edits while still deciding content.
- Batch image work: create or capture all route images first, upload them in one pass, store the returned `image_id` values locally, then insert document content that references those IDs.
- Prefer replacing a whole stable section over many sentence-level edits. When deleting a range is unavoidable, derive all block IDs from the same read pass and delete only the known range between two anchors.
- Preserve the existing outline unless the actual itinerary structure changes. Do not add temporary outline-level sections such as "adjustment notes" or "new version" to a traveler-facing document; move changed attractions, split-day rationale, source confidence and driving-risk notes into the affected daily sections.
- Verify with one readback after the batch. Only run a second patch for concrete failures such as missing D-days, empty hrefs, leftover raw URLs or leaked implementation captions.
- If MCP reports quota/permission failures after the user has authenticated, pause MCP writes and use the browser fallback path rather than retrying repeatedly.
- `smartcanvas.read` can repeat page frontmatter at the start of each paged response. Strip that per-page metadata before checking for leaked `cover:` or `title:` residue; otherwise the verifier may mistake readback framing for document content and waste quota on no-op updates.

## Browser Visual Verification

MCP readback proves structure, not visual quality. Before final delivery, open the Tencent document in a real browser and inspect the rendered page.

- Browser priority follows the general travel browser rule for all non-Xiaohongshu browser work: agent in-app Browser first, then browser-plugin-controlled Chrome/Edge or the current system browser, then standalone Playwright or a persistent Playwright profile, with Computer Use only as the last visible-UI fallback. Reuse an already logged-in/open Tencent Docs tab whenever available. If the in-app Browser has a transient setup, tab, navigation or screenshot issue, retry the lightweight browser connection or tab operation before falling back.
- Check the first viewport: cover/route overview image, visible title, conclusion paragraph and route card should be readable without awkward cropping.
- Check route and itinerary sections: wide tables must not crowd or clip text. If a table is visually narrow, convert it to bullets or short card-like blocks unless it is a compact cost/lodging summary.
- Check every daily section after itinerary changes: each day should have a matching route image or explicit route illustration, and the visible image caption/alt text must use the same Day number and route as the section heading.
- Check links and captions in the browser view: links should appear as descriptive text rather than raw long URLs; image captions should be traveler-facing and must not mention internal tooling.
- If visual verification finds issues, make one local fix plan, batch the smallest MCP edits that address the concrete problems, then re-check only the affected browser sections.

## Document Structure

The smart document should be visually polished and useful when opened later. Include:

- A document title in two places: Tencent file title and visible body title. When using fallback creation, start the inserted content with a visible `<Heading level="1">` or `#` title because frontmatter is not used by `smartcanvas.edit`.
- A short travel card: duration, route, total distance, driving pressure, best season or date caveat, suitable travelers.
- Route visual: prefer a real route image generated from AMap API-verified route planning. API priority is: WebService route planning with `waypoints` + `show_fields=polyline` -> AMap static map `paths`/`markers`/`labels`; if a richer map UI is needed, use JS API `AMap.Driving` and browser screenshot. Highlight start, recommended waypoints/rest stops and destination with readable real place names or short place-name labels, not only `A/1/Z`. If AMap static `labels` do not render reliably, post-process the PNG locally with verified coordinates and draw readable place labels before upload. Before upload, inspect the generated PNG at its final aspect ratio: the route must be complete, labels readable, start/end not pressed against the edge, and there should be no unexplained white header strip or clipped UI. If any of those checks fail, regenerate with a wider bbox/zoom-out and more padding rather than accepting the image. Traveler-facing captions and image alt text must use natural descriptions such as `Day 7 大柴旦到茫崖自驾路线图`; keep implementation details like `WebService`, `static map`, `含地名标签`, cache status, or tool names out of the final document. In JSX/MDX image attributes, avoid raw arrows like `->`; use natural wording such as `广州到荆州自驾路线图`. If no real map image can be created, use a clean navigation-style route diagram with a natural `路线示意图` label and keep the route table. Do not use simple straight coordinate lines as daily route maps unless clearly marked as a low-fidelity fallback.
- Existing-route consistency: when updating an existing smart document, inspect the earliest completed route maps and captions first. If D1/D2 or the overview already use real AMap route/map screenshots, every newly adjusted daily map should match that fidelity and should not be replaced with a schematic route diagram. Use a fallback diagram only after the AMap API/URI/browser route page is unavailable, and keep the fallback reason in chat or work notes rather than in the final user-facing document.
- Route overview: one compact table or bullets for the whole route, but do not cram all daily details into one wide table.
- Daily plan: make each day a level-2 section (`## Day N ...`) or MDX `<Heading level="2">`; use level-3 subsections when the day has multiple scenic clusters. Inside each day include start/end, distance/time, a visible `今日动线`/route flow, recommended route stops, attraction official/introductory text links, practical driving notes, parking/weather/supply reminders, important reservation/road-condition checks, and that night's concrete hotel recommendations.
- Day numbering: when an existing long itinerary changes length, create or update a local ordered day ledger before editing Tencent Docs. Use it to regenerate DXX headings, route image alt/captions, overview day counts, hotel anchors, appointment references, map links and cost formulas in one pass. Do not make ad hoc partial renumbering edits in the live document.
- Daily route map: generate or capture one route map per day when feasible. For long routes with many days, prioritize every high-complexity driving day and still include a flow/timeline for the rest. Do not leave daily detail as prose only.
- Attraction links: add official/introductory links for specific attractions when available.
- Large ticketed scenic spots: add Xiaohongshu guide links or note IDs for practical touring strategy.
- Links: use descriptive text as the hyperlink label for Xiaohongshu searches, official ticket pages, hotel searches and map POIs. In Tencent smartcanvas insertion, prefer standard Markdown links like `[莫高窟预约入口](https://...)` and read back to verify hrefs are preserved. If readback shows empty hrefs such as `[]()` or turns links into visible long URLs, switch that section to single-line MDX links (`<Link href="https://...">莫高窟预约入口</Link>`) and verify again. If both Markdown and `<Link>` still serialize as label-only text but the final browser view does not expose long URLs, stop retrying through MCP, keep the descriptive labels/keywords, and call out that clickable hrefs need browser-side or manual Tencent Docs confirmation. Do not expose long raw URLs in the final smart document unless the user explicitly asks for plain URLs.
- Reservation and lodging placement: put attraction/ticket/reservation links and lodging strategy inside the relevant daily section first. Keep only a short final `重点预约/证件/路况` checklist for items that affect the whole trip, not a long link index.
- Hotels: every overnight stop should have 1-3 concrete hotel candidates, not only a lodging area. Prefer `hotel-search-cn` recommendations; if dates are missing, still provide representative candidates with a clear "date-specific price needs recheck" note. Include hotel name, area, why it fits, parking/transport relevance, price confidence and booking/detail links. Link priority: Ctrip detail page, Tongcheng detail page, FlyAI/Fliggy detail page, then platform search result page. Never invent a detail URL.
- Cost table: hotel, fuel, toll, tickets, parking/shuttle, meals and buffer.
- Pending checks: weather, closures, reservations, hotel prices, vehicle restrictions.

Do not include in the final smart document:

- Source health checks, environment status, API keys, MCP/tool failures, retry logs or "this test command hung" notes.
- Raw source dumps, bare long URLs, long copied comments, internal scoring tables or agent handoff content.
- A giant all-days table as the itinerary carrier. Tables are useful for overview, lodging and cost summaries, but daily details need their own readable sections.

## Route Map Rules

Create route images from map facts rather than decorative guesswork:

1. Resolve every route endpoint and important lodging/scenic anchor with `maps_geo` or an already verified coordinate.
2. Run `maps_direction_driving` or the matching transport route tool for the total route and each daily segment. When an AMap WebService/JS API key is available, prefer API route planning with waypoints and returned `polyline`; capture distance, duration, route steps, major road names, instructions and waypoint order.
3. Prefer a real AMap route visual:
   - First use WebService route polyline + static map `paths`, `markers` and `labels` for a deterministic API-generated route image. Use `markers` for visible pins and `labels`/legend for readable place names; `markers.label` itself is limited to digits, uppercase letters or one Chinese character. If `labels` are missing in the returned static image, overlay the real place names locally with a raster post-processing step such as Pillow or Sharp, using the same verified coordinates and viewport.
   - If the static map is insufficient, use AMap JS API `AMap.Driving` in a browser and capture the rendered route.
   - If API routes fail or key/permissions are unavailable, use the browser fallback order: agent in-app Browser -> browser-plugin-controlled Chrome/Edge or the current system browser -> Playwright -> Computer Use fallback.
   - Save the screenshot locally before uploading it to Tencent Docs.
4. If real AMap tiles or a route screenshot are unavailable, generate an annotated navigation-style route image from AMap route planning data: route steps/major roads first, segment driving distances/durations second, and verified coordinates as anchors only. Label it in natural traveler-facing language as a route illustration, and do not present it as a live navigation screenshot.
5. For daily route maps, repeat the same process per day. If a daily map cannot be created, include an explicit route flow and a compact segment table for that day.

Do not use a generic line drawing that has no AMap-verified coordinates, route segment data or source label. Do not let a straight-line coordinate chart stand in for a planned driving route when AMap API/MCP route planning is available.

For existing documents, route-image replacements are quality-sensitive. Match the existing real-map route style before uploading replacement images; a new route image should not visibly downgrade from earlier days such as D1/D2. If a user points out that new maps look schematic, treat it as a document-quality bug and regenerate the affected images from AMap route pages, static maps or JS-rendered route screenshots before editing more prose.

## Image Rules

Tencent smartcanvas does not accept raw external image URLs in the final MDX:

1. Save or generate the route image locally.
2. Upload it with `upload_image`.
3. Use the returned `image_id` in `cover` or `<Image src="image_id" alt="..." />`.

If image upload fails, omit the image and keep a textual route table. Do not put `http://` or `https://` image URLs directly into MDX.

For non-map generated images, such as a cover image, destination mood image, food image or scenic illustration, prefer `GPT-IMAGE2` explicitly. These images are secondary to route maps and factual source images; do not let decorative images replace map evidence or Xiaohongshu/source screenshots.

## Daily Section Pattern

Use this as the minimum pattern for every day:

```mdx
## Day 3: 大理 -> 丽江

<Callout blockColor="light_blue" borderColor="blue">
    <Heading level="3">今日动线</Heading>
    <Paragraph>大理古城 -> 洱海观景点 -> 沙溪/补给 -> 丽江古城酒店</Paragraph>
</Callout>

<Image src="uploaded_route_image_id" alt="Day 3 大理到丽江自驾路线图" width="800" />

<ColumnList>
    <Column width="58%">
        <Heading level="3">沿途亮点</Heading>
        <BulletedList>
            <Mark bold>洱海西岸</Mark>: 适合上午短停拍照，避开环海东路拥堵；附官方或可信介绍链接。
            <Mark bold>沙溪古镇</Mark>: 可作为午餐和休息点，若当天驾驶压力高则改为备选；附官方或可信介绍链接。
        </BulletedList>
        <Heading level="3">驾驶/停车/天气/补给提醒</Heading>
        <BulletedList>
            高德 MCP 核验距离/时长、主要道路、停车场或补给点；天气和季节风险需标出待复核项。
        </BulletedList>
    </Column>
    <Column width="42%">
        <Callout blockColor="light_yellow" borderColor="yellow">
            <Heading level="4">今晚住宿</Heading>
            <BulletedList>
                [酒店名](携程或同程详情页): 价格/区域/停车/为什么适合今天。
                [备选酒店](同程或携程详情页): 价格信心和注意项。
            </BulletedList>
        </Callout>
    </Column>
</ColumnList>
```

Keep the actual wording destination-specific. The important shape is: route flow first, route image or map card second, then scenic cards, driving/parking/weather/supply notes, important reservation checks and hotel cards. Use arrows (`->`) or a compact timeline so the day is visually scannable. If the image is not a real AMap page screenshot, static map, tile screenshot, or JS API-rendered screenshot, its visible label or alt text should plainly say it is a route illustration without exposing implementation details.

## Creation Fallback

Prefer:

```bash
mcporter call tencent-docs create_smartcanvas_by_mdx --args '{"title":"...", "mdx":"...", "content_format":"mdx"}'
```

If the tool list shows `create_smartcanvas_by_mdx` but calling it fails with an RPC not registered / outdated pb error, use the stable two-step fallback:

1. Create an empty smartcanvas:
   ```bash
   mcporter call tencent-docs manage.create_file --args '{"file_type":"smartcanvas","title":"..."}'
   ```
2. Append the final MDX content:
   ```bash
   mcporter call tencent-docs smartcanvas.edit --args '{"file_id":"...","action":"INSERT_AFTER","id":"","content":"..."}'
   ```

When using this fallback, remove frontmatter from the inserted content and put a visible title block at the top, for example:

```mdx
<Heading level="1">
    广州到香格里拉自驾往返攻略
</Heading>
```

For verification, if `smartcanvas.read` fails with the same RPC error, use:

```bash
mcporter call tencent-docs get_content --args '{"file_id":"..."}'
```

## MDX Rules

- Use normal Markdown first. Use MDX components only when needed and only after checking `smartcanvas/mdx_references.md`.
- Keep tables readable; avoid dumping raw source output.
- Keep copied text from third-party sources brief. Prefer summaries, links, note IDs and confidence labels.
- The final chat response should include the Tencent Docs title, URL and `file_id`.
