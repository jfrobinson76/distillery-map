# Review Country Copy — 5-Persona Editorial Review

Run a country-page intro paragraph through five review personas before it ships.
Modeled on FarmAI Ireland's `/review-content` — same discipline, different domain.

## Instructions

1. Read `docs/editorial-voice.md` — the voice bible, informs every persona
2. Read the draft intro paragraph(s) under review, plus which country/countries they're for
3. If reviewing more than one country's copy in the same pass, also read the *other*
   drafts in the batch — Fintan (persona 2) needs to check cross-country uniqueness
4. Run all five personas below
5. Present the review table, then the overall verdict

## The Five Personas

### Marguerite — Trade Accuracy
**Role:** 25-year drinks trade veteran. Checks facts and defensibility.
**Questions she asks:**
- Is every specific claim (a date, a regulatory detail, a style) something you could
  defend if a distiller from that country pushed back on it?
- Is whisky/whiskey spelled correctly for this country?
- Does this confuse Scotland with the United Kingdom, or repeat the same claim on
  both pages?
- Any invented statistics, awards, or specifics that aren't broadly established
  industry knowledge?
**Returns:** PASS / CONDITIONAL / FAIL + max 3 specific notes

### Fintan — AI-Slop & Uniqueness Editor
**Role:** Brand voice editor. Checks it doesn't read like a template with the
country name swapped.
**Questions he asks:**
- Any banned words/phrases from `docs/editorial-voice.md`?
- Any AI-tell structures (false-binary openers, triple-adjective lists, generic
  "come explore" closers, restating the country name 3+ times)?
- If you swapped this paragraph onto a different country, would it still sound
  plausible? (If yes — FAIL. Every paragraph must be load-bearing for its country.)
- Read against the other drafts in this batch — any repeated sentence shapes,
  repeated opening moves, or repeated framing across countries?
**Returns:** PASS / CONDITIONAL / FAIL + max 3 specific notes

### Priya — Skeptic Reader
**Role:** The actual reader — a bar buyer or serious enthusiast researching a
region before a trip or a sourcing decision. Not a tourist reading a brochure.
**Questions she asks:**
- Did I learn something real in the first two sentences, or is this filler?
- Does this tell me what's actually distinct about this country's scene?
- Would I trust this enough to mention it to a colleague in the trade?
- Is it appropriately short — does it respect that I came here for the map, not
  an essay?
**Returns:** PASS / CONDITIONAL / FAIL + max 3 specific notes

### Callum — Commercial Neutrality
**Role:** Checks fairness across regions and producers — no favoritism, no
implied endorsement, no put-downs.
**Questions he asks:**
- Does the copy single out or implicitly endorse any specific named distillery?
  (The intro should talk about the scene, not pick winners — naming happens in
  the directory list, not the editorial intro.)
- Does it put down any other country or region to make this one sound better?
- Would a distillery owner in this country, reading this, feel it was fair —
  even if it mentions a bust era or a decline?
- Any defensive-sounding hedges ("no affiliation," "not sponsored by") that
  weren't asked for and just sound weird here?
**Returns:** PASS / CONDITIONAL / FAIL + max 3 specific notes

### Yuki — SEO & Search Intent
**Role:** Checks the page will actually surface for the searches it should.
**Questions she asks:**
- Does this match what someone searching "[country] distilleries" or
  "[country] whisky/whiskey scene" actually wants to know?
- Is the country name and the relevant spirit category (whisky/whiskey/spirits)
  present naturally, without stuffing?
- Is this meaningfully different from the other 68 country pages, or will Google
  see near-duplicate boilerplate across the site? (This is the exact issue that
  triggered this whole review process — see Search Console coverage findings,
  28 Jul 2026.)
**Returns:** PASS / CONDITIONAL / FAIL + max 3 specific notes

## Output

```
| Persona | Verdict | Notes |
|---------|---------|-------|
| Marguerite (Accuracy) | PASS | ... |
| Fintan (Voice/Uniqueness) | CONDITIONAL | ... |
| Priya (Reader) | PASS | ... |
| Callum (Commercial) | PASS | ... |
| Yuki (SEO) | PASS | ... |
```

**Overall verdict:**
- All PASS → ready to ship
- Any CONDITIONAL → fix and re-review before committing
- Any FAIL → needs a real rewrite, not a patch

## The gate

No country-page copy is committed without passing this review. This applies
whether the draft was written in this session or by a delegated subagent — a
subagent drafting copy must run this review itself before reporting the draft
as done, and must report the review table alongside the copy, not just the
copy alone.
