"""
Airbnb listing scraper using Playwright.

Extracts property details from an Airbnb listing URL by parsing the
page's embedded JSON data. Falls back to DOM parsing if needed.
Maps results to the worldwide Inside Airbnb feature schema.

Windows note:
- Uvicorn/FastAPI may run on an asyncio loop policy that does NOT support
  subprocesses. Playwright requires subprocess support to launch its driver.
  To avoid `NotImplementedError` on Windows, we run Playwright in a worker
  thread with its own event loop.
"""

import json
import re
import math
from typing import Optional

from app.ml.data_transformation import CITY_COORDS, CITY_CURRENCY, AMENITY_FEATURES


async def scrape_listing(url: str) -> dict:
    """
    Scrape an Airbnb listing URL and return features for prediction.

    On Windows, run Playwright in a worker thread with its own event loop
    to avoid `NotImplementedError` from subprocess support.
    """
    import os
    import asyncio
    import platform
    import anyio

    if platform.system().lower().startswith("win"):
        def _runner():
            # Force a Proactor event loop (required for subprocess support on Windows)
            try:
                loop = asyncio.ProactorEventLoop()
            except Exception:
                # Last-resort fallback: try whatever asyncio gives us
                return asyncio.run(_scrape_listing_async(url))

            try:
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(_scrape_listing_async(url))
            finally:
                try:
                    loop.run_until_complete(loop.shutdown_asyncgens())
                except Exception:
                    pass
                try:
                    loop.close()
                except Exception:
                    pass

        return await anyio.to_thread.run_sync(_runner)

    return await _scrape_listing_async(url)


async def _scrape_listing_async(url: str) -> dict:
    from playwright.async_api import async_playwright

    listing_id = _extract_listing_id(url)
    if not listing_id:
        raise ValueError(f"Could not extract listing ID from URL: {url}")

    canonical_url = _normalize_url(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        try:
            await page.goto(canonical_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            data = await _extract_from_scripts(page)
            if not data:
                data = await _extract_from_dom(page)

            if not data:
                raise RuntimeError("Could not extract listing data from page")

            return _normalize(data, listing_id)
        finally:
            await browser.close()


def _extract_listing_id(url: str) -> Optional[str]:
    match = re.search(r"/rooms/(\d+)", url)
    return match.group(1) if match else None


def _normalize_url(url: str) -> str:
    listing_id = _extract_listing_id(url)
    if listing_id:
        return f"https://www.airbnb.com/rooms/{listing_id}"
    return url


async def _extract_from_scripts(page) -> Optional[dict]:
    scripts = await page.query_selector_all("script[type='application/json']")
    for script in scripts:
        text = await script.inner_text()
        try:
            data = json.loads(text)
            listing = _find_listing_in_json(data)
            if listing:
                return listing
        except (json.JSONDecodeError, TypeError):
            continue

    # JSON-LD can include geo coordinates even when main JSON is obfuscated
    scripts_ld = await page.query_selector_all("script[type='application/ld+json']")
    for script in scripts_ld:
        text = await script.inner_text()
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            continue
        geo = _find_geo_in_jsonld(data)
        if geo:
            return geo

    content = await page.content()
    pattern = r'<script[^>]*id="data-deferred-state[^"]*"[^>]*>(.*?)</script>'
    matches = re.findall(pattern, content, re.DOTALL)
    for match in matches:
        try:
            data = json.loads(match)
            listing = _find_listing_in_json(data)
            if listing:
                return listing
        except (json.JSONDecodeError, TypeError):
            continue

    geo = _extract_geo_from_html(content)
    if geo:
        return geo

    return None


def _find_listing_in_json(data, depth=0) -> Optional[dict]:
    if depth > 8:
        return None
    if isinstance(data, dict):
        if "bedrooms" in data and ("bathrooms" in data or "bathroomLabel" in data):
            return data
        if "listing" in data and isinstance(data["listing"], dict):
            return data["listing"]
        if "pdpListing" in data and isinstance(data["pdpListing"], dict):
            return data["pdpListing"]
        for v in data.values():
            result = _find_listing_in_json(v, depth + 1)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = _find_listing_in_json(item, depth + 1)
            if result:
                return result
    return None


def _find_geo_in_jsonld(data) -> Optional[dict]:
    """Find `geo.latitude/longitude` in JSON-LD blobs."""

    def _coerce(x):
        try:
            return float(x)
        except Exception:
            return None

    if isinstance(data, list):
        for item in data:
            geo = _find_geo_in_jsonld(item)
            if geo:
                return geo
        return None

    if not isinstance(data, dict):
        return None

    geo_obj = data.get("geo")
    if isinstance(geo_obj, dict):
        lat = _coerce(geo_obj.get("latitude"))
        lng = _coerce(geo_obj.get("longitude"))
        if lat is not None and lng is not None:
            return {"latitude": lat, "longitude": lng}

    graph = data.get("@graph")
    if isinstance(graph, list):
        for item in graph:
            geo = _find_geo_in_jsonld(item)
            if geo:
                return geo

    return None


def _extract_geo_from_html(html: str) -> Optional[dict]:
    """Regex search coordinates inside HTML/JS payload."""
    m = re.search(r'"lat"\s*:\s*([-]?\d+\.\d+)\s*,\s*"lng"\s*:\s*([-]?\d+\.\d+)', html)
    if m:
        try:
            return {"latitude": float(m.group(1)), "longitude": float(m.group(2))}
        except Exception:
            return None

    m = re.search(r'"latitude"\s*:\s*([-]?\d+\.\d+)\s*,\s*"longitude"\s*:\s*([-]?\d+\.\d+)', html)
    if m:
        try:
            return {"latitude": float(m.group(1)), "longitude": float(m.group(2))}
        except Exception:
            return None

    return None

async def _extract_from_dom(page) -> Optional[dict]:
    data = {}
    try:
        title = await page.title()
        if title:
            data["name"] = title

        details_text = await page.inner_text("body")
        bedroom_match = re.search(r"(\d+)\s*bedroom", details_text, re.I)
        if bedroom_match:
            data["bedrooms"] = int(bedroom_match.group(1))

        bed_match = re.search(r"(\d+)\s*bed(?!room)", details_text, re.I)
        if bed_match:
            data["beds"] = int(bed_match.group(1))

        bath_match = re.search(r"([\d.]+)\s*bath", details_text, re.I)
        if bath_match:
            data["bathrooms"] = float(bath_match.group(1))

        guest_match = re.search(r"(\d+)\s*guest", details_text, re.I)
        if guest_match:
            data["accommodates"] = int(guest_match.group(1))

        review_match = re.search(r"([\d,]+)\s*review", details_text, re.I)
        if review_match:
            data["number_of_reviews"] = int(review_match.group(1).replace(",", ""))

        rating_match = re.search(r"([\d.]+)\s*·", details_text)
        if rating_match:
            val = float(rating_match.group(1))
            if 1 <= val <= 5:
                data["review_scores_rating"] = val

    except Exception:
        pass

    return data if data else None


def _detect_city(lat: float, lng: float) -> tuple[str, str]:
    """Find the closest known city based on coordinates."""
    best_city = "New York"
    best_dist = float("inf")

    for city, (clat, clng) in CITY_COORDS.items():
        dist = math.sqrt((lat - clat) ** 2 + (lng - clng) ** 2)
        if dist < best_dist:
            best_dist = dist
            best_city = city

    country_map = {
        "Amsterdam": "Netherlands", "Athens": "Greece", "Bangkok": "Thailand",
        "Barcelona": "Spain", "Berlin": "Germany", "Buenos Aires": "Argentina",
        "Cape Town": "South Africa", "Chicago": "United States",
        "Hong Kong": "China", "Lisbon": "Portugal", "London": "United Kingdom",
        "Los Angeles": "United States", "Madrid": "Spain",
        "Melbourne": "Australia", "Mexico City": "Mexico",
        "New York": "United States", "Paris": "France", "Prague": "Czech Republic",
        "Rome": "Italy", "San Francisco": "United States",
        "Singapore": "Singapore", "Sydney": "Australia",
        "Tokyo": "Japan", "Vienna": "Austria",
    }

    return best_city, country_map.get(best_city, "United States")


def _normalize(raw: dict, listing_id: str) -> dict:
    def _get(keys, default=None):
        for k in keys:
            if k in raw and raw[k] is not None:
                return raw[k]
        return default

    lat = float(_get(["latitude", "lat"], 40.7128))
    lng = float(_get(["longitude", "lng", "lon"], -74.006))
    city, country = _detect_city(lat, lng)

    room_type_raw = str(_get(["room_type", "roomType", "room_type_category"], "Entire home/apt"))
    room_map = {"entire": "Entire home/apt", "private": "Private room", "shared": "Shared room"}
    room_type = "Entire home/apt"
    for key, val in room_map.items():
        if key in room_type_raw.lower():
            room_type = val
            break

    amenities_raw = _get(["amenities", "listing_amenities"], [])
    amenities_list = []
    if isinstance(amenities_raw, list):
        amenities_list = [str(a).lower() for a in amenities_raw]
    elif isinstance(amenities_raw, str):
        try:
            parsed = json.loads(amenities_raw)
            amenities_list = [str(a).lower() for a in parsed]
        except (json.JSONDecodeError, TypeError):
            amenities_list = [a.strip().lower() for a in amenities_raw.split(",")]

    amenities_count = len(amenities_list)
    amenities_set = set(amenities_list)

    amenity_check = {
        "has_elevator": ["elevator", "lift"],
        "has_pool": ["pool", "swimming pool"],
        "has_hot_tub": ["hot tub", "jacuzzi"],
        "has_gym": ["gym", "fitness", "exercise equipment"],
        "has_doorman": ["doorman", "doorperson"],
        "has_air_conditioning": ["air conditioning", "a/c", "ac"],
        "has_heating": ["heating", "central heating"],
        "has_washer": ["washer", "washing machine"],
        "has_dryer": ["dryer"],
        "has_kitchen": ["kitchen"],
        "has_tv": ["tv", "television"],
        "has_wifi": ["wifi", "wireless internet", "wi-fi"],
        "has_free_parking_on_premises": ["free parking on premises", "free parking", "free street parking"],
        "has_indoor_fireplace": ["indoor fireplace", "fireplace"],
        "has_patio_or_balcony": ["patio or balcony", "patio", "balcony"],
        "has_breakfast": ["breakfast"],
        "has_buzzer_wireless_intercom": ["buzzer/wireless intercom", "buzzer", "intercom"],
        "has_wheelchair_accessible": ["wheelchair accessible"],
    }

    amenity_flags = {}
    for feat, aliases in amenity_check.items():
        amenity_flags[feat] = 1 if any(a in amenities_set for a in aliases) else 0

    host_response = _get(["host_response_rate"], 90)
    if isinstance(host_response, str):
        host_response = float(host_response.replace("%", "") or 90)
    host_response = float(host_response)
    if host_response > 1 and host_response <= 100:
        pass
    elif host_response <= 1:
        host_response *= 100

    rating = _get(["review_scores_rating", "star_rating"], 4.5)
    rating = float(rating)
    if rating > 5:
        rating = rating / 20.0

    result = {
        "property_type": str(_get(["property_type", "propertyType"], "Entire rental unit")),
        "room_type": room_type,
        "city": city,
        "country": country,
        "accommodates": int(_get(["accommodates", "personCapacity", "person_capacity"], 2)),
        "bedrooms": float(_get(["bedrooms", "bedroom_count"], 1)),
        "beds": float(_get(["beds", "bed_count"], 1)),
        "bathrooms": float(_get(["bathrooms", "bathroom_count"], 1.0)),
        "latitude": lat,
        "longitude": lng,
        "amenities_count": amenities_count,
        "host_response_rate": host_response,
        "host_acceptance_rate": float(_get(["host_acceptance_rate"], 85)),
        "host_is_superhost": "t" if _get(["host_is_superhost", "isSuperhost"], False) else "f",
        "instant_bookable": "t" if _get(["instant_bookable", "is_instant_bookable"], False) else "f",
        "number_of_reviews": int(_get(["number_of_reviews", "reviewsCount", "visible_review_count"], 0)),
        "reviews_per_month": float(_get(["reviews_per_month"], 1.5)),
        "review_scores_rating": rating,
        "review_scores_accuracy": float(_get(["review_scores_accuracy"], 4.5)),
        "review_scores_cleanliness": float(_get(["review_scores_cleanliness"], 4.5)),
        "review_scores_checkin": float(_get(["review_scores_checkin"], 4.5)),
        "review_scores_communication": float(_get(["review_scores_communication"], 4.5)),
        "review_scores_location": float(_get(["review_scores_location"], 4.5)),
        "review_scores_value": float(_get(["review_scores_value"], 4.5)),
        "minimum_nights": int(_get(["minimum_nights"], 2)),
        "availability_365": int(_get(["availability_365"], 200)),
        "calculated_host_listings_count": int(_get(["calculated_host_listings_count"], 1)),
        **amenity_flags,
        "_scraped": True,
        "_listing_id": listing_id,
    }

    return result
