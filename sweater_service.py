"""
Dog sweater service — searches Etsy for dog sweaters matching a breed.
Uses the Etsy Open API v3 findAllListingsActive endpoint (public, API-key only).
Falls back to mock data when credentials are missing or the API is unreachable.
"""

import logging
import os
from typing import List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

ETSY_KEYSTRING = os.getenv("ETSY_API_KEYSTRING", "")
ETSY_SECRET = os.getenv("ETSY_SHARED_SECRET", "")
ETSY_BASE = "https://openapi.etsy.com/v3/application"


def _etsy_headers() -> dict:
    return {"x-api-key": f"{ETSY_KEYSTRING}"}


def _search_etsy(breed_name: str, limit: int = 4) -> Optional[List[dict]]:
    """
    Search Etsy active listings for dog sweaters for the given breed.
    Returns a list of dicts or None on failure.
    """
    if not ETSY_KEYSTRING:
        return None

    query = f"{breed_name} dog sweater"
    params = {
        "keywords": query,
        "limit": limit,
        "sort_on": "score",
        "includes": "Images",
    }
    url = f"{ETSY_BASE}/listings/active"

    try:
        resp = requests.get(url, headers=_etsy_headers(), params=params, timeout=8)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("Etsy API request failed: %s", exc)
        return None

    data = resp.json()
    results = data.get("results", [])
    if not results:
        return None

    sweaters = []
    for listing in results[:limit]:
        title = listing.get("title", "Dog Sweater")
        listing_id = listing.get("listing_id", "")
        price_obj = listing.get("price", {})
        amount = price_obj.get("amount")
        divisor = price_obj.get("divisor", 100)
        currency = price_obj.get("currency_code", "USD")

        if amount is not None:
            price_val = amount / divisor
            price_str = f"${price_val:,.2f}" if currency == "USD" else f"{price_val:,.2f} {currency}"
        else:
            price_str = "See listing"

        product_url = listing.get("url", f"https://www.etsy.com/listing/{listing_id}")

        image_url = ""
        images = listing.get("images", [])
        if images:
            image_url = images[0].get("url_570xN", "") or images[0].get("url_170x135", "")
        if not image_url:
            image_url = f"https://placehold.co/200x200/e8d5f2/7c3aed?text={breed_name.replace(' ', '+')}"

        sweaters.append({
            "name": title,
            "product_url": product_url,
            "price": price_str,
            "image_url": image_url,
        })

    return sweaters


def _mock_sweaters(breed_name: str, limit: int = 4) -> List[dict]:
    items = [
        {"name": f"Cozy Knit Sweater for {breed_name}",   "product_url": "https://www.etsy.com/search?q=dog+sweater", "price": "$24.99", "image_url": "https://placehold.co/200x200/e8d5f2/7c3aed?text=Sweater+1"},
        {"name": f"Fair Isle Dog Sweater – {breed_name}",  "product_url": "https://www.etsy.com/search?q=dog+sweater", "price": "$29.99", "image_url": "https://placehold.co/200x200/c4b5fd/5b21b6?text=Sweater+2"},
        {"name": f"Warm Cable Knit – {breed_name}",        "product_url": "https://www.etsy.com/search?q=dog+sweater", "price": "$19.99", "image_url": "https://placehold.co/200x200/ddd6fe/6d28d9?text=Sweater+3"},
        {"name": f"Classic Plaid Dog Sweater",              "product_url": "https://www.etsy.com/search?q=dog+sweater", "price": "$27.99", "image_url": "https://placehold.co/200x200/ede9fe/4c1d95?text=Sweater+4"},
    ]
    return items[:limit]


def get_sweaters_for_breed(breed_name: str, limit: int = 4) -> List[dict]:
    """Return dog sweaters for a breed. Tries Etsy first, falls back to mocks."""
    etsy_results = _search_etsy(breed_name, limit)
    if etsy_results:
        return etsy_results
    log.info("Using mock sweater data (set ETSY_API_KEYSTRING in .env for real results)")
    return _mock_sweaters(breed_name, limit)
