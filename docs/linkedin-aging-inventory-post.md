# LinkedIn draft — global whiskey aging inventory

**Status: copy draft; current infographic rejected for LinkedIn, not published.**
Links to `distillerymap.org/whiskey-aging-inventory`.

Image: `public/share/whiskey-aging-inventory-1200.png` (1200x1200, retina) is a record of
the current web-map treatment, **not an approved social asset**. Do not post it. Regenerate
only for page testing with `npm run share-card` while a dev server is up.

## Visual review — 2026-08-03

John rejected the current square for LinkedIn. Preserve the feedback rather than iterating
now:

- the barrel mounds look crude and too obviously AI-generated;
- the country labels, ranges and provenance detail are illegible at feed size and visually
  exhausting;
- compressing a wide, detailed world map into a square creates the wrong information
  hierarchy;
- the treatment is acceptable as an explorable evidence page on DistilleryMap.org, where
  readers can inspect it, but not as the standalone LinkedIn graphic;
- a future LinkedIn redesign should be an editorial social graphic built around one clear
  idea and very little text, not a polished version of the same mound map. Keep the full
  geographic and sourcing detail on the linked page.

**Pause here.** The research and web page can stand. Do not redesign the social asset until
John explicitly resumes it. (Resumed 9 Aug 2026 — editorial big-number card in progress,
`docs/social/aging-inventory-card.html`.)

---

## Posture rule (John, 9 Aug 2026)

The LYQD lesson: a small player commissioned a report, stated a number, and stood by
it — and got quoted. We do the same. **State the exact figure (60.5m, not "about 60"),
own it, drop every "nobody knows" opener.** Invitation to correct comes from strength
("we stand by it, show us better") not from hedging. The card masthead is styled as a
report edition: "Global Whiskey Aging Inventory · August 2026".

## Japan-gap angle (added 9 Aug 2026 — John's call, current direction)

The post leads with the Japan hole instead of the global number, and the graphic is the
Stillbound-creative barrel-stack map (`docs/social/build-map-card.mjs`), Japan labelled
"NO OFFICIAL COUNT · ~2.3m derived" (flow-to-stock research, 9 Aug 2026 — see the
evidence doc Part 4E). Mechanic: DM Blair Bowman BEFORE posting, no tag in the post itself.
Blair founded Tenkyo Distillery (Bandai, Japan) and advises Japanese distilleries — he
comments on his own steam or not at all. A cold tag that gets no engagement hurts reach.

### DM draft — Blair Bowman (John sends, adapt freely)

> Hi Blair. I've been building a global estimate of whiskey aging inventory. Every
> published count assembled in one place, with the gaps left visible. It comes out
> around 60 million casks.
>
> Japan is the biggest hole on the map. No official count exists — Japan measures
> whisky at bottling, not at distillation, so maturing stock is invisible in every
> official series. The best I could do is derive a figure from NTA tax throughput:
> roughly 2.3 million casks, wide honest range 1.3 to 4 million. The only hard number
> underneath it is Suntory's Ōmi Aging Cellar at a reported ~600,000 casks.
>
> Given Tenkyo and your work with Japanese distilleries, you'd know better than anyone
> how far off that is. I'd rather be corrected before I post this than after.
>
> Full sources and caveats: distillerymap.org/whiskey-aging-inventory

### Post draft — Japan-led variant

> We went looking for global aged whiskey stock levels. No world number existed.
> So we are building one.
>
> Today it stands at 60.4 million casks, and we stand by it. Scotland counts its
> casks: 22 million. America publishes enough to derive roughly 25 million.
> Ireland has a fresh independent estimate: 4.5 million. The hardest country to
> pin down was Japan.
>
> Japan? No official count exists. Japan measures whisky at bottling, not at
> distillation, so maturing new-make is invisible in every official series. One of
> the four great whisky nations, and the only hard number anywhere is Suntory's Ōmi
> Aging Cellar: a reported 600,000 casks on one site.
>
> So I derived a national figure from tax throughput: roughly 2.3 million casks,
> with a wide honest range of 1.3 to 4 million. It rests on assumptions I'd love to
> replace with facts.
>
> Two countries hold 78% of the world's total.
>
> If you know Japan's whisky industry, or know someone who does, I'd rather publish
> your number than my derivation. Every figure, source and caveat is on the map,
> including the ones that make our own numbers look weak:
> distillerymap.org/whiskey-aging-inventory
>
> What am I getting wrong?
>
> #JapaneseWhisky #Scotch #Bourbon #IrishWhiskey

The full global-number draft below stays as the fallback / follow-up.

---

We went looking for global aged whiskey stock levels. No world number existed.
So we are building one.

Today it stands at 60.4 million casks. There is no registry, no agreed unit, no
shared reporting year. We assembled every published count, report and producer
disclosure, derived the rest with the method shown, and we stand by it.

Source-bounded range 55 to 68 million. The lower case applies every regional low
at once. Scotland and America both describe their own maturing stocks as record
highs, and they hold most of the world's.

What the published figures actually say:

**Scotland** — 22 million casks. Counted, by the Scotch Whisky Association.

**United States** — roughly 25 million barrels. Not 17 million. Kentucky's
much-quoted 17.1m is one state, and it counts all spirits, not just whiskey.
It's about two-thirds of America, not America.

**Ireland** — 4.5 million casks, per the LYQD Irish Whiskey Supply Report 2026.
Nearly nine years of global supply.

**England** — 50,000 casks. Tiny, and the only small producer that publishes
anything at all.

**Canada** — an estimated 4.5 million. Gimli publishes 1.5 million and Hiram
Walker/Pike Creek publicly reports more than 1.6 million. That 3.1 million floor
still excludes Valleyfield, Alberta and the long tail.

**Japan** — no official count. Whisky is measured at bottling, not at
distillation, so maturing stock is invisible in every official series. Derived
from tax throughput: roughly 2.3 million casks.

**China** — an estimated 750,000 casks. Laizhou's listed parent reported nearly
600,000 filled casks at the end of 2025; the national industry body had counted
450,000 across China only two years earlier.

**India** — an estimated 500,000 casks. Its malt-whisky association publishes a
300,000+ floor. Roughly 0.8% of world stock. That will look wrong to anyone who
knows the sales figures, so here is why it isn't.

Two countries hold 78% of the world's maturing whiskey. Everything else on the
map is a rounding error or a guess.

The figure that stopped me: American whiskey inventory is around 1.5 billion
proof gallons, against 103 million sold and exported a year. That is fourteen
years of supply sitting in warehouses.

Four rules I held to, because most versions of this number are inflated by the
same four mistakes:

**Money is not barrels.** Diageo reports $7.2bn of maturing whisk(e)y. That is a
balance sheet. It proves the scale of the capital tied up in maturation. It is
not a cask count.

**Capacity is not inventory.** Kavalan's widely-repeated 300,000 barrels is how
much the warehouses hold, not what is in them. Capacity is a building.

**A state is not a country.** See Kentucky, above.

**Sales are not stock.** Eight Indian brands sit in the world's twenty
best-selling whiskies — around 141 million cases a year, and McDowell's No. 1
outsells every Scotch on earth. India still holds under 1% of the world's
maturing casks. The bulk of an Indian blend is extra neutral alcohol, a
near-pure column spirit that never goes into a cask. The malt that flavours it
is frequently imported from Scotland, already aged and already counted there.
And a tropical angel's share of 8–12% a year turns whatever is laid down in
India over in two or three years rather than twelve. The Indian Malt Whisky
Association's 300,000+ barrel disclosure now gives that logic a published
floor. A bottle sold is not a cask resting.

The map is on DistilleryMap.org with every figure, every source and every
caveat, including the ones that make our own numbers look weak. It's free and
community-built.

If you work at a distillery and you know your own numbers, I would rather
publish yours than my estimate. Japan, Canada and Africa especially — those are
partial estimates or guesses and I'd like them not to be.

What am I getting wrong?

#IrishWhiskey #Scotch #Bourbon #Distilling

---

## Notes on the draft

- Leads with the gap ("nobody knows"), not the build. No mention of how the map
  was made, which is the commodity.
- Every number is one a distiller can check. The US correction is the part most
  likely to get quoted back, because the 17.1m figure is repeated everywhere.
- The ask is specific and low-friction: correct one country. That is a warmer
  route into a claim conversation than "add your distillery."
- Deliberately no cask-investment angle. That audience is noisy and it would
  drag the comments somewhere unhelpful.
- The India section is the most likely source of pushback, which is why it is
  argued rather than asserted.
- **Do not say Indian whisky is "molasses-based."** It is the obvious line and
  it is out of date. McDowell's No. 1, Royal Stag and Imperial Blue — the three
  biggest brands, over half the Indian volume — all use grain spirit, and Royal
  Stag and Imperial Blue actively market themselves *against* molasses blends.
  Molasses ENA still dominates the value tier below about ₹800 (Officer's
  Choice sits there), but as a blanket claim it is wrong and an Indian distiller
  will say so. The argument that works is about **neutral spirit not being
  cask-matured**, which is true regardless of feedstock.
- Equally, a widely-shared infographic claims "over half of India's alcohol
  sales are local single-malt whiskies." That is also wrong, in the opposite
  direction. Officer's Choice and Imperial Blue are blends, not single malts.
  Both errors are easy to make and either one loses the room.

## Follow-up posts this opens up (don't fire them all at once)

1. **The Kentucky stock-vs-flow chart** — aging inventory kept climbing through
   2024 while new fills eased off. That's the correction story, and it's a
   better second post than a first one.
2. **"14 years of supply"** — a single-stat post aimed at the trade rather than
   enthusiasts.
3. **Angel's share** — already on the roadmap in CLAUDE.md, and it pairs with
   this naturally: how much of those 60 million casks evaporates each year.
