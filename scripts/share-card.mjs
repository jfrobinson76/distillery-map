/**
 * Screenshots the /whiskey-aging-inventory/share-card route into a 1200x1200
 * PNG for LinkedIn. Needs the dev server (or a prod build) running.
 *
 *   node scripts/share-card.mjs [port] [outfile]
 */
import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";

const port = process.argv[2] ?? "3002";
const out = process.argv[3] ?? "public/share/whiskey-aging-inventory-1200.png";
const CHROME =
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

mkdirSync(out.split("/").slice(0, -1).join("/"), { recursive: true });

execFileSync(
  CHROME,
  [
    "--headless",
    "--disable-gpu",
    "--hide-scrollbars",
    "--force-device-scale-factor=2", // retina — LinkedIn downsamples, crisper text
    "--window-size=1200,1200",
    `--screenshot=${out}`,
    `http://localhost:${port}/whiskey-aging-inventory/share-card`,
  ],
  { stdio: "inherit" }
);
console.log(`wrote ${out}`);
