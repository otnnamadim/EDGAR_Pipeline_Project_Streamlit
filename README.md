# EDGAR Pipeline Project

This is a Python coding project developed for extracting and parsing financial statement data from six SEC filers via the Company Facts API. The result is presented within an interactive Streamlit web application that displays depicts the historical trends.

**Live app:** [aperture-insights-edgar-pull.streamlit.app](https://aperture-insights-edgar-pull.streamlit.app/)

> **Disclaimer:** The companies referenced in this repository's watchlist are not specific investment recommendations. This project exists to illustrate the functionality of the SEC's Company Facts API in extracting financial information to conduct financial statement analysis.

## Why this project exists

Every public company filing with the SEC tags their financial statements with XBRL tags. As an accounting consultant, I've previously worked on public company filings and converted the financial statements for a foreign private issuer from IFRS to US GAAP. Further, in financial reporting, I've prepared financial statement footnote disclosures and tagged each disclosure utilizing XBRL data in preparation for submission to EDGAR. This project is interesting because it retrieves the following filings types from the EDGAR database: 10-K, 10-Q, 6-K, 20/40-F report data in order to present financial data for both foreign and domestic filers.

## Distinguishing Foreign from Domestic filers
The technology and semiconductor ecosystem consists of many players both domestic and abroad, and this listing is a small example of the nuance of comparing their financial statements. The data pipeline pulls the XBRL data via the Company Facts API and flattens it into `pandas` DataFrames with a particular focus on distinguishing foreign private issuers (FPIs) from domestic filers. US-based companies, domestic filers, issue their financial statements under US GAAP, while many FPIs file under IFRS, with different XBRL taxonomies and tagging conventions entirely.

## How it works

- **Defines the Companies on the Investment Watchlist** by listing out the Company Name, CIK, Ticker, and categorizing them as either Domestic or FPI based on their headquarters domiciliation.
- **Pulls raw XBRL company facts** for any public company by referencing the company's CIK (Central Index Key) via the Company Facts API.
- **Flattens nested JSON Company Facts** into tidy DataFrames for all tagged financial statement line items.
- **Lists all available GAAP concepts** a company has reported to explore the available financial statement line before querying.

## The Streamlit App

The Python program establishes the pipeline, and the resulting pandas outputs are wrapped in an interactive via a Streamlit interface so the data is usable without touching the code:

- Select any company from the watchlist via dropdown
- Select a financial metric (Total Assets, Total Equity, Liabilities, Total Income, Total Revenue)
- Pull live data directly from EDGAR with one click
- View the latest reported figure, the full historical data table (form type, fiscal year, period, value, accession number), and a trend chart across annual filings

The app also surfaces the accounting logic under the hood — each result is captioned with the filer type (Domestic/FPI), the detected accounting standard (US-GAAP/IFRS), and the specific XBRL tag used to retrieve the value.

## Issues encountered in finalizing the StreamLit interface:

There were several companies that were

**Vertiv (VRT) — resolved.** Total Revenue for the company was initially coded as "Revenues" via XBRL. The original result when preparing the data pipeline initially returned `$0` due to XBRL; however, Vertiv tags revenue as `RevenueFromContractWithCustomerExcludingAssessedTax` rather than "Revenues" as the majority of companies on this listing do. The code was updated to include the fallback logic to incorporate 'RevenueFromContractWithCustomerExcludingAssessedTax' in order to have a comparable revenue datapoint incorporated within the database.


```python
METRIC_MAPPING = {
    "Total Revenue": {
        "us-gaap": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
        "ifrs-full": ["Revenue"]
    },
    # ... same pattern for other metrics
}
```

**Takeaway:** XBRL tagging is subject to the company's accounting team's discretion; as such, the tags are not perfectly standardized across filers even though the financial statement line items are reported comparably per the standards. It is still important to review the individual company's tags in order to understand whether or not the python script or the codes will properly pull the correct data. 

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

Built by [Ozoemena Nnamadim](https://www.otnnamadim.com), CPA

- [Website](https://www.otnnamadim.com)
- [Project case study](https://www.otnnamadim.com/projects-case-studies/edgarfspull)
