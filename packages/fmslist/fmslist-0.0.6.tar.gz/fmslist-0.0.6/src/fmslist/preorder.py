import json
import re
import time
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from utils import FMS_BASE_URL, fix_json


@dataclass(frozen=True)
class Period:
    """A class to hold a period of time"""

    start_time: datetime
    end_time: datetime


@dataclass
class PreorderEvent:
    """A class to hold details of a preorder event."""

    id: int
    title: str
    link: str
    periods: list[Period]
    shipping_time: str | None = None


class FindMeStorePreorderList:
    """A class to scrape the Find Me Store (FMS) list from the specified URL."""

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "MJ12bot"})

    def get_preorder_events(self) -> list[PreorderEvent]:
        """Fetches preorder events from the FMS list."""
        events = self._fetch_preorder_events()
        if not events:
            print("No preorder events found.")
            return []

        # Fetch additional details for each event
        self._fetch_preorder_period(events)

        # Order by max end date desc, then by min start date asc
        events.sort(
            key=lambda e: (
                (
                    max([p.end_time for p in e.periods]) if e.periods else datetime.min,
                    (
                        min([p.start_time.timestamp() for p in e.periods])
                        if e.periods
                        else 0
                    ),
                ),
            ),
            reverse=True,
        )

        return events

    def _remove_weekday(self, text: str) -> str:
        """Removes the weekday from the date string."""
        return re.sub(r"\s*[\(（].*?[\)）]\s*", " ", text).strip()

    def _unify_hyphen_symbol(self, text: str) -> str:
        """Unifies the tilde and hyphen symbols."""
        return re.sub(r"\s*[〜~-]\s*", "-", text).strip()

    def _remove_year_kanji(self, text: str) -> str:
        """Removes the year kanji from the date string."""
        return re.sub(r"\s*(\d{4})[\s年]*", r"\g<1>y", text).strip()

    def _fix_hour_kanji(self, text: str) -> str:
        """Replaces 時 with :00."""
        return text.replace("時", ":00")

    def _parse_period(self, text: str) -> Period | None:
        """Parses a period from a string and returns it as datetime objects."""
        start_str, end_str = text.split("-", 1)
        if "y" not in end_str:
            # The end date does not have a year, use the start year
            start_year, _ = start_str.split("y", 1)
            end_str = f"{start_year}y{end_str}"
        try:
            start_date = datetime.strptime(f"{start_str.strip()}", "%Yy%m/%d %H:%M")
            end_date = datetime.strptime(f"{end_str.strip()}", "%Yy%m/%d %H:%M")
            return Period(start_date, end_date)
        except ValueError as e:
            print(f"Error parsing date from '{text}': {e}")
            return None

    def _extract_periods(self, text: str) -> list[Period]:
        """Extracts a list of periods from a string and returns it as datetime objects."""
        text = self._remove_weekday(text)
        text = self._fix_hour_kanji(text)
        text = self._unify_hyphen_symbol(text)
        text = self._remove_year_kanji(text)

        matches = re.findall(
            r"(\d{4}y\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}-(?:\d{4}y)?\d{1,2}/\d{1,2} \d{1,2}:\d{1,2})",
            text,
        )

        if not matches:
            print(f"Failed to match periods: {text}")

        periods = []
        for match in matches:
            period = self._parse_period(match)
            if period:
                periods.append(period)

        return periods

    def _fetch_preorder_period(
        self, events: list[PreorderEvent], filter_non_preorder=True
    ) -> None:
        for event in events:
            res = self._session.get(event.link)
            if res.status_code != 200:
                print(
                    f"Failed to fetch event details for {event.link}: [{res.status_code}] {res.text}"
                )
                continue
            soup = BeautifulSoup(res.text, "html.parser")
            period_elem = soup.select_one("p.f-c-btoPreorderPeriod")
            if not period_elem:
                continue
            period_text = period_elem.get_text(strip=True)
            event.periods = self._extract_periods(period_text)

        if filter_non_preorder:
            # Filter out events that do not have a valid start date
            events[:] = [e for e in events if e.periods]

    def _fetch_preorder_events(self) -> list[PreorderEvent]:
        """Fetches preorder events from the FMS list."""
        all_events: list[PreorderEvent] = []
        # Get only one page for now, shouldn't care about old posts...
        try:
            # Fetch the first page of preorder events
            events = self._fetch_articles(1)
            all_events.extend(events)
        except ValueError as e:
            print(f"Error fetching preorder events: {e}")
        return all_events

    def _fetch_articles(self, page: int) -> list[PreorderEvent]:
        """Fetches the articles from the FMS list."""
        while True:
            res = self._session.get(
                f"{FMS_BASE_URL}/search?view=preorderjson&type=article&q=*&page={page}"
            )
            if res.status_code == 200:
                break
            elif res.status_code == 429:
                print(f"Rate limit exceeded, waiting 5s before retrying page {page}...")
                time.sleep(5)
            else:
                raise ValueError(
                    f"Failed to fetch preorder events at page {page}: [{res.status_code}] {res.text}"
                )
        return [
            PreorderEvent(
                id=item["id"],
                title=item["title"],
                link=f"{FMS_BASE_URL}/blogs/{item['handle']}",
                periods=[],
            )
            for item in json.loads(fix_json(res.text))
        ]


if __name__ == "__main__":
    fms = FindMeStorePreorderList()

    events = fms.get_preorder_events()
    now = datetime.now()
    for event in events:
        active = False
        for period in event.periods:
            if period.end_time > now:
                active = True
                break
        if not active:
            continue
        print(f"{event.title} ({event.link})")
        for period in event.periods:
            print(
                f"  - Start: {period.start_time.strftime("%Y/%m/%d %H:%M")}, End: {period.end_time.strftime("%Y/%m/%d %H:%M")}"
            )
