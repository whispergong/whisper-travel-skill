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
- State the inferred day count and why it is reasonable.

If the user's requested days are too short, provide a compressed route plus a safer recommended route.

## Daily Split Rules

Each day should have:

- Start and end point.
- Main route and estimated distance/duration.
- A visible route flow or timeline using arrows, for example `出发地 -> 沿途点 -> 景区 -> 酒店`.
- A daily route map or route visual when feasible; when not feasible, keep the arrow flow and a compact segment table.
- 1-4 meaningful stops, not an overloaded checklist.
- A lodging anchor that is practical for the next day.
- Meals/fuel/charging/parking/visitor-center notes when relevant.

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
- Meals: daily rough estimate per person unless the user gives style/budget.
- Buffer: 10-15% for route changes, parking, snacks, small paid attractions and price drift.

Confidence labels:

- `high`: official/current platform price or multiple source agreement.
- `medium`: recent guide or consistent platform estimates.
- `low`: inferred from distance, old guide, or missing exact current price.

Never hide uncertainty. If a fee is unknown, include it as a row with `待复核` instead of dropping it.
