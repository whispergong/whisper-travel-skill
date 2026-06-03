# Skill Benchmark: hotel-search-cn

**Date**: 2026-06-02T08:27:00Z
**Evals**: 1, 2, 3, 4, 5, 6 (1 run each per configuration)
**Skill path**: /Users/whisper/Desktop/workplace/whisper-travel-skill/hotel-search-cn

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Assertion Pass Rate | 100% ± 0% | 76% ± 29% | +0.24 |
| Time | unavailable | unavailable | n/a |
| Output Size | 5409 chars ± 2627 | 3976 chars ± 1471 | +1433 chars |

## Per Eval

| Eval | With Skill | Without Skill | Difference |
| ---: | ---: | ---: | ---: |
| 1 | 100% (6/6) | 50% (3/6) | +0.50 |
| 2 | 100% (4/4) | 100% (4/4) | +0.00 |
| 3 | 100% (4/4) | 75% (3/4) | +0.25 |
| 4 | 100% (5/5) | 100% (5/5) | +0.00 |
| 5 | 100% (3/3) | 33% (1/3) | +0.67 |
| 6 | 100% (4/4) | 100% (4/4) | +0.00 |

## Notes

- Each eval was run once with hotel-search-cn and once without the skill; the aggregate compares 6 with-skill reports vs 6 baseline reports.
- With-skill passed all workflow assertions (100%). Baseline passed 76.4%, with the largest gaps on the composite multi-source workflow and missing-input handling.
- The self-driving, Shanghai, and missing-Wendao-key baselines did well because the prompts explicitly named the important constraints; these assertions are less differentiating.
- The skill consistently improved source-health reporting, explicit fallback behavior, transport-mode weighting, and avoidance of invented dates/results.
- Subagent notifications did not include total_tokens or duration_ms, so timing is unavailable and token statistics in this benchmark are output character counts from report.md, not model token usage.
- Several runs were interrupted to stop long web/API probing; reports include partial source failures. Treat live hotel inventory and pricing as qualitative, not final booking-grade verification.
