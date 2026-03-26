#!/usr/bin/env python3
"""
sync_receipts.py — Fetch Gmail receipts/invoices and save as markdown files
organized by month under docs/finance/receipts/YYYY-MM/

Setup (first time only):
  1. Follow README in security/secrets/gmail/ to create credentials.json
  2. pip install -r scripts/requirements-receipts.txt
  3. python scripts/sync_receipts.py
     → Browser opens for one-time OAuth2 consent
     → token.json saved locally (gitignored)

Subsequent runs:
  python scripts/sync_receipts.py
  python scripts/sync_receipts.py --days 90   # look back further
"""

import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
RECEIPTS_DIR = REPO_ROOT / "docs" / "finance" / "receipts"
CREDENTIALS_FILE = REPO_ROOT / "security" / "secrets" / "gmail" / "credentials.json"
TOKEN_FILE = REPO_ROOT / "security" / "secrets" / "gmail" / "token.json"

# ---------------------------------------------------------------------------
# Receipt detection — subjects/senders that typically indicate a receipt
# ---------------------------------------------------------------------------
RECEIPT_SUBJECT_PATTERNS = [
    r"receipt",
    r"invoice",
    r"order confirmation",
    r"payment confirmation",
    r"subscription",
    r"you(r)? (paid|payment)",
    r"billing",
    r"your (order|purchase)",
    r"charge",
    r"transaction",
]

# Dollar/currency amounts — matches $12.34, £9.99, €20, USD 15.00 etc.
AMOUNT_PATTERN = re.compile(
    r"(?:USD?|GBP|EUR|£|\$|€)\s?(\d{1,6}(?:[.,]\d{2})?)"
    r"|(\d{1,6}(?:[.,]\d{2})?)\s?(?:USD|GBP|EUR)",
    re.IGNORECASE,
)


def extract_amount(text: str) -> str:
    """Return the first currency amount found in text, or 'Unknown'."""
    match = AMOUNT_PATTERN.search(text)
    if match:
        raw = (match.group(1) or match.group(2) or "").replace(",", ".")
        symbol = ""
        prefix = text[max(0, match.start() - 3) : match.start()]
        if "$" in prefix or "USD" in prefix.upper():
            symbol = "$"
        elif "£" in prefix or "GBP" in prefix.upper():
            symbol = "£"
        elif "€" in prefix or "EUR" in prefix.upper():
            symbol = "€"
        return f"{symbol}{raw}" if symbol else raw
    return "Unknown"


def decode_body(payload: dict) -> str:
    """Recursively extract plain-text body from a Gmail message payload."""
    mime = payload.get("mimeType", "")
    data = payload.get("body", {}).get("data", "")

    if mime == "text/plain" and data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    if mime == "text/html" and data:
        html = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        # Strip HTML tags for basic text
        return re.sub(r"<[^>]+>", " ", html)

    for part in payload.get("parts", []):
        result = decode_body(part)
        if result:
            return result

    return ""


def header(headers: list, name: str) -> str:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def safe_filename(s: str) -> str:
    return re.sub(r"[^\w\-.]", "_", s)[:60]


def save_receipt(msg_id: str, date: datetime, sender: str, subject: str, amount: str, body_snippet: str) -> Path:
    """Write receipt markdown file and return its path."""
    month_dir = RECEIPTS_DIR / date.strftime("%Y-%m")
    month_dir.mkdir(parents=True, exist_ok=True)

    vendor = sender.split("<")[0].strip().split("@")[0].strip() or "Unknown"
    filename = f"{date.strftime('%Y-%m-%d')}_{safe_filename(vendor)}_{safe_filename(amount)}-PRIVATE.md"
    filepath = month_dir / filename

    if filepath.exists():
        return filepath  # already saved, skip

    content = f"""# Receipt — {date.strftime('%B %d, %Y')}

| Field    | Value |
|----------|-------|
| **Date** | {date.strftime('%Y-%m-%d')} |
| **Vendor / From** | {sender} |
| **Subject** | {subject} |
| **Amount** | {amount} |
| **Gmail ID** | {msg_id} |

## Summary

{body_snippet[:800].strip()}

---
*Auto-imported by sync_receipts.py on {datetime.now().strftime('%Y-%m-%d')}*
"""
    filepath.write_text(content, encoding="utf-8")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Sync Gmail receipts to docs/finance/receipts/")
    parser.add_argument("--days", type=int, default=30, help="How many days back to search (default: 30)")
    parser.add_argument("--max", type=int, default=100, help="Max emails to process (default: 100)")
    args = parser.parse_args()

    # Lazy import so missing packages give a clean error
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("ERROR: Missing dependencies. Run:\n  pip install -r scripts/requirements-receipts.txt")
        sys.exit(1)

    if not CREDENTIALS_FILE.exists():
        print(f"ERROR: credentials.json not found at {CREDENTIALS_FILE}")
        print("See security/secrets/gmail/README-SETUP.md for instructions.")
        sys.exit(1)

    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())
        print(f"Token saved to {TOKEN_FILE}")

    service = build("gmail", "v1", credentials=creds)

    # Build search query
    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y/%m/%d")
    query_parts = [f"after:{since}"] + [f"subject:{p}" for p in ["receipt", "invoice", "order confirmation", "payment confirmation", "billing"]]
    query = f"({' OR '.join(query_parts[1:])})" + f" after:{since}"

    print(f"Searching Gmail for receipts in the last {args.days} days...")
    results = service.users().messages().list(userId="me", q=query, maxResults=args.max).execute()
    messages = results.get("messages", [])
    print(f"Found {len(messages)} matching emails.")

    saved = 0
    skipped = 0

    for msg_ref in messages:
        msg = service.users().messages().get(userId="me", id=msg_ref["id"], format="full").execute()
        hdrs = msg["payload"].get("headers", [])

        subject = header(hdrs, "Subject")
        sender = header(hdrs, "From")
        date_str = header(hdrs, "Date")

        # Parse date
        try:
            from email.utils import parsedate_to_datetime
            date = parsedate_to_datetime(date_str)
        except Exception:
            date = datetime.now(timezone.utc)

        # Extract body text for amount detection
        body = decode_body(msg["payload"])
        snippet = msg.get("snippet", "")
        amount = extract_amount(body) if body else extract_amount(snippet)

        path = save_receipt(msg_ref["id"], date, sender, subject, amount, body or snippet)

        if path.stat().st_mtime > (datetime.now().timestamp() - 5):
            print(f"  + Saved:   {path.relative_to(REPO_ROOT)}")
            saved += 1
        else:
            skipped += 1

    print(f"\nDone. {saved} new receipts saved, {skipped} already existed.")
    print(f"Receipts stored in: {RECEIPTS_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
