# Agent Orchestration

Use subagents when the environment supports them and the user permits parallel work. The main agent owns the final route, tradeoffs, and report.

## Recommended Workstreams

- `小红书攻略 agent`: search notes, fetch details, collect image URLs, summarize text/comments and practical warnings.
- `图片理解 agent`: inspect downloaded Xiaohongshu or webpage images and extract visual facts.
- `网络/本地语言 agent`: search official sites, local guides, road/ticket notices and non-XHS corroboration.
- `高德路线 agent`: geocode points, verify route distances/durations, find POIs, parking, gas/charging and visitor centers.
- `沿途点 agent`: evaluate segment-by-segment stops for scenic value and feasibility.
- `酒店 agent`: call `hotel-search-cn` for each stable daily lodging anchor.
- `费用 agent`: compile hotel, fuel, toll, ticket, parking, meals and buffer estimates.

## Concurrency Rules

- Xiaohongshu detail fetching is rate-sensitive. Only one Xiaohongshu agent should operate the browser/session at a time; fetch at most 3 details before waiting 10-20 seconds.
- Shared visible browsers, Chrome bridge, Edge profiles, Ctrip/Tongcheng web pages and login flows must be controlled by one browser agent at a time.
- Hotel searches can run per day in parallel after the route and lodging anchors are stable.
- A hotel subagent may internally use source-level subagents according to `hotel-search-cn`; keep final accommodation summaries scoped to that day.
- Do not let subagents make final route decisions. They return facts, candidates, risks, and confidence labels.

## Queue Priority

If subagent capacity is limited, queue in this order:

1. 高德路线 grounding.
2. 小红书攻略 and image evidence.
3. 网络/official corroboration.
4. 沿途点 refinement.
5. Hotels per night.
6. Cost table.

If subagents are unavailable, use parallel tool calls where safe, then fill gaps serially. State that no subagents were used.

## Handoff Format

Ask each subagent to return:

```markdown
## Sources Used
| Source | Query/URL | What it supports | Confidence |

## Facts
- [fact with source]

## Candidates
| Item | Why it matters | Feasibility | Risk |

## Open Questions
- [thing the main agent should verify or ask]
```

Keep raw copied text short. Prefer summaries with source links or note IDs.
