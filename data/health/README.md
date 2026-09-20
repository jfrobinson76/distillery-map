# Health layer: five register facts per company behind a pin

Started 20 September 2026 (Own the Index, join 2). One row per company in the crosswalk at
high or verified confidence. Joined to pins through `data/company-crosswalk/company-crosswalk.csv`
(slug → registry + company_number). Written by `scripts/read_company_health.py`; every run
also writes a dated copy to `snapshots/`, and the diff between two snapshots is the quarterly
"Distillery Health" note.

**A value without a date is not a value.** `read_on` is the day the register was read; for
bulk files it is the file's date, not the run's.

## Fields

| Field | Meaning | UK (Companies House) | Ireland (CRO) | US (TTB) |
|---|---|---|---|---|
| `status` | live, dormant, dissolved, liquidation, administration, receivership, strike-off-listed, insolvency, unknown | register status; `dormant` when the last accounts were dormant accounts | register status | `live` if on this week's permittee list, `dissolved` if a known permit has left it |
| `status_detail` | the register's own qualifier | e.g. "active-proposal-to-strike-off" | status date, dissolved date | "new permit this week", "permit no longer listed" |
| `incorporated` | date of incorporation | yes | yes | blank |
| `last_accounts_date` | period end of the newest accounts on file | yes | yes | blank |
| `last_accounts_type` | full, small, micro, dormant, group, ... | yes | blank (not in the free file) | blank |
| `next_due` | next accounts (UK) or annual return (IE) due date | yes | yes | blank |
| `accounts_overdue` | true/false | **a register fact** | **computed**: next return date has passed | blank |
| `confirmation_overdue` | confirmation statement past due | yes | blank | blank |
| `charges_total` | registered charges, all time | yes | blank (paid document) | blank |
| `charges_outstanding` | charges not marked satisfied | yes | blank | blank |
| `charges_latest` | date the newest charge was created | yes | blank | blank |
| `sic` | trade classification | SIC codes | NACE v2 | blank |
| `source` | register page for this company | yes | yes | the TTB list page |
| `note` | why a field is blank, or a caveat | | | "a permit is permission, not a working still" |

Every other register in the crosswalk (Sirene, ABR, ASIC, NTA, Zefix, MCA, ...) gets a row
with `status: unknown` and the reason in `note`, so the gap is visible. Readers for them are
added one at a time, each with its own dated note in `docs/data-quality/`.

## What the fields do and do not say

- A dissolved company behind a pin is a strong signal the distillery has closed. It is a
  flag on the pin, not a removal; the claims process and a website check settle it.
- Dormant accounts behind a working distillery mean the site is run by another company in
  the group (Glenburgie Distillery Limited is a name-holder; Chivas Brothers runs the still).
  The crosswalk's `operator` rows carry the company that matters.
- A new charge is a capital event: a loan secured on the company, often on the stock. It is
  not distress on its own. A run of charges plus overdue accounts is.
- Overdue in the UK is Companies House's own flag. In Ireland it is our arithmetic on the
  next-return-due date and is labelled as such.
- The TTB signal is presence on a list. Permits are surrendered for many reasons; a permit
  that leaves the list is a lead for a closure, not a closure.

## Reading cadence

UK: quarterly full read (about 650 requests, inside the free tier), and the vault's filings
watcher between reads for new accounts. Ireland: monthly, from the CRO open-data zip the
vault caches. US: weekly, from the TTB list `match_ttb_permits.py --fetch` already pulls.
