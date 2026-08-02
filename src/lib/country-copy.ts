/**
 * Per-country editorial copy for country pages, keyed by slug.
 * Written per docs/editorial-voice.md, cleared by .claude/commands/review-country-copy.md.
 *
 * Deliberately excludes the live distillery count — that's rendered separately
 * from entry.count so this text never goes stale as the map grows. Trend
 * language ("more than doubled") is fine; hardcoded digits are not.
 *
 * Countries not listed here fall back to the generic template in page.tsx.
 */
export const countryCopy: Record<string, string> = {
  ireland:
    "A generation ago, only four distilleries were left standing in the whole country. Licenses started going out again around 2013, and the count climbed from that handful to dozens within a decade — survivors and newcomers both listed below. Triple distillation is Ireland's traditional style, though it's not a legal requirement. The actual rule is that Irish whiskey must be distilled and aged on the island, Northern Ireland included, for at least three years.",
  scotland:
    "The Scotch Whisky Association counts closer to 150 active malt distilleries across Scotland. This map runs higher because it also tracks grain distilleries, tasting rooms, and a handful of mothballed sites still in the data. Five regions carry the real variation, and none tells a starker story than Campbeltown — once a boomtown, now down to a handful of stills. Speyside, by contrast, holds the densest concentration of distilleries in the country. The list below spans big Speyside names and small independent operations you won't find in a whisky glossary.",
  "united-states":
    "Most of that count is recent: state licensing rules only loosened enough for small producers to get a federal permit in the early 2010s. Kentucky still makes most of the country's bourbon, but the label was never a Kentucky exclusive — bourbon can legally be distilled anywhere in the US. What's below spans legacy bourbon houses and single-still craft operations in states that had no commercial distillery a decade ago.",
  japan:
    "For most of the twentieth century, only two distilleries mattered here: Suntory's Yamazaki, opened in 1923, and Nikka's Yoichi, founded eleven years later. That stayed a quiet, domestic story for Japanese whisky until 2014, when a Jim Murray award for a Yamazaki release sent global demand soaring. Aged stock couldn't keep up, and several well-known age-statement bottlings disappeared from shelves for years. The list below spans those two founding distilleries and the craft producers that followed once the category had proven it could sell.",
  germany:
    "Most of these aren't whisky distilleries. The count here is built on fruit — Obstbrand, Kirschwasser, Williams pear — from small farm operations concentrated in Baden-Württemberg and Bavaria. A state spirits monopoly governed those producers for most of a century and only wound up in 2018, which is why so many of them are simultaneously very old and commercially quite new. What's listed below leans regional and small rather than export brand.",
  "united-kingdom":
    "Scotland has its own page here, so this figure covers the whole UK — and most of the recent growth in it is English and Welsh. In 2009 the minimum still size for a distiller's licence was scrapped, and the gin boom that followed put a working still into a lot of railway arches. English single malt is the slower story: commercial whisky distilling lapsed for most of the twentieth century and only restarted in the 2000s. Outside the Scottish entries, the list below is gin-heavy.",
  france:
    "France buys more Scotch by volume than any other country, and distills almost none of what's counted here. The appellation spirits dominate instead — Cognac and Armagnac, each tied by law to a defined area, defined grapes and a defined still. Calvados does the same job for apple brandy in Normandy. Expect mostly houses working inside those rules, alongside a French single malt scene that's still young.",
  australia:
    "Tasmania banned small stills in 1839 and didn't lift the ban until 1992. Most of the Australian whisky industry dates from that single licence. Maturation runs fast — small casks, warm summers, and a lot of ex-fortified-wine wood out of Rutherglen and the Barossa. Gin has since overtaken whisky on producer numbers and accounts for a large share of this count. Both are represented below, and it skews small and independent.",
  italy:
    "Grappa explains most of this. It's distilled from vinaccia — the skins, pips and stems left after pressing wine — so Italy's distilling map tracks its wine map, the north and northeast especially. The category was leftovers until producers started bottling single-grape grappa in the 1970s and pricing it accordingly. Turin's vermouth houses and the amaro makers account for much of the rest.",
  canada:
    "Canadian whisky is still called rye whether or not much rye is in it — a habit from the 1800s, when a small rye addition was enough to mark out a mash. The rules are unusually permissive. Three years in wood is the floor, base and flavouring whiskies are distilled separately, and up to 9.09 per cent of the bottle can legally be something else. Most of the recent additions below are craft operations in British Columbia and the Prairies.",
};
