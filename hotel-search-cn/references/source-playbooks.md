# Source Playbooks

Use the same user intent across every source: destination or POI, check-in date, check-out date, adults, children, rooms, budget, facilities, excluded areas, and transport mode. Preserve negative constraints such as "不要县城", "不要禾木", or "只看景区入口附近".

## AMap MCP

Purpose:

- Resolve the destination/POI to coordinates.
- Discover hotel, inn, homestay, dining, parking, visitor-center, bus/transfer-station, and scenic-gate clusters.
- Measure distance from candidate hotels to target points and lodging anchors.
- Adjust location quality by transport mode.

Recommended calls:

- `maps_geo` for destination and anchor geocoding.
- `maps_around_search` around the target coordinate for keywords: `酒店`, `民宿`, `客栈`, `游客中心`, `停车场`, `公交`, `餐饮`.
- `maps_distance` for straight-line, walking, or driving distance checks.
- `maps_direction_driving`, `maps_direction_walking`, or `maps_direction_transit_integrated` when route shape matters.

Capture:

- POI name, address, coordinate, type, distance from target, and source confidence.
- 1-3 recommended lodging anchors with reason: e.g. "closest to visitor center", "better for parking", "better for transit".

Failure handling:

- If the exact POI is ambiguous, search multiple candidates and ask the user only when the ambiguity changes the recommended area.
- If a POI has no coordinate, keep it out of scoring and mark it as unverified.

## FlyAI / Fliggy

Use `flyai-cli` MCP when exposed in the current agent. Otherwise use the `flyai` CLI directly:

```bash
flyai search-hotel \
  --dest-name "<city-or-district>" \
  --poi-name "<poi-or-anchor>" \
  --check-in-date YYYY-MM-DD \
  --check-out-date YYYY-MM-DD \
  --sort no_rank
```

Optional filters:

- `--key-words "<hotel-or-area-keyword>"`
- `--hotel-types "酒店"` / `民宿` / `客栈`
- `--hotel-stars "3,4,5"`
- `--hotel-bed-types "大床房,双床房"`
- `--max-price <number>` only when the user gives a hard budget; otherwise avoid price caps until after the initial market distribution is known.
- `--sort distance_asc`, `rate_desc`, `price_asc`, or `no_rank`.

Capture from each item:

- `name`, `price`, `score`, `scoreDesc`, `star`, `address`, `latitude`, `longitude`, `interestsPoi`, `review`, `mainPic`, `detailUrl`, `shId`.

Failure handling:

- If the CLI is missing, install it with `npm i -g @fly-ai/flyai-cli`, then verify with `flyai --help` and one lightweight `search-hotel` or `keyword-search` call.
- If an agent needs MCP access, prefer the local `flyai-cli` MCP wrapper configured at `/Users/whisper/Desktop/workplace/whisper-travel-skill/tools/flyai-cli-mcp/server.mjs`. It calls the verified CLI and works for Codex/Cursor without relying on static HTTP headers.
- Use `flyai-http` only as a diagnostic path. The FlyAI CLI signs requests with dynamic `x-ff-ctx`, `x-ttid`, and HMAC headers; a static Bearer-only Streamable HTTP MCP can return 401 even when the CLI key is valid.
- To diagnose `flyai-http`, test the Streamable HTTP endpoint directly:

```bash
MCP_SECRETS_FILE="${MCP_SECRETS_FILE:-$HOME/.config/mcp/secrets.env}"
set -a; [ -f "$MCP_SECRETS_FILE" ] && . "$MCP_SECRETS_FILE"; set +a
jq -nc '{
  jsonrpc:"2.0",
  id:1,
  method:"initialize",
  params:{
    protocolVersion:"2025-03-26",
    capabilities:{},
    clientInfo:{name:"codex-hotel-search",version:"0.1"}
  }
}' |
curl -sS -X POST "https://flyai.open.fliggy.com/mcp" \
  -H "Authorization: Bearer $FLYAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d @-
```

- HTTP 401/403 means the static HTTP MCP auth is invalid for this endpoint. If CLI works, mark FlyAI as "CLI/MCP wrapper available, HTTP MCP auth failed" and use CLI results.
- If both CLI and MCP are unavailable, mark FlyAI as failed and include the missing command/key/auth cause in source health.

## AIGoHotel MCP

Use the exposed AIGoHotel tools when available. If the current tool layer does not expose them but Codex config contains `mcp_servers.aigohotel`, use Streamable HTTP fallback before marking the source unavailable.

Capture:

- Hotel name, platform/source id, price, rating, sales/review count if present, facilities, address, coordinate, room availability, and booking link.

Failure handling:

- If `/Users/whisper/.codex/config.toml` contains `mcp_servers.aigohotel` but no tool is exposed to this session, try Streamable HTTP fallback before declaring it unavailable:

```bash
MCP_SECRETS_FILE="${MCP_SECRETS_FILE:-$HOME/.config/mcp/secrets.env}"
set -a; [ -f "$MCP_SECRETS_FILE" ] && . "$MCP_SECRETS_FILE"; set +a
jq -nc '{
  jsonrpc:"2.0",
  id:1,
  method:"initialize",
  params:{
    protocolVersion:"2025-03-26",
    capabilities:{},
    clientInfo:{name:"codex-hotel-search",version:"0.1"}
  }
}' |
curl -sS -X POST "https://mcp.aigohotel.com/mcp" \
  -H "Authorization: Bearer $AIGOHOTEL_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d @-
```

Then call `tools/list` and look for `searchHotels` and `getHotelDetail`. If present, record "AIGoHotel callable via HTTP fallback" and use `tools/call`. You can also use the bundled helper, which wraps the same JSON-RPC calls:

```bash
node /Users/whisper/Desktop/workplace/whisper-travel-skill/hotel-search-cn/scripts/aigohotel-mcp.mjs tools-list
```

Search example:

```bash
jq -nc '{
  jsonrpc:"2.0",
  id:2,
  method:"tools/call",
  params:{
    name:"searchHotels",
    arguments:{
      originQuery:"2026-06-13 入住 2026-06-14 离店，2名成人1间房，自驾，喀纳斯贾登峪附近酒店，优先停车",
      place:"贾登峪",
      placeType:"详细地址",
      countryCode:"CN",
      checkInParam:{checkInDate:"2026-06-13",stayNights:1,adultCount:2},
      filterOptions:{distanceInMeter:10000},
      size:10
    }
  }
}' |
curl -sS -X POST "https://mcp.aigohotel.com/mcp" \
  -H "Authorization: Bearer $AIGOHOTEL_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d @-
```

Equivalent helper command:

```bash
node /Users/whisper/Desktop/workplace/whisper-travel-skill/hotel-search-cn/scripts/aigohotel-mcp.mjs search \
  --place "贾登峪" \
  --place-type "详细地址" \
  --check-in-date 2026-06-13 \
  --nights 1 \
  --adults 2 \
  --distance 10000 \
  --size 10 \
  --query "2026-06-13 入住 2026-06-14 离店，2名成人1间房，自驾，喀纳斯贾登峪附近酒店，优先停车"
```

- Retry empty searches with multiple `place`/`placeType` combinations, such as city/district, scenic spot, POI, and detailed address.
- Treat a successful call with an empty hotel list as "empty result", not an environment failure.
- Do not fabricate AIGoHotel results from other sources.

## Tongcheng Chengxin

Use the official Chengxin hotel script:

```bash
cd /Users/whisper/.agents/skills/chengxin
node scripts/hotel-query.js \
  --destination "<city-or-region>" \
  --extra "<check-in/check-out, adults/children/rooms, POI/anchor, budget, facilities, exclusions>" \
  --channel webchat \
  --surface webchat
```

Example:

```bash
node scripts/hotel-query.js \
  --destination "阿勒泰地区" \
  --extra "2026-06-06 入住 2026-06-07 离店 2名成人 1间房 新疆喀纳斯景区 贾登峪附近 不要布尔津县城 不要禾木 价格 评分 房源 设施" \
  --channel webchat \
  --surface webchat
```

Capture:

- Hotel name, shown price, rating, tags/facilities, location text, booking link, and any room-status hint.

Failure handling:

- Missing `CHENGXIN_API_KEY` is a source-health issue. Ask the user to configure it or confirm degraded execution.
- If the script returns results but lacks coordinates, later match with AMap by hotel name and area.

## Ctrip Wendao

Use the official Wendao endpoint:

```bash
TOKEN="$WENDAO_API_KEY"
USER_QUERY="<natural-language hotel query>"
jq -n --arg token "$TOKEN" --arg query "$USER_QUERY" \
  '{token: $token, query: $query}' |
  curl -s -X POST https://wendao-skill-prod.ctrip.com/skill/query \
    -H "Content-Type: application/json" \
    -d @-
```

Query template:

```text
请搜索<destination>/<poi>附近酒店，入住<checkin>，离店<checkout>，<adults>名成人，<children>名儿童，<rooms>间房。
偏好：<budget/facilities/transport/exclusions>。
请尽量返回酒店名、价格、评分、位置、设施、房源或预订链接。
```

Capture:

- Hotel name, price, rating, location text, facilities, room/booking hints, and links.

Failure handling:

- Missing `WENDAO_API_KEY` is a source-health issue.
- If Wendao returns prose rather than structured rows, extract only facts present in the response and mark field completeness as partial.

## Visible Browser / Edge Extension / Playwright Profile

Use a user-visible browser for Ctrip and Tongcheng web checks. Follow the Playwright best-practices skill for locator choice, authentication reuse, waits, and multi-tab handling.

Preferred order:

1. Codex Chrome/Edge extension: use the existing user Edge window/profile, claim an existing hotel tab or open a new tab, then operate through `tab.playwright` locators. This is the best path for real login state, member prices, and user-visible login handoff.
2. Existing visible Edge/Playwright persistent profile: use this only if the extension route is unavailable. In the current Codex/Cursor setup this may look like `--browser msedge --user-data-dir ...`.
3. Codex in-app browser: acceptable for public page structure checks, but it normally does not share Edge cookies or member login state, so do not rely on it for login-only prices.
4. New persistent browser profile: last resort; tell the user which profile is being used.

Extension route checks:

- Bootstrap through the Chrome skill/browser-client and call `agent.browsers.get("extension")`.
- Call `browser.user.openTabs()` once to confirm the extension can see tabs. Any non-error response means the extension is usable.
- If a matching Ctrip/Tongcheng tab is already open, claim it with `browser.user.claimTab(tabInfo)` using the exact object returned by `openTabs()`.
- If no matching tab is open, use `browser.tabs.new()` and navigate to the platform homepage.
- At the end of the browser work, call `browser.tabs.finalize({ keep })`. Keep a tab as `handoff` only when the user still needs to log in or continue from that live page.

Concurrency and fallback:

- When multiple agents are collecting sources, avoid simultaneous writes and avoid closing the shared browser. Browser agents should open their own tab, capture results, and leave the session available for others.
- Do not run several Playwright agents against the same persistent `user-data-dir` at the same time. If old Playwright MCP Edge sessions are timing out or stuck loading, prefer the extension route or stop the duplicate MCP sessions before retrying.
- If the user asks to use the global Edge profile and it is already occupied, try the extension route or open a new tab in the existing browser. Do not forcibly close or steal the user's browser.
- For login-required pages, navigate visibly to the login/search/detail page and ask the user to complete login. After login, continue in the same browser/profile so the session persists for later agents.
- Use role/label/text locators first; use CSS selectors only for non-semantic legacy pages or after capturing visible page structure.
- Avoid AppleScript DOM execution as a primary path. Edge may block JavaScript from Apple Events unless the user enables that setting, and the extension route is more reliable.

## Tongcheng Web

Use Playwright to simulate a user on the visible web UI.

Validated paths:

### Homepage-to-list path

1. Open `https://www.ly.com/hotel`.
2. Enter city or county, e.g. `布尔津县` or `博乐市`.
3. Enter target keyword in the keyword field, e.g. `贾登峪` or `赛里木湖`.
4. Set check-in and check-out dates, adults, and children by visible controls when possible.
5. Click search.
6. Confirm the result page URL contains `/hotel/hotellist`.

Note: on the Tongcheng homepage, directly setting date input values via JavaScript may leave the app state at the default dates. Prefer visible calendar controls; if the page has already produced a result URL with the correct city code, use the list URL path below for a stable repeatable search.

Validated desktop controls:

- City input: `input.searchInput.address`.
- Check-in input: `input.date.start`; check-out input: `input.date.end`.
- Calendar day cells: `div[data-date="YYYY-MM-DD"]`.
- Keyword input: `input.keyWordInput`.
- Guest control: `#hotel_peoples`; adult plus is the first `.peoplesInfo .icon-people_max`; finish with visible text `完成`.
- Search button: `.searchBtn`.

For Sayram Lake, select the city suggestion `博乐市`, set keyword `赛里木湖`, and verify the list page still shows the keyword after search.

### List URL path after city code is known

Use a visible page route generated from the user path, not hidden APIs:

```text
https://www.ly.com/hotel/hotellist?city=<cityCode>&inDate=YYYY-MM-DD&outDate=YYYY-MM-DD&keywords=<encoded keyword>
```

Known Kanas / Jiadengyu example validated on 2026-06-02:

```text
https://www.ly.com/hotel/hotellist?city=2569&inDate=2026-06-13&outDate=2026-06-14&keywords=%E8%B4%BE%E7%99%BB%E5%B3%AA
```

Expected visible confirmations:

- Page title or search box shows `布尔津县`.
- Date strip shows `6月13日 周六` and `6月14日 周日`.
- Keyword chip/search box shows `贾登峪`.
- The page may show login status such as `Hi，同程会员...`; if not logged in, prices or member discounts may require login.
- Validated visible result count for this example: `84 家酒店`.

Known Sayram Lake example validated on 2026-06-03:

```text
https://www.ly.com/hotel/hotellist?city=2521&inDate=2026-06-13&outDate=2026-06-14&keywords=%25E8%25B5%259B%25E9%2587%258C%25E6%259C%25A8%25E6%25B9%2596
```

Expected visible confirmations:

- Page title or search box shows `博乐`.
- Date strip shows `6月13日 周六` and `6月14日 周日`.
- Guest control shows `2 成人 0 儿童`.
- Keyword chip/search box shows `赛里木湖`.
- Validated visible result count for this example: `199 家酒店`.
- If the page top says `您好，请 登录` or list cards show `￥？`, the route is working but prices require login verification. Keep names, scores, distance, facilities, and room-status hints; mark price as `需登录复核`.

Example first-page visible results for the Sayram Lake search when not logged in:

- `赛里木湖山水庄园`, 3.6 / 259 reviews, 3km from 赛里木湖景区(白鸟湖口景点), free parking, washing service, charging pile, room tight, `￥？`.
- `赛里木湖中亚全纳酒店`, 4.4 / 2170 reviews, 920m from 赛里木湖景区(白鸟湖口景点), free parking, meeting room, chess room, only 3 low-price rooms, `￥？`.
- `蓝湖国际酒店B座(赛里木湖景区店)`, 4.8 / 751 reviews, 698m from 赛里木湖景区(白鸟湖口景点), free parking, new opening, washing service, charging pile, only 2 low-price rooms, `￥？`.
- `赛里木湖望山一号院子(赛里木湖景区店)`, 4.9 / 2947 reviews, 1.3km from 赛里木湖景区(白鸟湖口景点), free parking, pickup, gym, smart room controls, only 1 low-price room, `￥？`.
- `赛里木湖万豪AC酒店`, 4.8 / 995 reviews, 1.8km from 赛里木湖景区(白鸟湖口景点), free parking, new opening, pickup, spa, chess room, `￥？`.

Example first-page visible results for the known Kanas search:

- `贾登峪快船酒店`, 4.6 / 1879 reviews, 535m from 贾登峪, free parking, `¥428起`.
- `喀纳斯舒心别苑`, 4.5 / 278 reviews, 517m from 贾登峪, free parking, `¥238起`.
- `喀纳斯鸿瑞山庄(贾登峪店)`, 4.4 / 588 reviews, 559m from 贾登峪, free parking, `¥268起`.
- `喀纳斯夜泊酒店`, 4.9 / 302 reviews, 489m from 贾登峪, free parking, `¥340起`.
- `喀纳斯白桦林度假酒店`, 4.8 / 1848 reviews, 1.3km from 贾登峪, free parking and charging pile, `¥532起`.

Capture:

- Hotel name, price, rating, distance text, tags/facilities, sales/review hints, room-status hints, and detail link.

Failure handling:

- If the page route works but a particular POI has no suggestion, retry with county/city plus target keyword.
- If login/captcha blocks visible list access or prices, open the page in a visible browser/profile and ask the user to log in. After login, continue with the same browser profile and re-run the visible search path.
- If the user declines login or cannot complete it, mark price fields as "requires login verification" and still capture visible non-price fields when available.
- If a homepage click lands on the login page because a membership banner intercepts the click, do not mark Tongcheng failed. Return to the hotel page and use the visible search fields or the stable list URL path.
- Do not use hidden API calls unless the user explicitly asks for reverse engineering.

## Ctrip Web

Use Playwright to simulate a user on desktop or mobile Ctrip hotel search.

Preferred paths:

- Desktop homepage: `https://www.ctrip.com/`.
- Desktop hotel page fallback: `https://hotels.ctrip.com/`.
- Mobile fallback: `https://m.ctrip.com/webapp/hotels/`.

Steps:

1. Enter destination city/region and target POI.
2. Pick a visible suggestion matching the intended POI.
3. Set check-in/check-out dates and room/guest count.
4. Submit search.
5. Capture visible list count and first 20 results when possible.

Validated desktop controls from `https://www.ctrip.com/`:

- Destination input: `#hotels-destination`; for Sayram Lake choose visible suggestion `博乐, 新疆, 中国`.
- Keyword input: `#keyword`.
- Date display/control: `#checkIn`; in the calendar, scope to `.c-calendar-month` containing the target month such as `2026年6月`, then click day `13` and day `14`.
- Guest control: visible text such as `1间, 1位`; in `.hotel-search-box-roomguest-choice`, the `.hs_icon-btn_Gs-wx` buttons are room minus, room plus, adult minus, adult plus, child minus, child plus. Click adult plus once for 2 adults, then finish with `.hs_done-span_-EIBx`.
- Search button: `.hs_search-btn-container_R0HuJ`.

Known Sayram Lake example validated on 2026-06-03:

```text
https://hotels.ctrip.com/hotels/list?countryId=1&city=2548&provinceId=0&checkin=2026/06/13&checkout=2026/06/14&optionId=2548&optionType=City&directSearch=1&optionName=%E8%B5%9B%E9%87%8C%E6%9C%A8%E6%B9%96&display=%E8%B5%9B%E9%87%8C%E6%9C%A8%E6%B9%96&crn=1&adult=2&children=0&searchBoxArg=t&travelPurpose=0&ctm_ref=ix_sb_dl&domestic=1&&v2_mod=84&v2_version=E
```

Expected visible confirmations:

- Search box shows `博乐`.
- Dates show `6月13日(周六)` to `6月14日(周日)`.
- Guest button shows `1间, 2成人, 0儿童`.
- Keyword shows `赛里木湖`.
- Result count shows `找到386家酒店`.
- If the top navigation shows an account name rather than a login prompt, logged-in prices can be captured from the list.

Example first-page visible results for the Sayram Lake search when logged in:

- `赛里木湖丽呈花盛国际酒店`, 79 reviews, near 赛里木湖景区(白鸟湖口景点), free cancellation, low-price room only 1, `¥1,157` from visible discounted price.
- `如山如宿民宿(赛里木湖东门游客中心店)`, 4.4 / 178 reviews, near 白鸟湖口/月亮湾, free cancellation, low-price room only 1, `¥786`.
- `赛里木湖福泽颐居民宿（赛里木湖景区店）`, 4.3 / 87 reviews, near 白鸟湖口/博州赛里木湖滑雪场, free cancellation and breakfast, `¥909`.
- `赛柯里民宿（赛里木湖东门游客中心店）`, 4.2 / 601 reviews, near 白鸟湖口/三台海子, free cancellation, only 2 rooms, `¥872`.
- `蓝湖国际酒店B座（赛里木湖景区店）`, 4.5 / 390 reviews, near 白鸟湖口/三台海子, free cancellation, only 2 rooms, `¥1,049`.
- `蓝湖国际酒店A座（赛里木湖景区店）`, 4.7 / 705 reviews, near 白鸟湖口/月亮湾, free cancellation, `¥1,217`.
- `赛里木湖逸扉酒店`, 4.7 / 227 reviews, Hyatt affiliated, near 白鸟湖口/天境里, free cancellation and breakfast, `¥1,673`.
- `入画入梦民宿（赛里木湖游客中心店）`, 4.7 / 45 reviews, near 白鸟湖口/月亮湾, free cancellation, only 4 rooms, `¥702`.

Capture:

- Hotel name, price, rating, distance/location text, review/sales hints, facilities/tags, room status, and link.

Failure handling:

- Desktop failure may be retried on mobile.
- If mobile returns a usable list and desktop does not, mark desktop as failed and mobile as successful.
- If Ctrip redirects to login or shows login-only prices, open the login/detail/search page in a visible browser and let the user log in. Reuse that browser profile for the follow-up search.
- If the user does not log in, visible detail pages may still verify date, room availability, score, facilities, and policies; do not treat login-only prices as numeric prices.
- If a natural-language source such as Wendao returns a Ctrip hotel detail link, use the visible detail page to verify date, room availability, score, facilities, and policies for that specific candidate, then search the broader list if needed for alternates.
- Do not silently mix results from a different city or broad district; compare with AMap coordinates before recommending.

## Excluded Sources

Do not use these in v1:

- Jinko MCP.
- `travel-cn`.
- Qunar web.

Qunar verification note:

- Domestic hotel homepage and city pages redirected to the main Qunar homepage.
- Mobile guessed hotel paths also redirected to the main homepage.
- Overseas hotel page opened, but search redirected to login before results.
- Result: not stable enough for domestic hotel list collection in v1.
