# Interactive dashboard

**Live: https://claude.ai/code/artifact/4b343ae2-f31e-4c63-ae51-77ef521a5498**

`index.html` is the source for the live page above — self-contained, no build step, no dependencies beyond a Google Fonts link (Archivo, IBM Plex Sans, IBM Plex Mono). Open it directly in a browser (`open dashboard/index.html`) to view it locally, or click the live link.

Every number on the page is copy-pasted from `analysis/findings.md`, which is itself sourced from real query output in `sql/`. Nothing here is randomly generated or placeholder — if a number changes upstream (a query gets rerun, a finding gets corrected), this file needs a matching edit, same as `analysis/make_charts.py`.

## What's on it

Four sections matching the customer journey this whole repo is structured around: acquisition (GA4 funnel, channel revenue), delivery (lateness by state and by seller-customer distance), post-purchase (the delay-vs-review-score finding the PRD is built on, repeat-purchase, freight economics), and a "rigor" section summarizing the four-lens critique in `analysis/limitations-and-alternative-views.md`.

## Design notes

Built following this session's `artifact-design` and `dataviz` skill guidance: a real token system (not a templated look), the same validated accessible color palette used in `analysis/make_charts.py`'s static PNGs (so the interactive and static charts read as one system), full light/dark theme support, and inline hover tooltips on every bar. Charts are hand-built SVG, not a charting library — the CSP an Artifact runs under doesn't allow arbitrary third-party JS.

One real bug worth noting for anyone editing this file: an early version had no `<meta charset="utf-8">` tag, which silently turned every em-dash and arrow character into mojibake (`â€"`, `viewâ†'cart`). If you see garbled punctuation after an edit, check that tag first before suspecting the content itself.
