# EDGAR Pipeline Project

This is a Python coding project developed for extracting and parsing financial statement data directly from the SEC's EDGAR Database via the Company Facts API, presented through an interactive Streamlit app.

**Live app:** [aperture-insights-edgar-pull.streamlit.app](https://aperture-insights-edgar-pull.streamlit.app/)

> **Disclaimer:** The companies referenced in this repository's watchlist are not specific investment recommendations. This project exists to illustrate the functionality of the SEC's Company Facts API in extracting financial information to conduct financial statement analysis.

## Why this project exists

Every public company filing with the SEC tags its financial statement data via XBRL. I've previously worked on IFRS and US GAAP SEC financial reporting projects as a CPA where I've prepared disclosures and tagged XBRL data for submission to EDGAR; however, this project retrieves the 10-K, 10-Q, 6-K, 20/40-F report data from the investing public side.

This project pulls that data directly from SEC's public API and flattens it into clean, analysis-ready `pandas` DataFrames — with a particular focus on distinguishing foreign private issuers (FPIs) from domestic filers. US-based companies, domestic filers, issue their financial statements under US GAAP, while many FPIs file under IFRS, with different XBRL taxonomies and tagging conventions entirely.

## How it works

- **Defines the Companies on the Investment Watchlist** by listing out the Company Name, CIK, Ticker, and categorizing them as either Domestic or FPI based on their headquarters domiciliation.
- **Pulls raw XBRL company facts** for any public company by referencing the company's CIK (Central Index Key) via the Company Facts API.
- **Flattens nested JSON Company Facts** into tidy DataFrames for all tagged financial statement line items.
- **Lists all available GAAP concepts** a company has reported to explore the available financial statement line before querying.

## The Streamlit App

The pipeline above is wrapped in an interactive Streamlit interface so the data is usable without touching the code:

- Select any company from the watchlist via dropdown
- Select a financial metric (Total Assets, Total Equity, Liabilities, Total Income, Total Revenue)
- Pull live data directly from EDGAR with one click
- View the latest reported figure, the full historical data table (form type, fiscal year, period, value, accession number), and a trend chart across annual filings

The app also surfaces the accounting logic under the hood — each result is captioned with the filer type (Domestic/FPI), the detected accounting standard (US-GAAP/IFRS), and the specific XBRL tag used to retrieve the value.

## Known Issues & Limitations

**Foxconn (Hon Hai Precision Industry, HNHPF)** — Financials are published through the company's own investor relations portal as a PDF, not filed with the SEC as a 10-K or 20-F. No CIK-based XBRL data exists to pull. Currently omitted from the active watchlist.

**Infineon Technologies (IFNNY)** — Has a valid SEC CIK and has filed 20-F annual reports, but the Company Facts API returns no data. The company's financials do not appear to be tagged in XBRL format, which the `companyfacts` endpoint requires. Omitted from the active watchlist pending further investigation.

**STMicroelectronics (STM)** — Confirmed to file with the SEC (unlike the two above), but the pipeline's initial guess at the revenue tag name (`"Revenues"`) did not match STM's actual XBRL tag. Root cause not yet confirmed — deferred to keep the project moving.

**Vertiv (VRT) — resolved.** Total Revenue initially returned `$0` due to XBRL tag variability: Vertiv tags revenue as `RevenueFromContractWithCustomerExcludingAssessedTax` (the ASC 606 contract-revenue element most domestic filers adopted post-2018), not the older, more generic `Revenues` tag the pipeline originally checked for. Fixed by trying a prioritized list of candidate tags per metric instead of a single hardcoded tag:

```python
METRIC_MAPPING = {
    "Total Revenue": {
        "us-gaap": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "ifrs-full": ["Revenue"]
    },
    # ... same pattern for other metrics
}
```

**Takeaway:** XBRL tagging is not perfectly standardized across filers, even within the same accounting standard. A tool that assumes one canonical tag name per financial concept will silently produce wrong (not missing) data for companies that tag differently — arguably more dangerous than an outright error.

## Setup

Install the required dependencies before running:

```
pip install pandas requests streamlit
```

To run the Streamlit app locally, create a `.streamlit/secrets.toml` file with your own contact email (required by the SEC as a `User-Agent` identifier on API requests):

```toml
USER_AGENT = "your_email@domain.com"
```

Then launch the app:

```
streamlit run StreamlitApp.py
```

## Tech Stack

- **Python** — core pipeline logic
- **pandas** — data extraction and transformation
- **requests** — SEC API calls
- **Streamlit** — interactive web interface
- **SEC EDGAR Company Facts API** — data source (`data.sec.gov/api/xbrl/companyfacts/`)

## About

Built by [Ozoemena Nnamadim](https://www.otnnamadim.com), CPA — part of the **Aperture Insights** content series exploring the intersection of accounting, Python, and financial technology.

- [Website](https://www.otnnamadim.com)
- [Project case study](https://www.otnnamadim.com/projects-case-studies/edgarfspull)
