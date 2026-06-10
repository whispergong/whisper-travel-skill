# Route and Costing

## Route Candidate Model

Represent each candidate route with:

```json
{
  "route_name": "",
  "transport_mode": "",
  "total_days": null,
  "total_distance_km": null,
  "daily_segments": [],
  "key_stops": [],
  "scenic_value": "high|medium|low",
  "driving_pressure": "high|medium|low",
  "lodging_feasibility": "high|medium|low",
  "source_confidence": "high|medium|low",
  "risks": []
}
```

Use this as a thinking model; final reports should be readable markdown, not raw JSON.

## Inferring Days

If the user does not provide available days:

- Self-driving: infer from total distance, safe daily driving time, typical guide routes, and scenic density. Prefer not to exceed about 5-7 hours of driving on sightseeing days, and avoid repeated very long days unless the route is mainly transit.
- Public transit: infer from train/flight/bus frequency, transfer complexity, attraction opening hours, and hotel check-in feasibility.
- Round trips: include return driving pressure and avoid making the return leg invisible.
- Round trips should avoid highly repeating the outbound route when there is a reasonable scenic or pressure-balanced alternative. If the safest or shortest return still repeats large sections, say why and offer at least one alternate split or return corridor.
- State the inferred day count and why it is reasonable.

If the user's requested days are too short, provide a compressed route plus a safer recommended route.

## Daily Split Rules

Each day should have:

- Start and end point.
- Main route and estimated distance/duration.
- A dedicated level-2 or level-3 daily section in the final guide. Do not make one large all-days table carry the detailed daily route; tables are only for overview and cost/lodging summaries.
- A visible `今日动线` / route flow or timeline using arrows, for example `出发地 -> 沿途点 -> 景区 -> 酒店`.
- A daily route map or route visual based on AMap route planning whenever feasible. Prefer API implementation: WebService driving route planning with `waypoints` and returned `polyline`, then AMap static map `paths`/`markers`/`labels` or JS API `AMap.Driving` screenshot. Highlight start, recommended waypoints/rest stops and destination, and make the point names readable with real place names, short place names, or a clear legend. If using static map markers, remember `markers.label` only supports digits, uppercase letters or one Chinese character; put fuller Chinese names in `labels` or the document text. If static map `labels` do not render in the returned PNG, overlay readable place labels locally with verified coordinates before upload. Build the viewport from the full polyline and all labels/markers, add padding, then visually inspect the PNG before upload: endpoints, labels and route lines should not hug the edge, the whole route must be visible, and there should be no unexplained white bars or clipped map UI. In traveler-facing image alt/captions, use natural route descriptions and do not expose `WebService`, `static map`, `含地名标签`, cache or tool details; in MDX attributes avoid raw `->` and use wording like `广州到荆州自驾路线图`. If no real route screenshot/static map can be created, generate a navigation-style annotated visual from AMap-verified route steps/segments and label it as a route illustration. Do not use a simple straight-line coordinate chart as the daily route map unless the user explicitly accepts a low-fidelity fallback, and label that fallback clearly.
- If itinerary edits add, remove, merge, or split days, update the day ledger before writing: day number, heading, start/end, route image, hotel anchor, reservation references, cost formulas and every later DXX cross-reference. Prefer one renumbering pass from a local ordered list, formula-assisted table, mapping table or script, then write stable `D1/D2/...` headings into the final document. Do not rely on visible ordered-list numbering or live formulas in Tencent Docs as the final Day labels. Read back the affected range to catch duplicate/missing day numbers, stale route image alt text and cost formulas with the old day count.
- 1-4 meaningful stops, not an overloaded checklist.
- Recommended along-the-way points with a short reason for inclusion or downgrade to optional.
- Official or credible introductory text links for attractions when available.
- A lodging anchor that is practical for the next day.
- Important reservation, ticket, road-condition and permit links inside the relevant daily section when that attraction or road appears. Keep whole-trip reservation summaries short and focused on hard-to-book or trip-critical items.
- Lodging strategy inside the relevant daily section, with hotel/detail/search links carried by descriptive text rather than raw URLs.
- Driving, parking, weather, meals/fuel/charging/supply and visitor-center notes when relevant.

Score daily splits by:

- Route feasibility and no excessive backtracking.
- Scenic or experiential value along the way.
- Driving pressure or transfer pressure.
- Lodging availability and price reasonableness.
- Weather, altitude, seasonal road, and crowd risks.

## Along-the-Way Points

Do not only plan destination attractions. For each major segment, search and evaluate:

- Viewpoints, scenic roads, old towns, local markets, villages, lakes, passes, canyons, museums.
- Food and rest stops, service areas, gas/charging, parking lots.
- Seasonal closures, construction, snow/ice, altitude, ferry/boat or shuttle constraints.

Use Xiaohongshu + web search + AMap. A point with strong social buzz but weak map feasibility should be marked as optional, not core.

## Costing

Produce a rough cost table. Split facts from estimates.

Cost buckets:

- Hotels: from `hotel-search-cn` nightly recommendations and price ranges.
- Fuel: estimate from total driving km, assumed fuel consumption, and current or stated fuel price. If unknown, use a clearly labeled rough assumption.
- Tolls: use AMap/route result if available; otherwise estimate by highway distance and label low confidence.
- Tickets: official scenic ticket pages or travel sources preferred; Xiaohongshu can provide user-reported prices but needs confidence labels.
- Parking/transfer/shuttle: gather from Xiaohongshu images, comments, official pages, or map POI notes.
- Meals: if the user gives a dining style or budget, use that. Otherwise default to `人数 × 天数 × 75 元/人/天`, explicitly showing the people count and day count in the formula.
- Buffer: 10-15% for route changes, parking, snacks, small paid attractions and price drift.

Confidence labels:

- `high`: official/current platform price or multiple source agreement.
- `medium`: recent guide or consistent platform estimates.
- `low`: inferred from distance, old guide, or missing exact current price.

Never hide uncertainty. If a fee is unknown, include it as a row with `待复核` instead of dropping it.
