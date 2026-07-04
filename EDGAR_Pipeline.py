"""
Disclaimer: The companies detailed herein are not specific investment recommendations.
The purpose of this code is to illustrate the functionality of the SEC's Company Fact
API in extracting financial information to conduct financial statement analysis.
"""


import pandas as pd
import requests


#OTN Note: Defines the watchlist first based on the company's CIK, company name, Ticker, and SEC Filing category.

def investment_watchlist() -> pd.DataFrame:
    watchlist_domestic = [
        {"category": "domestic", "company_name": "Flex Ltd", "ticker": "FLEX", "cik": "0000866374"},
        {"category": "domestic", "company_name": "Vertiv", "ticker": "VRT", "cik": "0001674101"},
        {"category": "domestic", "company_name": "AEHR Test Systems", "ticker": "AEHR", "cik": "0001040470"},
        {"category": "domestic", "company_name": "Quanta Services Inc", "ticker": "PWR", "cik": "0001050915"},
    ]

    watchlist_fpi = [
        {"category": "fpi", "company_name": "Taiwan Semiconductor", "ticker": "TSM", "cik": "0001046179"},
        {"category": "fpi", "company_name": "GlobalFoundries Systems", "ticker": "GFS", "cik": "0001709048"},
        #{"category": "fpi", "company_name": "STMicroelectronics", "ticker": "STM", "cik": "0000932787"},
        #{"category": "fpi", "company_name": "Infineon", "ticker": "IFNNY", "cik": "0001107457"},
        #{"category": "fpi", "company_name": "FoxCon - Hon Hai Precision Industry Co", "ticker": "HNHPF", "cik": "0001611906"},
    ]
    return pd.DataFrame(watchlist_domestic + watchlist_fpi)


#OTN Note: This section connects to EDGAR via the company facts API by referencing the company CIK number & user agent. Once the API connects, the XBRL data for the stock is stored as a dictionary.

def get_company_facts(cik: str, user_agent: str) -> dict:

    padded_cik = cik.zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json"
    headers = {"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"}

    print(f"Fetching data from: {url}")
    response = requests.get(url, headers=headers)

    response.raise_for_status()

    data = response.json()
    assert isinstance(data, dict)

    return data


#OTN Note: Extracts the XBRL data from each 10-K, 10-Q, 6-K, and 20-F and stores the result as a dataframe. Annotates IFRS and US GAAP reporting method to ensure accounting standards are clearly delineated for comparability.

def extract_fsli_to_dataframe(company_json: dict, fsli_name: str) -> pd.DataFrame:

    try:
        facts = company_json.get("facts", {})

        if "us-gaap" in facts:
            accounting_standard = "us-gaap"
        elif "ifrs-full" in facts:
            accounting_standard = "ifrs-full"
        else:
            accounting_standard = None

        if not accounting_standard:
            raise KeyError("Neither accounting standard found in company facts.")

        statements = facts[accounting_standard]

        if fsli_name not in statements:
            raise KeyError(
                f"Financial statement line item '{fsli_name}' not found in this company's facts."
            )

        fsli_data = statements[fsli_name]
        unit_key = list(fsli_data["units"].keys())[0]
        financial_statements = fsli_data["units"][unit_key]
        df = pd.DataFrame(financial_statements)

        columns_to_keep = ["form", "fy", "fp", "start", "end", "val", "accn", "frame"]
        df = df[[col for col in columns_to_keep if col in df.columns]]
        df["accounting_standard"] = accounting_standard

        return df

    except KeyError as e:
        print(f"Error parsing JSON structure: {e}")
        return pd.DataFrame()


#OTN Note: Parses the company facts dictionary to list the accounting standard and number of financial statement line items and historical datapoints for each company.

def list_accounting_standard (company_json: dict) -> pd.DataFrame:
    try:
        facts = company_json.get("facts", {})
        accounting_standard = "us-gaap" if "us-gaap" in facts else "ifrs-full" if "ifrs-full" in facts else None

        if not accounting_standard:
            print("Could not find the accounting standard for this company.")
            return pd.DataFrame()

        summary_data = []

        for concept, details in facts[accounting_standard].items():
            first_unit = list(details["units"].keys())[0]
            record_count = len(details["units"][first_unit])

            summary_data.append(
                {"Taxonomy": accounting_standard, "Concept": concept, "Data_Points_Count": record_count}
            )

        fsli_list_df = pd.DataFrame(summary_data)
        return fsli_list_df.sort_values(by="Concept").reset_index(drop=True)

    except (KeyError, IndexError):
        return pd.DataFrame()
