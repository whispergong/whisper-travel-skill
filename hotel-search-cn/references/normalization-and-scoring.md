# Normalization and Scoring

This reference defines how to merge hotel results from maps, skills, MCPs, and browser-visible pages.

## Canonical Hotel Fields

Use this shape when normalizing each hotel candidate:

```json
{
  "hotel_name": "",
  "normalized_name": "",
  "source": "",
  "platform": "",
  "platform_hotel_id": "",
  "price_cny": null,
  "price_text": "",
  "room_type": "",
  "availability": "",
  "rating": null,
  "rating_text": "",
  "review_count": null,
  "sales_count": null,
  "address": "",
  "latitude": null,
  "longitude": null,
  "distance_to_target_m": null,
  "distance_to_anchor_m": null,
  "nearest_anchor": "",
  "facilities": [],
  "breakfast": "",
  "cancellation": "",
  "parking": "",
  "image_url": "",
  "booking_url": "",
  "collected_at": "",
  "source_confidence": "high|medium|low",
  "matched_sources": [],
  "source_count": 1,
  "notes": []
}
```

Field rules:

- `price_cny` must be numeric and only derived from a visible or returned price for the same date. Keep the raw text in `price_text`.
- `rating` should be normalized to a 5-point scale when possible. If the source uses another scale, note the conversion.
- Use AMap coordinates when a source lacks coordinates and the hotel can be confidently matched by name and area.
- Keep uncertain data as null or empty; do not invent missing fields.

## De-duplication

Treat candidates as the same hotel when two or more signals match:

- Normalized hotel names are highly similar after removing punctuation, spaces, platform suffixes, and common words like `酒店`, `民宿`, `客栈`, `山庄`.
- Coordinates are within 300 meters.
- Address or area text is clearly the same.
- Booking/detail pages identify the same platform hotel id.

When unsure, keep separate rows and mark `source_confidence: low`. Do not merge hotels with similar names but different villages, scenic areas, or counties.

## Source Coverage

After de-duplication, record which independent sources mention the hotel:

- Count separate platform/source families, not repeated pages from the same family. For example, Ctrip Wendao and Ctrip Web are useful corroboration but should be described as one Ctrip family plus an internal verification note.
- Treat AMap as a location/identity corroboration source, not a price source.
- A hotel matched by two or more independent families, such as Tongcheng Web plus FlyAI/Fliggy plus AMap, earns a credibility/popularity boost because it is easier to verify and compare.
- Do not let source coverage override hard cautions: bad location for the user's transport mode, suspicious room type, no availability, login-only price, or very weak reviews still need to be called out.

Use report labels such as:

- `多源命中`: two or more independent hotel/travel sources match.
- `地图已核`: AMap identity/location is verified.
- `网页已核`: visible web page confirms the requested date and availability.

## Price Comparison

For each deduped hotel:

- List all platform prices and links by source.
- Compute lowest, P25, P40, median/P50, P75, and highest price from valid prices only. P40 is the default "comfort line": it reflects the point where roughly 40% of comparable options are cheaper and 60% are more expensive.
- Treat a price as valid only if it belongs to the requested check-in/check-out date and guest count, or if the source clearly states it is the current available starting price for that query.
- If a platform shows no room, login-only price, or unclear date, keep it as a note and do not use it in numeric scoring.
- When one source surfaces a promising hotel, search the same hotel name in other available sources or visible web pages when practical. Cross-platform prices for the same hotel are more useful than comparing unrelated hotels across platforms.
- Do not apply a default max-price filter before seeing the market. Unless the user provides a hard budget, collect a broad candidate set first, then judge value by the observed local distribution.
- Build the comparable price pool from the same destination/anchor, stay date, guest count, and broadly similar lodging class. If there are enough candidates, compare hotels with hotels and homestays/inns with homestays/inns; if the pool is small, use one local pool and clearly note the mix.
- Rank valid candidate prices from low to high and assign a price percentile. Tied prices share the same percentile band.

Price percentile guidance:

| Price position | Treatment |
| --- | --- |
| `<= P25` | Strong price boost if date, room type, location, and reviews are credible; otherwise mark as possible bargain with verification needed. |
| `P25-P40` | Positive price signal and usually within the comfortable value zone. |
| `P40-P60` | Slight price drag; still acceptable when location, rating, breakfast, parking, or availability is better. |
| `P60-P75` | Clear premium; require visible justification in the recommendation. |
| `> P75` | High-price penalty; recommend only as comfort/location pick or when the market is inventory-constrained. |

Price anomaly rules:

- Mark `low_price_outlier` when a price is more than 35% below the hotel's cross-platform median or the comparable local candidate median.
- Mark `high_price_outlier` when a price is more than 50% above the median.
- For outliers, inspect whether the cause is room type, no window, shared bathroom, non-refundable policy, tax/fee exclusion, distant location, different date, or low inventory.

## Base Score

Default value-for-money score:

| Component | Weight |
| --- | ---: |
| Price | 30% |
| Location | 25% |
| Rating | 18% |
| Review/sales volume and source coverage | 12% |
| Facilities and availability confidence | 15% |

Use this as a ranking guide, not a fake precision score. In the report, explain the top drivers in plain language.

Adjust price weight by intent:

- If the user says "性价比", "别太贵", "预算有限", "价格敏感", or similar, raise Price to about 35% and take the difference mostly from Rating and Facilities.
- If the user gives a hard budget, keep candidates outside the budget visible when useful, but mark them as over-budget instead of hiding the market shape.
- If the user explicitly prioritizes comfort, luxury, family facilities, or a specific hotel class, lower Price to about 25% and explain which premium is justified.

Component guidance:

- Price: first sort valid prices from low to high, compute P40, and favor credible hotels at or below the P40 comfort line. Above P40, apply increasing price drag unless other signals justify the premium. Do not automatically rank the absolute cheapest first when the price is suspicious or the room/location is weak.
- Location: use AMap distance to target and anchors; prefer practical travel distance over raw straight-line distance when route data exists.
- Rating: favor consistently high ratings, but down-weight ratings with little review/sales evidence.
- Review/sales volume and source coverage: reward broad evidence across reviews and independent sources; mark missing volume as unknown rather than bad.
- Facilities/availability: reward visible facilities matching user preferences, clear room availability, breakfast/cancellation info, and parking/transit details when relevant.

## Transport Mode Adjustments

### Self-driving / Has Car

Increase the influence of:

- Parking availability or nearby parking lot.
- Driving route and road access.
- Distance to main road, scenic-area gate, or parking/transfer area.

Decrease the penalty for:

- Being slightly farther from the scenic entrance when driving access and parking are better.

Be cautious about:

- Hotels inside areas where private cars cannot enter.
- Remote hotels with unclear road conditions or no parking evidence.

### Public Transit

Increase the influence of:

- Walking distance to visitor center, shuttle stop, bus stop, train station, or transfer station.
- AMap walking/transit route practicality.
- Clear access to restaurants and basic services without a car.

Penalize:

- Hotels far from transit nodes.
- Hotels that require private transfer without clear availability or price.

### Taxi / Chartered Car

Increase the influence of:

- Road access and pickup/drop-off convenience.
- Practical driving distance to target.
- Clear address and enough local recognizability for drivers.

Decrease the influence of:

- Public transit proximity.

Be cautious about:

- Hotels on roads that are difficult to access at night or in bad weather.

### Unspecified Independent Travel

Use the base score. State that the recommendation assumes ordinary independent travel and balanced location needs.

## Recommendation Tiers

Use 3-5 final recommendations:

- Best value: balanced price, rating, and location.
- Best location: closest or most practical for the user's transport mode.
- Best comfort: higher rating/facilities if price premium is justified.
- Budget pick: cheaper but not suspicious; explain tradeoffs.
- Caution pick: only if a tempting result needs special verification.

Avoid recommending a hotel when:

- The only good signal is a suspiciously low price.
- Location cannot be verified and the area is easy to confuse.
- Browser-visible price conflicts strongly with skill/API price and no explanation is available.
- It is outside the user's excluded area.
