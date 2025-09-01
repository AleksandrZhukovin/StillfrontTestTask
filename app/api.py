import time
import requests

from app.db import Rate
from app.logger import setup_logger


logger = setup_logger(__name__)


class SweaRatesAPI:
    SERIES_URL = "https://api.riksbank.se/swea/v1/Series"
    RAW_RATES_URL = (
        "https://api.riksbank.se/swea/v1/Observations/Latest/"  # Must include series ID
    )
    SERIES_ID_KEY = "seriesId"
    RATE_DATE_FORMAT = "%Y-%m-%d"

    def __init__(
        self, requests_per_minute: int = 5, batch: int = None, insert_data: bool = False
    ):
        self.series_json = None
        self.min_interval = 60.0 / requests_per_minute
        self._last_request = 0
        self.batch = batch  # For testing, to get not all series but some
        self.insert_data = insert_data

    def _respect_rate_limit(self):
        """
        The API has restriction on 5 requests per minute for unauthenticated clients. https://www.riksbank.se/en-gb/statistics/interest-rates-and-exchange-rates/retrieving-interest-rates-and-exchange-rates-via-api/faq--the-api-for-interest-rates-and-exchange-rates/
        This method enforces the delay between requests.
        """
        now = time.monotonic()
        elapsed = now - self._last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_request = time.monotonic()

    def _request_with_retry(self, url: str, retry=True) -> dict:
        self._respect_rate_limit()
        logger.info(f"Request sent to {url}")
        r = requests.get(url)
        if r.status_code == 429:
            wait = int(r.headers.get("Retry-After", "15"))
            logger.warning(f"Rate limit exceeded, waiting {wait} seconds")
            time.sleep(wait)
            if retry:
                logger.info(f"Retrying to request {url}")
                return self._request_with_retry(url, retry=False)
        r.raise_for_status()
        return r.json()

    def get_series(self):
        self.series_json = self._request_with_retry(self.SERIES_URL)
        series_ids = [
            item[self.SERIES_ID_KEY]
            for item in self.series_json
            if self.SERIES_ID_KEY in item
        ]
        return series_ids[: self.batch] if self.batch else series_ids

    def get_rate(self, series_id: str):
        url = f"{self.RAW_RATES_URL}{series_id}"
        data = {"series_id": series_id}
        data.update(self._request_with_retry(url))
        if self.insert_data:
            Rate.create(**data)
        return data

    def get_latest_rates(self, series_ids: list[str]):
        return [self.get_rate(sid) for sid in series_ids]

    def request_data(self):
        series_ids = self.get_series()
        return self.get_latest_rates(series_ids)
