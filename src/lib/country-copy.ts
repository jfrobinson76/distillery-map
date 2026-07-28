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
};
