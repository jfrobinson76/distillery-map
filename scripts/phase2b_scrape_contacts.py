"""
Phase 2B — Step 3: Contact scrape for IE + UK + Scotland live entities.

For each LIVE entity in the priority regions, fetches:
  - Homepage: LinkedIn company URL, generic email
  - /contact or /contact-us: email, phone, contact person name
  - /about or /about-us: founder/MD/distiller name + role

Stores results in the contacts table.
Rate limit: 1 req/sec. Skips already-scraped entities.
"""

import logging
import re
import sqlite3
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "stillbound_intelligence.db"

HEADERS = {
    "User-Agent": "Stillbound-Research/1.0 (john@stillbound.ai)",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}
TIMEOUT = 12
RATE_LIMIT = 1.2  # seconds between requests

CONTACT_PATHS = ["/contact", "/contact-us", "/contact-us/", "/contact/", "/contactus"]
ABOUT_PATHS = ["/about", "/about-us", "/about-us/", "/about/", "/our-story", "/team"]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
LINKEDIN_RE = re.compile(r"https?://(?:www\.)?linkedin\.com/company/[^\s\"'<>]+", re.I)
TEL_RE = re.compile(r"(?:tel:|callto:)([\d\s\+\-\(\)]+)", re.I)

# Role keywords for person detection
ROLE_KEYWORDS = [
    "founder", "co-founder", "distiller", "head distiller", "master distiller",
    "managing director", "md", "ceo", "owner", "director", "general manager",
]


def base_url(website: str) -> str:
    parsed = urlparse(website)
    return f"{parsed.scheme}://{parsed.netloc}"


def fetch_page(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                            allow_redirects=True)
        if resp.status_code >= 400:
            return None
        time.sleep(RATE_LIMIT)
        return BeautifulSoup(resp.text, "lxml")
    except Exception as exc:
        log.debug("Fetch failed %s: %s", url, exc)
        time.sleep(RATE_LIMIT)
        return None


def extract_emails(soup: BeautifulSoup, url: str) -> list[str]:
    emails = set()
    # mailto links
    for a in soup.find_all("a", href=True):
        if "mailto:" in a["href"].lower():
            email = a["href"].replace("mailto:", "").split("?")[0].strip().lower()
            if EMAIL_RE.match(email) and not email.startswith("noreply"):
                emails.add(email)
    # inline text
    for email in EMAIL_RE.findall(soup.get_text()):
        email = email.lower()
        if not email.startswith("noreply") and not email.endswith(
            (".png", ".jpg", ".gif", ".css", ".js")
        ):
            emails.add(email)
    return list(emails)


def extract_linkedin(soup: BeautifulSoup) -> str | None:
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if LINKEDIN_RE.match(href):
            return href.rstrip("/")
    return None


def extract_phone(soup: BeautifulSoup) -> str | None:
    # tel: links
    for a in soup.find_all("a", href=True):
        m = TEL_RE.match(a["href"])
        if m:
            return m.group(1).strip()
    return None


def extract_person(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """Return (name, role) for the most prominent leadership person found."""
    text = soup.get_text(separator=" ", strip=True)
    for role in ROLE_KEYWORDS:
        # Look for "Name, Role" or "Role: Name" patterns near role keyword
        pattern = re.compile(
            rf"([A-Z][a-z]+ [A-Z][a-z]+),?\s*(?:[-–]?\s*)?{re.escape(role)}",
            re.I,
        )
        m = pattern.search(text)
        if m:
            return m.group(1).strip(), role.title()
        # Reverse: "Role: Name"
        pattern2 = re.compile(
            rf"{re.escape(role)}[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)",
            re.I,
        )
        m2 = pattern2.search(text)
        if m2:
            return m2.group(1).strip(), role.title()
    return None, None


def scrape_entity(source_id: str, website: str) -> dict:
    """Scrape contact info from an entity's website. Returns dict of found data."""
    result = {
        "source_id": source_id,
        "emails": [],
        "linkedin": None,
        "phone": None,
        "contact_name": None,
        "contact_role": None,
    }

    site_base = base_url(website)

    # Homepage
    soup = fetch_page(website)
    if soup:
        result["emails"].extend(extract_emails(soup, website))
        result["linkedin"] = extract_linkedin(soup)
        result["phone"] = extract_phone(soup)

    # Contact page
    for path in CONTACT_PATHS:
        contact_url = urljoin(site_base, path)
        soup = fetch_page(contact_url)
        if soup:
            result["emails"].extend(extract_emails(soup, contact_url))
            if not result["phone"]:
                result["phone"] = extract_phone(soup)
            if not result["contact_name"]:
                name, role = extract_person(soup)
                result["contact_name"] = name
                result["contact_role"] = role
            break

    # About page (for person extraction)
    if not result["contact_name"]:
        for path in ABOUT_PATHS:
            about_url = urljoin(site_base, path)
            soup = fetch_page(about_url)
            if soup:
                name, role = extract_person(soup)
                if name:
                    result["contact_name"] = name
                    result["contact_role"] = role
                    break

    # Deduplicate emails
    result["emails"] = list(dict.fromkeys(result["emails"]))
    return result


def main() -> None:
    if not DB_PATH.exists():
        log.error("DB not found — run Phase 2 + Phase 2B Steps 1-2 first")
        return

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL")

    # Only scrape LIVE priority-region entities not yet scraped
    already_scraped = {
        r[0] for r in con.execute(
            "SELECT DISTINCT entity_source_id FROM contacts WHERE source = 'website_scrape'"
        )
    }

    rows = con.execute(
        """SELECT e.source_id, e.website FROM entities e
           WHERE e.website_status = 'LIVE'
           AND e.region IN ('ireland', 'scotland', 'uk')
           AND e.website IS NOT NULL"""
    ).fetchall()

    rows = [(sid, url) for sid, url in rows if sid not in already_scraped]
    log.info("%d priority-region LIVE entities to scrape", len(rows))

    emails_found = contacts_found = linkedin_found = 0

    for i, (source_id, website) in enumerate(rows, 1):
        log.info("[%d/%d] %s — %s", i, len(rows), source_id, website)
        result = scrape_entity(source_id, website)

        # Store emails
        for email in result["emails"]:
            con.execute(
                """INSERT OR IGNORE INTO contacts
                   (entity_source_id, contact_email, source)
                   VALUES (?, ?, 'website_scrape')""",
                (source_id, email),
            )
            emails_found += 1

        # Store LinkedIn as a contact entry
        if result["linkedin"]:
            con.execute(
                """INSERT OR IGNORE INTO contacts
                   (entity_source_id, contact_name, contact_role, source)
                   VALUES (?, ?, 'linkedin_url', 'website_scrape')""",
                (source_id, result["linkedin"]),
            )
            linkedin_found += 1

        # Store named contact
        if result["contact_name"]:
            con.execute(
                """INSERT OR IGNORE INTO contacts
                   (entity_source_id, contact_name, contact_role, source)
                   VALUES (?, ?, ?, 'website_scrape')""",
                (source_id, result["contact_name"], result["contact_role"]),
            )
            contacts_found += 1

        if i % 20 == 0:
            con.commit()
            log.info("  Progress: %d emails, %d named contacts, %d LinkedIn URLs",
                     emails_found, contacts_found, linkedin_found)

    con.commit()
    con.execute(
        "INSERT INTO enrichment_log (source, rows_updated, notes) VALUES (?, ?, ?)",
        ("phase2b_scrape_contacts", len(rows),
         f"emails={emails_found}, named_contacts={contacts_found}, linkedin={linkedin_found}"),
    )
    con.commit()
    con.close()

    log.info("Contact scrape complete:")
    log.info("  Emails found:    %d", emails_found)
    log.info("  Named contacts:  %d", contacts_found)
    log.info("  LinkedIn URLs:   %d", linkedin_found)


if __name__ == "__main__":
    main()
