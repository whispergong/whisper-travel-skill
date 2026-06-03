# Eval 5: Missing Required Inputs

## Task

帮我找喀纳斯附近性价比高的酒店。

## Skill Used

Primary instructions: `/Users/whisper/Desktop/workplace/whisper-travel-skill/hotel-search-cn/SKILL.md`

## Required Input Check

The skill requires these fields before any hotel search:

| Field | Status | Notes |
| --- | --- | --- |
| 目的地或 POI | Present | 喀纳斯附近 |
| 入住日期 | Missing | Must be a concrete date; do not guess or use the current date. |
| 离店日期 | Missing | Must be a concrete date; do not infer nights without user input. |
| 入住人数 | Missing | Adult and child counts are required. |
| 房间数 | Defaultable | Skill allows defaulting missing room count to 1 room. |

## Decision

Do not perform hotel search.

The request is missing required stay dates and guest counts. Per the skill, when destination, dates, or guest count are missing, the correct behavior is to ask a brief clarification first. Because this eval explicitly says not to ask the real user, the exact clarification is recorded below instead.

## Exact Clarification To Ask

请补充入住日期、离店日期和入住人数（成人/儿童）；房间数如不说我先按 1 间。

## Search Status

No Preflight health check was run.

No hotel sources were called.

No dates, guest counts, hotel names, prices, ratings, or recommendations were invented.
