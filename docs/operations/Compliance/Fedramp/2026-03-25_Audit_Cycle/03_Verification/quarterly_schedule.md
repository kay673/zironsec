# Quarterly Re-Verification Schedule

Date: 2026-03-25 14:30 CST

## Purpose
Conduct quarterly scans of the `src/` directory to ensure ongoing compliance with FedRAMP controls SI-7, SC-8, and AC-3. Verify SRI hashes, PII exposure, and external link security.

## Schedule
- **Q2 2026**: June 25, 2026
- **Q3 2026**: September 25, 2026
- **Q4 2026**: December 25, 2026
- **Q1 2027**: March 25, 2027

## Process
1. Run grep_search on `src/` for PII patterns.
2. Verify SRI hashes on external resources (re-generate if CDN updated).
3. Check for new external links and ensure `rel="noopener noreferrer"`.
4. Update `compliance_attainment.md` with findings.
5. If issues found, create new audit cycle in `docs/operations/Compliance/Fedramp/`.

## Responsible
Principal Security Architect

## Reminder
Set calendar alerts for each date. Integrate with CI/CD pipeline for automated scans if possible.