#!/usr/bin/env python3
"""
Render the STAMPED Compliance Checklist (or any state-encoded variant) to a
vector PDF suitable for inclusion in a LaTeX paper.

Usage:
    pip install playwright
    pip install datalad
    playwright install chromium
    python render_checklist.py

The PDF will have selectable, zoomable vector text and graphics.
Edit URL and WIDTH below to taste.
"""

from playwright.sync_api import sync_playwright

# Your saved state — copy the full URL from your browser address bar after
# filling in the checklist. The encoded `state` and `responses` params preserve
# all your answers.
URL = (
    "https://checklist.stamped-principles.org/"
    "?cols=auto&sections=off"
    "&state=MTAwMDAwMDAwMTAwMDAxMDAwMDAwMDAwMDAwMDAw"
    "&responses=eyJzMF9wMF9pMCI6eyJ2YWx1ZSI6InllcyIsInJlYXNvbiI6IiJ9LCJzMF9wMF9pMSI6eyJ2YWx1ZSI6Im5vIiwicmVhc29uIjoiIn0sInMwX3AzX2kxIjp7InZhbHVlIjoieWVzIiwicmVhc29uIjoiIn0sInMwX3A2X2kwIjp7InZhbHVlIjoieWVzIiwicmVhc29uIjoiIn19"
)

WIDTH_PX = 1800          # 4 columns needs more room
OUTPUT = "figures/checklist-figure.pdf"
COLS = 5                 # 1, 2, 3, 4, or "auto"

# Light-theme override CSS — force light mode, hide UI chrome that doesn't
# belong in a paper figure, and force the column count. We use very high
# specificity (#app .cards-grid) and override BOTH possible layout mechanisms
# (CSS grid and CSS multi-column) since we don't know which the app uses.
PRINT_CSS = f"""
html {{ color-scheme: light !important; }}
.header, .toolbar, .header-actions, .cookie-consent-banner, .version-indicator,
.branding-indicator, .toast, #cookie-consent-banner,
.intro-text {{ display: none !important; }}
.reason-input, .reason-counter {{ display: none !important; }}
body {{ background: white !important; padding-top: 0 !important; }}
.container, #app {{ padding-top: 0 !important; margin-top: 0 !important; }}

/* Force N columns. Use #app .cards-grid for high specificity, and override
   both layout mechanisms in case the app uses one or the other. */
#app .cards-grid,
#app .cards-grid.cols-auto,
#app .cards-grid.cols-1,
#app .cards-grid.cols-2,
#app .cards-grid.cols-3,
#app .cards-grid.cols-4,
#app .cards-grid.cols-5 {{
    display: grid !important;
    grid-template-columns: repeat({COLS}, minmax(0, 1fr)) !important;
    column-count: {COLS} !important;
    column-gap: 1rem !important;
    gap: 1rem !important;
}}
/* Section dividers should span the full row when sections are on */
#app .section-divider {{ grid-column: 1 / -1 !important; }}
/* Prevent cards from being chopped across columns if column-count path wins */
#app .principle-card {{ break-inside: avoid !important; -webkit-column-break-inside: avoid !important; }}
"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    # Force light color scheme at the browser level
    ctx = browser.new_context(
        viewport={"width": WIDTH_PX, "height": 1000},
        color_scheme="light",
    )
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")

    # Force-set the theme attribute to light in case the app reads localStorage
    page.evaluate("document.documentElement.setAttribute('data-theme', 'light')")

    # Apply our overrides (light theme, hide chrome, force N columns)
    page.add_style_tag(content=PRINT_CSS)

    # Give the app a beat to settle after our DOM/style changes
    page.wait_for_timeout(500)

    # Measure full content height so the PDF is one tall page (no awkward breaks)
    height = page.evaluate(
        "Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
    )

    page.pdf(
        path=OUTPUT,
        width=f"{WIDTH_PX}px",
        height=f"{height + 40}px",   # tiny margin
        print_background=True,
        prefer_css_page_size=False,
    )
    browser.close()

print(f"Wrote {OUTPUT}")