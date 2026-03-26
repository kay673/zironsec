# Gmail Receipt Sync — Setup Guide

## 1. Create a Google Cloud Project & Enable Gmail API

1. Go to https://console.cloud.google.com/
2. Create a new project (e.g. "ZironSec Tools")
3. Navigate to **APIs & Services → Library**
4. Search for **Gmail API** → Enable it
5. Navigate to **APIs & Services → OAuth consent screen**
   - User type: **External**
   - App name: "ZironSec Receipt Sync"
   - Support email: your Gmail address
   - Add scope: `https://www.googleapis.com/auth/gmail.readonly`
   - Add yourself as a **Test user**
6. Navigate to **APIs & Services → Credentials**
   - Click **Create Credentials → OAuth Client ID**
   - Application type: **Desktop app**
   - Name: "ZironSec Receipt Sync"
   - Click **Create** → **Download JSON**
7. Save the downloaded file as `credentials.json` in THIS folder

## 2. Install Python Dependencies

```bash
pip install -r scripts/requirements-receipts.txt
```

## 3. First-Time Auth (one-time only)

```bash
python scripts/sync_receipts.py
```

A browser window will open asking you to sign in and grant read-only Gmail access.
After approval, a `token.json` is saved here (gitignored — never committed).

## 4. Run Regularly

From VS Code: **Terminal → Run Task → Sync Gmail Receipts (last 30 days)**

Or from the terminal:
```bash
python scripts/sync_receipts.py          # last 30 days
python scripts/sync_receipts.py --days 90  # last 90 days (for backfill)
```

## Security Notes

- `credentials.json` and `token.json` are gitignored — never commit them
- The script requests **read-only** Gmail access only
- Receipts saved as `*-PRIVATE.md` files, also gitignored from public view
