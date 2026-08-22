import fs from 'node:fs';
import path from 'node:path';

const file = path.resolve(process.cwd(), 'public/data/distilleries.geojson');
const data = JSON.parse(fs.readFileSync(file, 'utf8'));
const features = data.features || [];

function countsBy(key) {
  const counts = new Map();
  for (const feature of features) {
    const value = String(feature.properties?.[key] ?? '').trim() || '(blank)';
    counts.set(value, (counts.get(value) ?? 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

function printTable(title, entries, limit = Infinity) {
  console.log(`\n${title}`);
  for (const [name, count] of entries.slice(0, limit)) console.log(`${count}\t${name}`);
}

const duplicateSlugs = new Map();
for (const feature of features) {
  const slug = String(feature.properties?.slug ?? '').trim();
  if (!slug) continue;
  duplicateSlugs.set(slug, (duplicateSlugs.get(slug) ?? 0) + 1);
}

const roles = countsBy('entity_role');
const countries = countsBy('country');
const regions = countsBy('region');
const requestedCountries = ['China', 'United States', 'Poland', 'Czech Republic', 'Slovakia', 'Hungary', 'Romania', 'Ukraine', 'Bulgaria', 'Croatia', 'Serbia', 'Slovenia', 'Bosnia and Herzegovina', 'Moldova', 'Lithuania', 'Latvia', 'Estonia'];

console.log(`PUBLISHED_FEATURES\t${features.length}`);
console.log(`UNIQUE_COUNTRIES\t${countries.filter(([country]) => country !== '(blank)').length}`);
console.log(`BLANK_COUNTRY\t${countries.find(([country]) => country === '(blank)')?.[1] ?? 0}`);
console.log(`DUPLICATE_SLUGS\t${[...duplicateSlugs.values()].filter((count) => count > 1).length}`);
console.log(`NON_DISTILLING_ENTITY_ROLES\t${features.filter((f) => String(f.properties?.entity_role ?? '').trim()).length}`);

printTable('COUNTRY_COUNTS_TOP_40', countries, 40);
printTable('REGION_COUNTS', regions);
printTable('ENTITY_ROLE_COUNTS', roles);
printTable('SOURCE_COUNTS', countsBy('source'));
printTable('REQUESTED_COUNTRY_COUNTS', requestedCountries.map((country) => [country, countries.find(([name]) => name === country)?.[1] ?? 0]));

const countryRegionCounts = new Map();
for (const feature of features) {
  const country = String(feature.properties?.country ?? '').trim() || '(blank)';
  const region = String(feature.properties?.region ?? '').trim() || '(blank)';
  const key = `${country} | ${region}`;
  countryRegionCounts.set(key, (countryRegionCounts.get(key) ?? 0) + 1);
}
printTable('UNITED_STATES_COUNTRY_REGION_BREAKDOWN', [...countryRegionCounts.entries()].filter(([key]) => key.startsWith('United States | ')).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
printTable('USA_REGION_COUNTRY_BREAKDOWN', [...countryRegionCounts.entries()].filter(([key]) => key.endsWith(' | usa')).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));

for (const country of ['United States', 'Germany', 'China', 'Poland', 'Romania', 'Ukraine', 'Croatia', 'Slovakia']) {
  const sourceCounts = new Map();
  for (const feature of features) {
    if (feature.properties?.country !== country) continue;
    const source = String(feature.properties?.source ?? '').trim() || '(blank)';
    sourceCounts.set(source, (sourceCounts.get(source) ?? 0) + 1);
  }
  printTable(`SOURCES_IN_${country.toUpperCase().replaceAll(' ', '_')}`, [...sourceCounts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

console.log('\nCHINA_RECORDS');
for (const feature of features.filter((f) => f.properties?.country === 'China').sort((a, b) => String(a.properties?.name ?? '').localeCompare(String(b.properties?.name ?? '')))) {
  const p = feature.properties || {};
  console.log(`${p.source}\t${p.name}\t${p.address}\t${p.slug}`);
}

const propertyNames = new Map();
for (const feature of features) {
  for (const key of Object.keys(feature.properties || {})) propertyNames.set(key, (propertyNames.get(key) ?? 0) + 1);
}
printTable('PROPERTY_FIELD_PRESENCE', [...propertyNames.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
