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
- Compute lowest, median, and highest price from valid prices only.
- Treat a price as valid only if it belongs to the requested check-in/check-out date and guest count, or if the source clearly states it is the current available starting price for that query.
- If a platform shows no room, login-only price, or unclear date, keep it as a note and do not use it in numeric scoring.
- When one source surfaces a promising hotel, search the same hotel name in other available sources or visible web pages when practical. Cross-platform prices for the same hotel are more useful than comparing unrelated hotels across platforms.

Price anomaly rules:

- Mark `low_price_outlier` when a price is more than 35% below the hotel's cross-platform median or the comparable local candidate median.
- Mark `high_price_outlier` when a price is more than 50% above the median.
- For outliers, inspect whether the cause is room type, no window, shared bathroom, non-refundable policy, tax/fee exclusion, distant location, different date, or low inventory.

## Base Score

Default value-for-money score:

| Component | Weight |
| --- | ---: |
| Price | 25% |
| Location | 25% |
| Rating | 20% |
| Review/sales volume and source coverage | 15% |
| Facilities and availability confidence | 15% |

Use this as a ranking guide, not a fake precision score. In the report, explain the top drivers in plain language.

Component guidance:

- Price: favor hotels near the local median with good rating and verified availability. Do not automatically rank the cheapest first.
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
