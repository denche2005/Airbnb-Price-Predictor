"""
Download Airbnb listings data from Inside Airbnb for 24 major cities worldwide.
Run: python download_data.py
"""

import os
import sys
import urllib.request
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "worldwide_listings.csv.gz")

CITIES = {
    # Europe
    "Barcelona": ("spain/catalonia/barcelona", "2025-09-14", "Spain", "EUR"),
    "Madrid": ("spain/comunidad-de-madrid/madrid", "2025-09-14", "Spain", "EUR"),
    "Paris": ("france/ile-de-france/paris", "2025-09-12", "France", "EUR"),
    "London": ("united-kingdom/england/london", "2025-09-14", "United Kingdom", "GBP"),
    "Berlin": ("germany/be/berlin", "2025-09-23", "Germany", "EUR"),
    "Rome": ("italy/lazio/rome", "2025-09-14", "Italy", "EUR"),
    "Amsterdam": ("the-netherlands/north-holland/amsterdam", "2025-09-11", "Netherlands", "EUR"),
    "Lisbon": ("portugal/lisbon/lisbon", "2025-09-21", "Portugal", "EUR"),
    "Vienna": ("austria/vienna/vienna", "2025-09-14", "Austria", "EUR"),
    "Athens": ("greece/attica/athens", "2025-09-26", "Greece", "EUR"),
    "Prague": ("czech-republic/prague/prague", "2025-09-23", "Czech Republic", "CZK"),
    # Americas
    "New York": ("united-states/ny/new-york-city", "2025-12-04", "United States", "USD"),
    "San Francisco": ("united-states/ca/san-francisco", "2025-12-04", "United States", "USD"),
    "Los Angeles": ("united-states/ca/los-angeles", "2025-12-04", "United States", "USD"),
    "Chicago": ("united-states/il/chicago", "2025-09-22", "United States", "USD"),
    "Buenos Aires": ("argentina/ciudad-aut%C3%B3noma-de-buenos-aires/buenos-aires", "2025-01-29", "Argentina", "ARS"),
    "Mexico City": ("mexico/df/mexico-city", "2025-09-27", "Mexico", "MXN"),
    # Asia
    "Tokyo": ("japan/kant%C5%8D/tokyo", "2025-09-29", "Japan", "JPY"),
    "Bangkok": ("thailand/central-thailand/bangkok", "2025-09-26", "Thailand", "THB"),
    "Singapore": ("singapore/sg/singapore", "2025-09-28", "Singapore", "SGD"),
    "Hong Kong": ("china/hk/hong-kong", "2025-09-23", "China", "HKD"),
    # Oceania
    "Sydney": ("australia/nsw/sydney", "2025-09-12", "Australia", "AUD"),
    "Melbourne": ("australia/vic/melbourne", "2025-09-12", "Australia", "AUD"),
    # Africa
    "Cape Town": ("south-africa/wc/cape-town", "2025-09-28", "South Africa", "ZAR"),
}


def download_city(city_name, path, date, country, currency):
    url = f"https://data.insideairbnb.com/{path}/{date}/data/listings.csv.gz"
    local_gz = os.path.join(DATA_DIR, f"{city_name.lower().replace(' ', '_')}.csv.gz")

    if os.path.exists(local_gz):
        print(f"  [cached] {city_name}", flush=True)
    else:
        print(f"  Downloading {city_name} from {url}...", flush=True)
        try:
            urllib.request.urlretrieve(url, local_gz)
        except Exception as e:
            print(f"  [FAILED] {city_name}: {e}", flush=True)
            return None

    try:
        df = pd.read_csv(local_gz, low_memory=False)
        df["city"] = city_name
        df["country"] = country
        df["currency"] = currency
        print(f"  {city_name}: {len(df):,} listings", flush=True)
        return df
    except Exception as e:
        print(f"  [FAILED to read] {city_name}: {e}", flush=True)
        return None


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Downloading listings from {len(CITIES)} cities...\n", flush=True)

    frames = []
    for city_name, (path, date, country, currency) in CITIES.items():
        df = download_city(city_name, path, date, country, currency)
        if df is not None:
            frames.append(df)

    if not frames:
        print("No data downloaded!", flush=True)
        sys.exit(1)

    print(f"\nConcatenating {len(frames)} city datasets...", flush=True)
    combined = pd.concat(frames, ignore_index=True)
    print(f"Total: {len(combined):,} listings across {combined['city'].nunique()} cities", flush=True)

    combined.to_csv(OUTPUT_FILE, index=False, compression="gzip")
    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"Saved to {OUTPUT_FILE} ({size_mb:.1f} MB)", flush=True)

    print("\nPer-city breakdown:", flush=True)
    for city, count in combined["city"].value_counts().items():
        print(f"  {city:20s} {count:>7,d}", flush=True)


if __name__ == "__main__":
    main()
