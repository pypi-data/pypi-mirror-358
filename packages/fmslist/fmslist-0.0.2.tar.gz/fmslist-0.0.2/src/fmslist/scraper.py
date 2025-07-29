import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

import requests


@dataclass
class Variant:
    """A class to hold details of a variant of an item."""

    id: int
    name: str
    price: str
    available: bool
    quantity: int


@dataclass(frozen=True)
class ItemDetails:
    """A class to hold details of an item."""

    id: int
    title: str
    vendor: str
    image_urls: list[str]
    link: str
    published_at: datetime
    updated_at: datetime
    variants: list[Variant]


class FindMeStoreList:
    """A class to scrape the Find Me Store (FMS) list from the specified URL."""

    items: list[ItemDetails] = []

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "MJ12bot"})
        self._base_url = "https://findmestore.thinkr.jp"

    def fetch_items(self) -> None:
        """Fetches all items from the FMS list."""
        page = 1
        while True:
            try:
                # Fetch the first page of products
                items = self._fetch_products(page)
                self.items.extend(items)
                if not items:
                    break  # No products found, exit the loop
                page += 1
            except ValueError as e:
                print(f"Error fetching products: {e}")
                break  # Exit the loop on error

        # Sort items by publish time
        self.items.sort(key=lambda item: item.published_at, reverse=True)

    def fill_quantities(self) -> None:
        """Fills the quantities for each variant in the items."""
        quantities: Mapping[int, int] = {}
        page = 1
        while True:
            try:
                # Fetch quantities from the search API
                q = self._fetch_quantities(page)
                quantities.update(q)
                if not q:
                    break
                page += 1
            except ValueError as e:
                print(f"Error fetching quantities: {e}")
                break

        for item in self.items:
            for variant in item.variants:
                variant.quantity = max(quantities.get(variant.id, 0), -1)

    def _fetch_quantities(self, page: int) -> Mapping[int, int]:
        """Fetches the quantities from search API. Returns a mapping of variant IDs to quantities."""
        while True:
            res = self._session.get(
                f"{self._base_url}/search?view=preorderjson&q=*&page={page}"
            )
            if res.status_code == 200:
                break
            elif res.status_code == 429:
                print(f"Rate limit exceeded, waiting 5s before retrying page {page}...")
                time.sleep(5)
            else:
                raise ValueError(
                    f"Failed to fetch search result at page {page}: [{res.status_code}] {res.text}"
                )
        # A hacky fix for the API returning an empty "id" field
        json_fixed = re.sub(r":\s*(,|\})", f": null\\1", res.text)
        return {
            variant["id"]: variant["inventory_quantity"]
            for product in json.loads(json_fixed)
            for variant in product.get("variants", [])
            if variant["available"]
        }

    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parses a timestamp string into a datetime object."""
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")

    def _parse_product(self, product: dict) -> ItemDetails:
        """Parses a product dictionary into an ItemDetails object."""
        id = product["id"]
        title = product["title"]
        vendor = product.get("vendor", "Unknown Vendor")
        image_urls = [image["src"] for image in product.get("images", [])]
        link = f"{self._base_url}/products/{product['handle']}"
        published_at = self._parse_timestamp(product["published_at"])
        updated_at = self._parse_timestamp(product["updated_at"])
        variants = [
            Variant(
                id=variant["id"],
                name=variant["title"] if variant["title"] != "Default Title" else "",
                price=variant["price"],
                available=variant["available"],
                quantity=0,
            )
            for variant in product.get("variants", [])
        ]
        return ItemDetails(
            id, title, vendor, image_urls, link, published_at, updated_at, variants
        )

    def _fetch_products(self, page: int) -> list[ItemDetails]:
        """Fetches the products from the FMS list."""
        while True:
            res = self._session.get(
                f"{self._base_url}/products.json?limit=250&page={page}"
            )
            if res.status_code == 200:
                break
            elif res.status_code == 429:
                print(f"Rate limit exceeded, waiting 5s before retrying page {page}...")
                time.sleep(5)
            else:
                raise ValueError(
                    f"Failed to fetch products at page {page}: [{res.status_code}] {res.text}"
                )
        products = res.json().get("products", [])
        return [self._parse_product(product) for product in products]
