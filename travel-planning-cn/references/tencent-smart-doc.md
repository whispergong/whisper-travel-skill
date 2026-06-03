# Tencent Smart Document Delivery

After the itinerary is stable, create a Tencent smart document (`smartcanvas`) as the shareable final artifact. Use `/Users/whisper/Desktop/workplace/tencent-docs/SKILL.md` and the `smartcanvas/entry.md` workflow. The document is for travelers, not for agent debugging.

Use the built-in Tencent Docs travel template as the closest local pattern:

```bash
/Users/whisper/Desktop/workplace/tencent-docs/smartcanvas/template/quanzhou_3_day_travel_guide.mdx
```

It uses a clear title, itinerary card, route overview, daily sections, columns/callouts, lodging/transport guidance and practical tips. Adapt that structure to the destination instead of producing a dense diagnostic report.

## Visual Research Summary

Use these concrete patterns from local Tencent templates, `find-skills` results (`travel-planner`, `itinerary-optimizer`) and public travel itinerary templates:

- Start with a strong visible title and an itinerary card: who it is for, total days, total distance, daily driving pressure, best season/date caveat and one-line route.
- Put the route map near the top. Good travel docs make the path visible before the reader enters day-by-day detail.
- Use daily sections as the main reading unit. Each day should feel like a mini page, not one row in a giant table.
- Use a route flow or timeline inside every day: `出发地 -> 沿途点 -> 核心景点 -> 酒店`. This gives a quick scan path before prose.
- Use card-like callouts and columns for scenic spots, food/rest stops, parking/altitude/weather notes and hotel candidates.
- Put hotel booking/detail links directly on hotel names when available. A travel doc that cannot take the user to the hotel page feels unfinished.
- Keep internal diagnostics out. Source health checks and tool failures belong in chat, not the shareable user document.

## Preflight

Run:

```bash
mcporter list tencent-docs
```

Confirm the tool list includes `create_smartcanvas_by_mdx`, `manage.create_file`, `smartcanvas.edit` and `upload_image`. If auth fails, token is missing, or the tool reports `400006`, stop and guide the user to finish Tencent Docs authorization before creating the final document.

## Document Structure

The smart document should be visually polished and useful when opened later. Include:

- A document title in two places: Tencent file title and visible body title. When using fallback creation, start the inserted content with a visible `<Heading level="1">` or `#` title because frontmatter is not used by `smartcanvas.edit`.
- A short travel card: duration, route, total distance, driving pressure, best season or date caveat, suitable travelers.
- Route visual: prefer a real route image generated from AMap MCP-verified coordinates/segments, such as a captured AMap route page, AMap static/map screenshot, or an annotated image based on AMap route data. If no real map image can be created, use a clean route diagram labeled `高德核验路线示意图` and keep the route table.
- Route overview: one compact table or bullets for the whole route, but do not cram all daily details into one wide table.
- Daily plan: make each day a level-2 section (`## Day N ...`) or MDX `<Heading level="2">`. Inside each day include start/end, distance/time, a visible route flow, route stops, practical driving notes, parking/altitude/weather reminders, and that night's concrete hotel recommendations.
- Daily route map: generate or capture one route map per day when feasible. For long routes with many days, prioritize every high-complexity driving day and still include a flow/timeline for the rest. Do not leave daily detail as prose only.
- Attraction links: add official/introductory links for specific attractions when available.
- Large ticketed scenic spots: add Xiaohongshu guide links or note IDs for practical touring strategy.
- Hotels: every overnight stop should have 1-3 concrete hotel candidates, not only a lodging area. Prefer `hotel-search-cn` recommendations; if dates are missing, still provide representative candidates with a clear "date-specific price needs recheck" note. Include hotel name, area, why it fits, parking/transport relevance, price confidence and booking/detail links. Link priority: Ctrip detail page, Tongcheng detail page, FlyAI/Fliggy detail page, then platform search result page. Never invent a detail URL.
- Cost table: hotel, fuel, toll, tickets, parking/shuttle, meals and buffer.
- Pending checks: weather, closures, reservations, hotel prices, vehicle restrictions.

Do not include in the final smart document:

- Source health checks, environment status, API keys, MCP/tool failures, retry logs or "this test command hung" notes.
- Raw source dumps, long copied comments, internal scoring tables or agent handoff content.
- A giant all-days table as the only itinerary. Tables are useful for overview, but daily details need their own readable sections.

## Route Map Rules

Create route images from map facts rather than decorative guesswork:

1. Resolve every route endpoint and important lodging/scenic anchor with `maps_geo` or an already verified coordinate.
2. Run `maps_direction_driving` or the matching transport route tool for the total route and each daily segment. Capture distance, duration, major road names and instructions.
3. Prefer a real AMap route visual:
   - Open/capture an AMap route page or map page using the verified origin, destination and waypoints when browser tools are available.
   - Or use an AMap static/map screenshot path if available in the environment.
   - Save the screenshot locally before uploading it to Tencent Docs.
4. If real AMap tiles or a route screenshot are unavailable, generate an annotated route image from AMap-verified coordinates and segment distances. Label it as `高德核验路线示意图`, not as a live navigation screenshot.
5. For daily route maps, repeat the same process per day. If a daily map cannot be created, include an explicit route flow and a compact segment table for that day.

Do not use a generic line drawing that has no AMap-verified coordinates, route segment data or source label.

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

<Image src="uploaded_route_image_id" alt="Day 3 高德核验路线图" width="800" />

<ColumnList>
    <Column width="58%">
        <Heading level="3">沿途亮点</Heading>
        <BulletedList>
            <Mark bold>洱海西岸</Mark>: 适合上午短停拍照，避开环海东路拥堵。
            <Mark bold>沙溪古镇</Mark>: 可作为午餐和休息点，若当天驾驶压力高则改为备选。
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

Keep the actual wording destination-specific. The important shape is: route flow first, route image or map card second, then scenic cards and hotel cards. Use arrows (`->`) or a compact timeline so the day is visually scannable.

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
