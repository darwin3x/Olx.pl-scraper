# OLX Monitor

A lightweight, real-time listing monitor for OLX.pl — a desktop app that watches any OLX search URL and instantly surfaces new listings with photos, prices and one-click access.

Built for people hunting good deals: instead of manually refreshing search results, the app polls the page in the background, detects listings you haven't seen yet, and pushes them into a clean, dark-themed feed with a sound alert.

## Features

- **Real-time monitoring** — polls the chosen OLX search page every 10 seconds in a background thread, so the UI stays responsive.
- **New-listing detection** — keeps track of already-seen listings and only displays the ones that appear during the session.
- **Rich listing cards** — each card shows the photo, title, price, location and direct link to the offer.
- **One-click open** — a single click (or the rounded "Otwórz w przeglądarce" button) launches the listing in your default browser.
- **Sound alerts** — a beep plays whenever a new listing is detected, so you never miss a deal.
- **Polished dark UI** — custom dark theme with hover effects, smooth mouse-wheel scrolling and image placeholders for offers without photos.

## Tech stack

| Area | Technology |
|---|---|
| Language | Python 3 |
| Scraping | `requests`, `BeautifulSoup` |
| GUI | `tkinter` (multi-threaded, `after()`-based UI updates) |
| Imaging | `Pillow` (thumbnailing, placeholders) |
| Alerts | `winsound` (Windows) |

## Installation

```bash
git clone https://github.com/<your-username>/olx-scraper.git
cd olx-scraper
pip install -r requirements.txt
```

> Windows only (uses `winsound` and `start` to open listings).

## Usage

```bash
python olx.py
```

1. Paste any OLX search URL when prompted, e.g.
   `https://www.olx.pl/elektronika/q-lenovo/?search%5Border%5D=filter_float_price:asc`
2. The app immediately loads the current listings as a baseline.
3. Every 10 seconds it re-checks the page — new offers pop up at the top with a sound alert.

## How it works

1. The user provides an OLX search URL at startup.
2. A background thread fetches the page with `requests` and parses listing cards via CSS selectors (`[data-cy="l-card"]`, title, price and location test IDs).
3. Newly detected links are compared against a set of already-seen listings.
4. New offers are downloaded as thumbnails, wrapped into listing cards and inserted into the scrollable feed on the main thread (`parent.after(...)`) to keep tkinter thread-safe.
5. A beep notifies the user, and each card's button opens the original listing in the browser.

## Project structure

```
olx-scraper/
├── olx.py            # application entry point (scraper + GUI)
├── requirements.txt  # Python dependencies
└── README.md
```

## Disclaimer

This project is for personal, educational use. Please respect OLX's terms of service and keep the polling interval reasonable.
