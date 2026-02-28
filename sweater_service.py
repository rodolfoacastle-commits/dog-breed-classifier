"""
Dog sweater service: abstract layer for fetching dog sweaters by breed.
Mock implementation returns hardcoded items; replace with real API (e.g. Etsy) later.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class DogSweater:
    name: str
    product_url: str
    price: str
    image_url: str


def get_sweaters_for_breed(breed_name: str, limit: int = 4) -> List[dict]:
    """
    Return a list of dog sweaters for the given breed.
    Mock: returns placeholder sweaters. Replace with real API call (see comments below).
    """
    # TODO: Plug in real API here (e.g. Etsy, eBay). Use breed_name in query.
    # Example: requests.get(API_URL, params={"q": f"dog sweater {breed_name}"})
    mock_sweaters = [
        DogSweater(
            name=f"Cozy Knit Sweater for {breed_name}",
            product_url="https://example.com/sweater1",
            price="$24.99",
            image_url="https://placehold.co/200x200/e8d5f2/7c3aed?text=Sweater+1",
        ),
        DogSweater(
            name=f"Fair Isle Dog Sweater – {breed_name}",
            product_url="https://example.com/sweater2",
            price="$29.99",
            image_url="https://placehold.co/200x200/c4b5fd/5b21b6?text=Sweater+2",
        ),
        DogSweater(
            name=f"Warm Cable Knit – {breed_name}",
            product_url="https://example.com/sweater3",
            price="$19.99",
            image_url="https://placehold.co/200x200/ddd6fe/6d28d9?text=Sweater+3",
        ),
        DogSweater(
            name=f"Classic Plaid Dog Sweater",
            product_url="https://example.com/sweater4",
            price="$27.99",
            image_url="https://placehold.co/200x200/ede9fe/4c1d95?text=Sweater+4",
        ),
    ]
    return [
        {"name": s.name, "product_url": s.product_url, "price": s.price, "image_url": s.image_url}
        for s in mock_sweaters[:limit]
    ]
