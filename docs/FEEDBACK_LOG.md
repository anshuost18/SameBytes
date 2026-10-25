# Feedback log (raw material for the required submission feedback)

> Add an entry the moment something is good, confusing, broken or missing. Be specific: name the tool, the step, the error, and what we expected. On Thursday we'll turn this into the Devpost feedback section (`DEMO_AND_SUBMISSION.md` §7). Ten "Most Valuable Feedback" awards of $100 + NVIDIA swag are given.
>
> The organizers asked us to cover, for each tool:
> - what we used it for;
> - what worked;
> - what needs work;
> - onboarding (zero to hello world);
> - whether we'd build with it again, and why.

## Template

```
- YYYY-MM-DD HH:MM | Tool: <Token Factory inference / Batch / Sandboxes / Nemotron Ultra|Super|3.5 Super|Lightning|Nano / Tavily / Builders Program>
  What we were doing:
  What happened (exact error / behaviour):
  What we expected:
  Workaround (if any):
  Severity: blocker / annoying / minor / praise
```

## Token Factory (inference)

- 2026-10-24 | Onboarding (reported by other participants on the Devpost forum, not yet confirmed by us): the billing check rejects RuPay cards, and support confirmed there's no card-free activation. Fill in our own experience here.
- 2026-10-25 | Tool: Token Factory inference
  What we were doing: first API call from the OpenAI Python SDK with a custom base_url.
  What happened: worked first try; /models listed 30 models; automatic prefix caching worked (4,224 of 4,520 prompt tokens cached on the second identical call).
  Severity: praise
- 2026-10-25 | Tool: Token Factory model catalog (observed during research)
  What happened: model IDs use inconsistent casing and separators (`nvidia/nemotron-3-super-120b-a12b`, `nvidia/Nemotron-3-Ultra-550b-a55b`, `nvidia/Nemotron-3_5-Lightning` with an underscore, `nvidia/Nemotron-3.5-Super-VL` with a dot). Easy to mistype.
  What we expected: one naming convention, or case-insensitive aliases.
  Severity: minor
- (T06) Whether `chat_template_kwargs` reasoning controls (`enable_thinking`, `reasoning_budget`, `force_nonempty_content`) are honoured, per model: record the result here.

## Token Factory Batch inference

- (Tue) Request shape, turnaround time, and whether caching or discounts apply: record here.

## Token Factory Sandboxes (beta)

- (Sun) Access request sent: record the date and response time here.

## Nemotron 3 Nano

- 2026-10-25 | Tool: Nemotron 3 Nano
  What happened: with max_tokens=50, content came back as None and completion_tokens=50, because reasoning tokens used the whole budget. With max_tokens=1500 it returned the answer, with thinking in a separate `reasoning` field.
  What we expected: a short answer.
  Workaround: use a large max_tokens. A docs note on reasoning-token budgets would help.
  Severity: annoying
- 2026-10-25 | Tool: Nemotron 3 Nano
  What happened: JSON mode and function calling both worked first try, about 0.5s latency on a trivial call.
  Severity: praise

## Nemotron 3 Super

- 2026-10-25 | Tool: Nemotron 3 Super
  What happened: JSON mode and function calling worked first try (148 completion tokens for a small JSON answer).
  Severity: praise

## Nemotron 3.5 Super VL / 3.5 Lightning

-

## Nemotron 3 Ultra

- 2026-10-25 | Tool: Nemotron 3 Ultra
  What happened: JSON mode and function calling worked first try (109 completion tokens for a small JSON answer).
  Severity: praise

## Tavily

-

## Docs / Builders Program / credits

-
