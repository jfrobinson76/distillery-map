/**
 * Ping IndexNow with the country pages that have reviewed intro copy.
 *
 * IndexNow is supported by Bing, Yandex, Seznam and Naver — one POST tells all
 * of them a URL changed, instead of waiting for a crawl. It is free and has no
 * per-day quota worth worrying about.
 *
 * Google does NOT participate in IndexNow, and has no equivalent for ordinary
 * pages. Its Indexing API is restricted to JobPosting and BroadcastEvent
 * schema, and the old sitemap ping endpoint was retired in 2023. For Google the
 * only levers are the sitemap and Search Console's manual "Request indexing"
 * button, which is rate-limited to a handful of URLs a day. Don't add a Google
 * call here expecting it to work.
 *
 *   node scripts/indexnow.mjs           # dry run, prints what it would send
 *   node scripts/indexnow.mjs --send    # actually submits
 */
import { countryCopy } from "../src/lib/country-copy.ts";

const HOST = "distillerymap.org";
const KEY = "4c36c22c553fc17ec8bc61cded0a4a65";

const urlList = [
  `https://${HOST}/`,
  `https://${HOST}/distilleries`,
  ...Object.keys(countryCopy).map((slug) => `https://${HOST}/distilleries/${slug}`),
];

const send = process.argv.includes("--send");

console.log(`${urlList.length} URLs (${Object.keys(countryCopy).length} country pages with copy):`);
for (const u of urlList) console.log(`  ${u}`);

if (!send) {
  console.log("\nDry run. Re-run with --send to submit to IndexNow.");
  process.exit(0);
}

const res = await fetch("https://api.indexnow.org/indexnow", {
  method: "POST",
  headers: { "Content-Type": "application/json; charset=utf-8" },
  body: JSON.stringify({
    host: HOST,
    key: KEY,
    keyLocation: `https://${HOST}/${KEY}.txt`,
    urlList,
  }),
});

// 200 = accepted, 202 = accepted but key still being validated. Both are fine.
console.log(`\nIndexNow responded ${res.status} ${res.statusText}`);
if (!res.ok && res.status !== 202) {
  console.error(await res.text());
  process.exit(1);
}
