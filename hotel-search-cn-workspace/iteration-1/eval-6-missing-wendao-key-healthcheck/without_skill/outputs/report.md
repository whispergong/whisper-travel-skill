# Baseline Eval Report: Missing WENDAO Key Healthcheck

- Run date: 2026-06-02, Asia/Shanghai
- User task: 假设 `WENDAO_API_KEY` 没配置，查 2026-06-06 喀纳斯贾登峪 2 成人酒店，并说明有哪些来源可用。
- Benchmark assumption: `WENDAO_API_KEY` is missing. I did not attempt a WENDAO call and did not read or use the hotel-search skill path.
- Search parameters used: 喀纳斯 / 贾登峪, check-in 2026-06-06, assumed check-out 2026-06-07, 1 room, 2 adults.

## Executive Summary

With `WENDAO_API_KEY` unavailable, the baseline can still discover credible hotel candidates near 贾登峪 from map POI data and public OTA pages, but it cannot reliably confirm exact-date bookable inventory or final prices for 2026-06-06.

The best available baseline sources are:

1. 高德地图 POI lookup: usable for hotel discovery, addresses, coordinates, photos, ratings, and whether a POI appears booking-enabled in map metadata.
2. 携程 public mobile hotel pages: reachable with check-in/check-out URL parameters, useful for hotel identity and metadata, but static HTML did not expose a reliable date-specific room-rate table.
3. Trip.com public pages/search results: usable for cross-checking hotel names, ratings/reviews, room-type hints, and some addresses, but not enough for authoritative exact-date stock/price without interactive/API booking flow.
4. Generic web search: usable for discovery and source links, but not reliable for live inventory.

## Hotel Candidates Found

These are candidates near the 贾登峪接待基地 / 喀纳斯景区入口 area. “Date availability” is not confirmed unless a source explicitly exposes bookable inventory for 2026-06-06, which the baseline did not obtain.

| Hotel | Evidence found | Baseline status |
| --- | --- | --- |
| 喀纳斯苏豪酒店(贾登峪店) | 高德 POI: 贾登峪三区33号楼, rating 4.6, booking flag present. 携程 mobile page reachable. Trip.com public page found. | Strong candidate. Exact 2026-06-06 price/stock not confirmed. |
| 喀纳斯爱琴海酒店(贾登峪店) / Kanas Aegean Sea Homestay | 高德 POI: 贾登峪综合旅游接待基地三区11号楼, rating 4.3, booking flag present. Trip.com public listing found. | Strong candidate. Exact 2026-06-06 price/stock not confirmed. |
| 北苑山庄(喀纳斯景区贾登峪国家森林公园店) | 高德 POI: 贾登峪三区58号北苑山庄, rating 4.5, booking flag present. Trip.com public listing found. | Strong candidate. Exact 2026-06-06 price/stock not confirmed. |
| 贾登峪栖云客栈 / Kanas Qiyun Hotel | 高德 POI: 贾登峪旅游接待基地三区24号楼, rating 4.7, booking flag present. Trip.com public listing found. | Strong candidate. Exact 2026-06-06 price/stock not confirmed. |
| 喀纳斯贾登峪城堡度假酒店 / 疆来旅投大酒店(贾登峪城堡酒店) | 高德 POI: 喀纳斯旅游风景区贾登峪小镇 / 景区消防救援大队西南侧约140米. 城堡度假酒店 rating 3.4; one related POI had no map booking flag. | Candidate, but lower confidence for direct baseline booking. Exact 2026-06-06 price/stock not confirmed. |
| 喀纳斯夜泊酒店 | 高德 POI: 贾登峪综合服务区别墅区三区19号, booking flag present. | POI-only candidate. Exact 2026-06-06 price/stock not confirmed. |
| 喀纳斯一朵莲酒店 | 高德 POI: 贾登峪三区二十二栋, booking flag present. | POI-only candidate. Exact 2026-06-06 price/stock not confirmed. |
| 贾登峪快船酒店 | 高德 POI: 贾登峪景区三区55号, booking flag present. | POI-only candidate. Exact 2026-06-06 price/stock not confirmed. |
| 喀纳斯宿在山间民宿(贾登峪店) | 高德 POI: 贾登峪综合旅游接待基地三区别墅A3-7栋. | POI-only candidate. Exact 2026-06-06 price/stock not confirmed. |
| 喀纳斯峪源山庄 / 喀纳斯万峰山庄 / 贾登峪肆拾壹号苑 / 游牧传奇民宿 / 布尔津米克山庄 / 布尔津西坡山乡民宿 | 高德 POI candidates within the same area. | Backup candidates. Exact 2026-06-06 price/stock not confirmed. |

## Source Availability Healthcheck

| Source | Available under missing WENDAO key? | What it can provide | Limitation |
| --- | --- | --- | --- |
| WENDAO | No | Nothing in this benchmark run. | `WENDAO_API_KEY` is assumed missing, so WENDAO should be treated as unavailable. |
| 高德地图 POI | Yes | Location/geocode, nearby hotel POIs, address, coordinates, rating, photos, and map booking metadata. | Does not provide a verified 2026-06-06 room inventory/price through this baseline interface. |
| 携程 public mobile page | Partially | Hotel identity, page metadata, facilities/reviews context, and exact-date URL parameters can be supplied. | Static fetch exposed page/room markers but not a clean authoritative exact-date price/availability table. |
| Trip.com public pages/search | Partially | Hotel name cross-checking, ratings/reviews, address/room-type hints, public property pages. | Public pages/search snippets are not authoritative live inventory; final availability requires interactive/API booking confirmation. |
| Generic web search | Yes | Discovery of candidate hotel names and OTA/source pages. | Can be stale and should not be used alone for pricing or stock. |
| Project hotel-search skill path | Not used | None. | Excluded by benchmark instruction. |

## Source Links Checked

- 高德地图 search entry point: [贾登峪 酒店](https://ditu.amap.com/search?query=%E8%B4%BE%E7%99%BB%E5%B3%AA%20%E9%85%92%E5%BA%97)
- 携程 mobile exact-date page tested for 苏豪酒店: [喀纳斯苏豪酒店(贾登峪店), 2026-06-06 to 2026-06-07, 2 adults](https://m.ctrip.com/html5/hotel/hoteldetail/46035644.html?checkIn=2026-06-06&checkOut=2026-06-07&adults=2&children=0&rooms=1)
- Trip.com public page checked for 苏豪酒店: [Kanas Suhao Hotel](https://tw.trip.com/hotels/burqin-hotel-detail-46035644/kenasi-suhao-hotel/)
- Trip.com generic search entry point: [Kanas Jiadengyu hotels](https://www.trip.com/hotels/list?city=3327&searchword=Jiadengyu%20Kanas)

## Bottom Line

For a missing-WENDAO-key baseline, the usable output is a candidate shortlist plus source health status, not a confirmed booking quote. The most credible next booking-facing sources are 携程 and Trip.com, while 高德 is the best fallback for local POI discovery. Exact 2026-06-06 availability and final prices remain unconfirmed in this baseline run.
