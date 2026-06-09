---
name: whisper-travel-cn
description: Use when the user asks in Chinese for trip planning, route planning, self-driving or public-transport itineraries, daily lodging, travel budgets, Tencent travel documents, China scenic-area hotels, domestic hotel search, or Ctrip/Tongcheng/Fliggy hotel comparison.
---

# Whisper Travel CN

This is the integrated entrypoint for the `whisper-travel-skill` repository. Use it as the one installed skill, then dispatch internally to the bundled subskills. Do not answer from this file alone when a subskill applies.

## Dispatch

- Full itinerary, route planning, self-driving or public-transport plans, day-by-day schedules, guide research, route maps, costs, Tencent smart travel documents, or requests like "从 A 到 B 怎么玩": read and follow `travel-planning-cn/SKILL.md`.
- Hotel-only or lodging-only requests, scenic-area hotels, homestays, Ctrip/Tongcheng/Fliggy/FlyAI/AIGoHotel comparison, platform price checks, or "住哪里/查酒店/比价": read and follow `hotel-search-cn/SKILL.md`.
- Mixed requests: use `travel-planning-cn` as the controller. Once daily lodging anchors, dates, people, and transport mode are stable, use `hotel-search-cn` for each lodging task.
- If the user explicitly names `travel-planning-cn` or `hotel-search-cn`, load that subskill directly while still keeping this integrated routing contract in mind.
- If it is unclear whether the user wants a complete trip plan or only hotels, infer from wording. Ask only when the missing choice would materially change the work.

## Subskill Contract

- `travel-planning-cn` owns the final route, daily structure, route/cost tradeoffs, Tencent smart document, and whether hotel findings require itinerary adjustments.
- `hotel-search-cn` owns lodging-source health checks, hotel search, price distribution, cross-platform comparison, Ctrip/Tongcheng/FlyAI/AIGoHotel links, and hotel recommendation ranking.
- The controller should not duplicate hotel scoring logic. The hotel subskill should not rewrite the whole itinerary.
- When the user proposes itinerary changes, the controller must independently research and verify the suggestion with travel sources, official notices when relevant, and AMap route checks before changing the final route. Do not blindly accept user-proposed day merges, new stops, transport changes, or lodging anchors.
- Keep bundled relative paths intact after installation. Do not ask the user to install `travel-planning-cn` and `hotel-search-cn` separately unless they explicitly want direct/debug installs.
- `xiaohongshu-skills` is a third-party dependency. Do not edit or patch that repository from this skill. When Xiaohongshu research is needed, call its local `scripts/cli.py` from the installed Xiaohongshu project and report any login/Bridge issue instead of changing third-party files.

## Browser Priority

- For any browser-based work except Xiaohongshu, use browser surfaces in this fixed order: agent in-app Browser first, then browser-plugin-controlled Chrome/Edge or the current system browser, then standalone Playwright or a persistent Playwright profile; Computer Use is only a last UI fallback after those browser surfaces are unavailable or unsuitable.
- This rule covers Ctrip/Tongcheng web search, Tencent Docs visual verification, AMap web route rendering, ordinary webpage research and login-dependent travel pages. If the agent in-app Browser has a transient setup/tab/navigation problem, retry the lightweight connection or tab operation before declaring it unavailable. Only use Playwright after the first two surfaces are unavailable, blocked or unsuitable for the task.
- Reuse the same browser/profile after the user logs in. Do not switch browser surfaces mid-search or mid-verification unless the current one is unavailable or blocked.
- For Xiaohongshu, treat the XHS Bridge connection as the source of truth. If Edge or Chrome already has the XHS Bridge extension connected, use that connected browser through the Xiaohongshu CLI; if not connected, prefer the browser where the user installed the XHS Bridge extension and ask the user to open/enable it when it cannot be detected.

## Output Behavior

- For complete trip planning, finish with the `travel-planning-cn` report shape and create the Tencent smart document when the environment allows it.
- For hotel-only work, finish with the `hotel-search-cn` report shape and include source health, price distribution, merged comparison, and final recommendations.
- When either subskill requires login, browser control, MCP repair, or user confirmation for degraded execution, surface that in chat before continuing.
