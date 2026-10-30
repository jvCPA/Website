# PRODUCT.md

> Inferred from the owner's written brief (the owner asked not to be interviewed unless blocked).
> Lines marked *(assumption)* were not stated and should be confirmed.

## What it is
A one-page personal resume site for **Jorge Vincent Coral**, an accountant who builds AI and
Google Workspace automation and turns financial data into dashboards. It runs as a Google Apps
Script web app embedded in Google Sites.

## Who it is for
- Small-business owners, accounting firms and bookkeeping practices hiring remote help
  (tax, BAS/GST, month-end, automation). *(assumption: mostly AU/US/PH clients, given BAS/GST, Xero and QBO)*
- Recruiters screening for finance + automation profiles.

## The one thing a visitor should do
Contact Jorge (the contact form), after seeing proof: real certificates and concrete automation projects.

## Surface mode
Persuade, with an Experience hero (the 360° turntable and orbiting certificates).

## Voice
Tight, plain, professional. Numbers and outcomes over adjectives. No hype, no invented facts.

## Visual authority
`DESIGN.md` (colour, type, spacing tokens). The hero uses a deeper navy stage than `night`.
One accent colour (`primary` #5266eb). Inter as the open substitute for arcadia.

## Constraints
- Runs inside Apps Script HtmlService (sandboxed iframe), embedded in Google Sites.
- Images load from jsDelivr (commit-pinned) — the page never uses the original uploads.
- Must work on phones, honour reduced motion, and degrade without WebGL.
