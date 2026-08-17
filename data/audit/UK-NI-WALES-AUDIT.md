# Northern Ireland and Wales audit — 16 August 2026

> **CORRECTED 17 August 2026. Defect 2 below is wrong — retracted.**
>
> Machrihanish is not mis-regioned. `region` is a **map viewport** assigned from
> coordinates, not a geography field, and Campbeltown at 55.44°N, -5.66°W sits
> inside a box drawn around Ireland — as does the rest of Kintyre. The `ireland`
> box holds 16 UK rows for exactly this reason. Verified first-hand against the
> source coordinates.
>
> **Defect 1 stands, and is sharpened by this.** The `country` field genuinely is
> inconsistent across the island of Ireland, and that is a real defect
> independent of the viewport question. It is also now the *only* field that
> could carry the answer, since `region` was never claiming to.
>
> **Defects 3 and 4 stand** (Henstone's postcode, and Coles missing).
>
> Practical consequence: none for the jurisdiction resolver, which already leads
> on postcode and treats `region` as a weak secondary. That design was right for
> the wrong stated reason — the code comments describe `region` as unreliable
> when it is better described as answering a different question.

Found while splitting NI and Wales out as GTM jurisdictions in the Stillbound
ops-intelligence account master (`stillbound` branch `gtm/ni-wales-jurisdictions`).
Same class of finding as `CANADA-AUDIT.md`.

## Defect 1 — `country` is inconsistent across the island of Ireland

The 20 Northern Irish sites carry `country: "United Kingdom"` for some rows and
`country: "Ireland"` for others, with no discernible rule. Titanic Distillers,
Rademon Estate, Belfast Distillery, The Quiet Man and Scotts Irish are
"Ireland"; Bushmills, Echlinville, Killowen, Boatyard, Hinch, Copeland and the
rest are "United Kingdom".

Both are defensible readings of a contested constitutional question, which is
probably how it happened. What is not defensible is holding both at once, in
one dataset, unmarked.

**Downstream effect.** Any consumer keying on `country` splits NI arbitrarily.
Stillbound's account master did exactly that until today. This is now handled
upstream by resolving on the BT postcode instead, which is exclusive to NI, but
the source disagreement remains.

**Suggested fix.** Pick one and mark the other. A `region: "northern-ireland"`
value would be cleaner than either, and would match how the map already splits
Scotland out of the UK.

## Defect 2 — The Machrihanish Distillery is in the Ireland region

`The Machrihanish Distillery`, Campbeltown PA28 6NT, carries `region: "ireland"`.
Campbeltown is a protected Scotch whisky appellation in Argyll. The row also
made Stillbound's first NI cohort until a Scottish-postcode guard was added.

Related: `Bonnington`, Anderson Place, Edinburgh EH6 5NP, is not in the Scotland
region either. Both were corrected upstream by postcode.

## Defect 3 — Henstone Distillery has a Welsh postcode and an English address

Recorded as `Trewern, Henstone SY21 8EG`. SY21 is Welshpool, Powys — Wales.
Henstone Distillery trades from Oswestry, Shropshire. One of the two is wrong.
The Welsh-jurisdiction rule applied correctly to the data as given and put it in
Wales, which is only right if the postcode is.

## Defect 4 — a GI-protected Welsh whisky producer is missing

Single Malt Welsh Whisky took UK PGI status in July 2023. The product
specification (UK GI S0006) names five protected producers. Four are in the
dataset:

- Penderyn ✓
- Aber Falls ✓
- The Welsh Wind ✓ (listed as "The Welsh Wind")
- Dà Mhìle ✓ (listed as "Distillfa Dà Mhìle Distillery")
- **Coles — absent**

Same class as Black Velvet in Canada: the dataset carries the craft gin tail and
misses a producer on the statutory register. Wales is 20 rows, of which 11
resolved to other spirits, so a missing GI holder is a large proportion of the
actual whisky population.

## Not a defect — worth knowing

NI coverage is otherwise good. 20 rows against roughly that many operating or
announced NI distilleries. Three carried no address at all (Echlinville,
Copeland, Hinch) and two more resolved only from the region field, so
address completeness is the weak spot rather than coverage.

## Related

- `data/audit/CANADA-AUDIT.md` — the same audit for Canada, 16 Aug 2026
- `stillbound` repo, branch `gtm/ni-wales-jurisdictions` — the jurisdiction
  split and the resolution-order rules that work around defects 1 and 2
