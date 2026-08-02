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
  austria:
    "Austrian distilleries are mostly attached to something else — an orchard, a farm, a guesthouse — rather than standing as businesses in their own right. The signature spirit is fruit: Wachau apricot brandy carries protected status, and Styria supplies much of the rest, down to rowanberry and stone pine. A label reading Brand means the spirit was fermented and distilled from the named fruit; Geist means the fruit was steeped in neutral alcohol instead. Whisky exists here, but it's a recent and small share of what follows.",
  india:
    "India drinks more whisky by volume than any other country, though much of what sells there is distilled from molasses and wouldn't meet the European definition of whisky at all. The single malt side is far smaller and matures at speed — tropical heat drives an angel's share of eight to twelve per cent a year, against roughly two in Scotland. A five-year-old Indian malt is not a young whisky in any meaningful sense. Both worlds appear below, alongside the rum and country-spirit producers that make up the bulk of the count.",
  belgium:
    "Genever is the reason this list takes the shape it does. Gin's older ancestor holds a protected designation, made almost entirely here and in the Netherlands, and it's built on malt wine rather than neutral spirit — closer to a light whisky than to a London Dry. Hasselt has long been the centre of it. The brewing industry shows up too, in distillers turning beer into eau-de-vie and, lately, single malt. Old jenever houses and very new arrivals sit side by side below.",
  switzerland:
    "Two bans shape this list. Grain couldn't legally be turned into spirit in Switzerland until 1999, so every Swiss whisky on this map postdates that year. Absinthe was outlawed from 1910 until 2005, despite Val-de-Travers being the valley where it was invented — and where it quietly kept being made throughout. The steady business underneath both has always been fruit: Kirsch around Zug, Williams pear in the Valais.",
  "south-africa":
    "Brandy is the backbone, and the rules are stricter than most drinkers expect — potstill brandy here must be copper-pot distilled and aged at least three years in oak. The Western Cape wine industry feeds it, which is why the distilleries cluster where the vineyards do. Rougher traditions sit underneath: witblits and mampoer, unaged grape and fruit spirits made on farms long before anyone thought to regulate them. Gin and whisky producers account for most of the newer names here.",
  spain:
    "Brandy de Jerez is aged the way sherry is — in a solera, where casks are partly drawn and refilled so the spirit never carries a single vintage. It has to happen inside the Jerez triangle, in barrels that previously held sherry. Menorca has its own protected gin, left over from the British navy's years on the island. The gin-tonic habit did the rest, and a good share of what's listed is recent gin rather than old brandy.",
};
