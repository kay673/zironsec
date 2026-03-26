# 📝 Report Content (The ZironSec Standard)
# 🛡️ ZironSec Advisory: Zero Trust & Supply Chain Privacy

Prepared by: Kay Stephen, MBA | Principal Security Architect
Classification: [PRIVATE] - ZironSec Internal Proprietary
Date: 2026-03-25 14:30 CST
Client: ZironSec LLC
Scope: `src/Website/index.html`, `src/` directory scan, and compliance posture for Tier 3 enterprise sales

---

## Executive Summary

ZironSec’s corporate website demonstrates strong design intent and brand positioning, but a Tier 3 enterprise CISO will escalate the following key risk domains:

1. Supply-chain risk from remote dependencies without SRI integrity checks.
2. Data privacy exposure from publicly visible contact identifiers and local `.env` artifacts.
3. Identity workflow and booking channel risk in the absence of a hardened Calendly/contact handoff.

This advisory defines findings, impact, and remediation as a FedRAMP-ready compliance narrative.

---

## 1. Supply Chain & Subresource Integrity (SRI) Audit

### 1.1 Findings
- `index.html` uses remote static assets:
  - `<script src="https://cdn.tailwindcss.com"></script>`
  - `<link href="https://fonts.googleapis.com/css2?family=Inter..." rel="stylesheet">`
  - Google Fonts resources loaded from `fonts.gstatic.com`
  - External background image `https://www.transparenttextures.com/patterns/carbon-fibre.png`
- No `integrity` or `crossorigin` attributes are present on remotely loaded resources.
- Clients now enforce CSP in HTML, but SRI deficiency remains a standalone supply chain weakness.

### 1.2 Risk Rationale (Tier 3)
- Third-party CDN compromise enables injection of arbitrary JS/CSS in the served page.
- Attack vector: DNS spoofing or package-hosting tampering converted into site-wide breach.
- Enterprise requirement: “Immutable supply chain sign-off and verified integrity for all web dependencies”—currently unmet.

### 1.3 Remediation
- Persistently self-host all required resources; remove direct CDN dependency.
- For remaining remote resources, add:
  - `integrity="sha384-<hash>..."`
  - `crossorigin="anonymous"`
- Validate remote resources automatically via build pipeline:
  - `npm run lint:stale-assets` or equivalent.
- Maintain an internal vendor whitelist and audit artifacts for each release.

---

## 2. Data Privacy & PII Leak Audit

### 2.1 Findings
- Static PII in repo:
  - `src/Website/.env`: `VITE_OFFICE_PHONE="(281) 766-7909"`, `VITE_FOUNDER_EMAIL="kay@zironsec.com"`
- Hardcoded contact details in HTML:
  - `mailto:support@zironsec.com` in `index.html`, `404.html`, and `maintenance.html`
  - `tel:2817667909` in `index.html`
- No obvious API keys were discovered in scanned patterns for common tokens.

### 2.2 Privacy-by-Design Analysis
- GDPR/CCPA expect minimal exposure of personal identifiers without purpose and consent.
- Hardcoded contacts increase scraping and spam risk; lacks defense-in-depth.
- Storing contact descriptors in `.env` within source tree may leak if miscommitted.

### 2.3 Remediation
- Replace hardcoded contact links with secure outbound form gateway:
  - Contact form → backend service → ticketing/email while keeping emails hidden from bots.
- `.env` handles secrets and PII strictly in secure vault/CD pipeline (HashiCorp Vault / Azure Key Vault / AWS Secrets Manager).
- Add `docs/operations/privacy-policy` with explicit data processing and retention statements.
- Add in `README` and new SOP: `.env` variables are never committed and are rotated on every repo root access.

---

## 3. Identity & Zero Trust Workflow Audit

### 3.1 Findings
- `Book Strategy Call` points to public Calendly URL.
- `Contact` link actions are direct `mailto:` and `tel:`.
- No intermediate authentication, request validation or audit trail on entry.

### 3.2 Risks
- External booking flows are subject to automation/spam and possible credential phishing.
- Lack of webhook validation could allow bogus event creation if Calendly callbacks are consumed without signature checks.
- Direct email/phone exposure encourages unsolicited risk to staff and escalates social engineering vector.

### 3.3 Recommended Controls
- Use hardened Calendly widget integration with verification of `x-calendly-signature` callbacks.
- Build a booking proxy endpoint:
  1. User intent capture (`/book-call`) + CAPTCHA + rate limit.
  2. Honeypot and bot detection.
  3. Forward to Calendly via server-initiated API rather than direct link.
- Replace open `mailto:` with API contact form and logged request pipeline.
- Add auditing/alerting when booking volume spikes and enforce adaptive MFA for team confirmations.

---

## 4. Compliance Actions Implemented
- `index.html` updated with:
  - `meta name="description"` (160-character AI-SecOps narrative)
  - `meta name="robots" content="index, follow"`
  - OpenGraph tags for LinkedIn previews
  - Twitter Card metadata
  - strict CSP meta to limit source domains
  - `rel="noopener noreferrer"` on all `target="_blank"`

---

## 5. Next Steps for FedRAMP Alignment
- Onboard security controls into KM: SC-6, SA-9, SI-3, SI-7 (supply chain) as mapping matrix.
- Run dependency SBOM and static SRI verification per STIG.
- Integrate with DevSecOps pipeline (policy as code) and certify via independent audit.
- Build a governance document in `docs/operations/Compliance/Fedramp` for continuous monitoring.

---

## Appendix
- Sources: `src/Website/index.html`, `docs/**/*.md`, `src/**/*.env` patterns.
- Date of assessment: 2026-03-25.
- Auditor: Principal Security Architect, ZironSec.
