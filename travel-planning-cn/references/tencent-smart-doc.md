# Tencent Smart Document Delivery

After the itinerary is stable, create a Tencent smart document (`smartcanvas`) as the shareable final artifact. Use `/Users/whisper/Desktop/workplace/tencent-docs/SKILL.md` and the `smartcanvas/entry.md` workflow.

## Preflight

Run:

```bash
mcporter list tencent-docs
```

Confirm the tool list includes `create_smartcanvas_by_mdx`, `manage.create_file`, `smartcanvas.edit` and `upload_image`. If auth fails, token is missing, or the tool reports `400006`, stop and guide the user to finish Tencent Docs authorization before creating the final document.

## Document Structure

The smart document should be visually polished and useful when opened later. Include:

- A short frontmatter block with `title` and one `icon`.
- A concise conclusion section: recommended days, route, driving pressure, best-fit traveler, biggest risks.
- Route visual: prefer an image generated from AMap-verified points, a captured map screenshot, or a clean route diagram. If no image can be created, include a route table and explain the limitation.
- Daily plan: a table with day, start/end, distance/time, stops, lodging anchor and reminders.
- Day detail sections: each day has practical notes for driving, parking, scenic stops, meals/fuel and weather/altitude risks.
- Attraction links: add official/introductory links for specific attractions when available.
- Large ticketed scenic spots: add Xiaohongshu guide links or note IDs for practical touring strategy.
- Hotels: summarize `hotel-search-cn` recommendations or lodging anchors, with price confidence.
- Cost table: hotel, fuel, toll, tickets, parking/shuttle, meals and buffer.
- Pending checks: weather, closures, reservations, hotel prices, vehicle restrictions.

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

For verification, if `smartcanvas.read` fails with the same RPC error, use:

```bash
mcporter call tencent-docs get_content --args '{"file_id":"..."}'
```

## MDX Rules

- Use normal Markdown first. Use MDX components only when needed and only after checking `smartcanvas/mdx_references.md`.
- Keep tables readable; avoid dumping raw source output.
- Keep copied text from third-party sources brief. Prefer summaries, links, note IDs and confidence labels.
- The final chat response should include the Tencent Docs title, URL and `file_id`.
