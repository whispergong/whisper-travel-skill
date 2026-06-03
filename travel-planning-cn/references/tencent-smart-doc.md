# Tencent Smart Document Delivery

After the itinerary is stable, create a Tencent smart document (`smartcanvas`) as the shareable final artifact. Use `/Users/whisper/Desktop/workplace/tencent-docs/SKILL.md` and the `smartcanvas/entry.md` workflow. The document is for travelers, not for agent debugging.

Use the built-in Tencent Docs travel template as the closest local pattern:

```bash
/Users/whisper/Desktop/workplace/tencent-docs/smartcanvas/template/quanzhou_3_day_travel_guide.mdx
```

It uses a clear title, itinerary card, route overview, daily sections, columns/callouts, lodging/transport guidance and practical tips. Adapt that structure to the destination instead of producing a dense diagnostic report.

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
- Route visual: prefer an image generated from AMap-verified points, a captured map screenshot, or a clean route diagram. If no image can be created, include a route table and explain the limitation.
- Route overview: one compact table or bullets for the whole route, but do not cram all daily details into one wide table.
- Daily plan: make each day a level-2 section (`## Day N ...`) or MDX `<Heading level="2">`. Inside each day include start/end, distance/time, route stops, practical driving notes, parking/altitude/weather reminders, and that night's concrete hotel recommendations.
- Attraction links: add official/introductory links for specific attractions when available.
- Large ticketed scenic spots: add Xiaohongshu guide links or note IDs for practical touring strategy.
- Hotels: every overnight stop should have 1-3 concrete hotel candidates, not only a lodging area. Prefer `hotel-search-cn` recommendations; if dates are missing, still provide representative candidates with a clear "date-specific price needs recheck" note. Include hotel name, area, why it fits, parking/transport relevance and price confidence.
- Cost table: hotel, fuel, toll, tickets, parking/shuttle, meals and buffer.
- Pending checks: weather, closures, reservations, hotel prices, vehicle restrictions.

Do not include in the final smart document:

- Source health checks, environment status, API keys, MCP/tool failures, retry logs or "this test command hung" notes.
- Raw source dumps, long copied comments, internal scoring tables or agent handoff content.
- A giant all-days table as the only itinerary. Tables are useful for overview, but daily details need their own readable sections.

## Image Rules

Tencent smartcanvas does not accept raw external image URLs in the final MDX:

1. Save or generate the route image locally.
2. Upload it with `upload_image`.
3. Use the returned `image_id` in `cover` or `<Image src="image_id" alt="..." />`.

If image upload fails, omit the image and keep a textual route table. Do not put `http://` or `https://` image URLs directly into MDX.

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
