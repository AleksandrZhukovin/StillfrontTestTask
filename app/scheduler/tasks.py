from app.scheduler.celery import celery
from app.api import SweaRatesAPI
from app.logger import setup_logger


logger = setup_logger(__name__)


@celery.task
def request_and_store_rates_data():
    logger.info("Starting requesting rates data")
    api = SweaRatesAPI(insert_data=True)
    api.request_data()
    logger.info("Finished requesting rates data")


@celery.task
def test_request(requests_per_minute=60, batch=3, insert_data=True):
    """
    This method is used to manually call to test API works.
    """
    from app.db import Rate
    from app.api import SweaRatesAPI

    def print_last_rates(title):
        rates = Rate.query_all()
        print(f"\n=== {title} ===")
        if not rates:
            print("No rates in DB yet")
            return

        last_three = rates[-5:]
        for r in last_three:
            print(
                f"id={r.id}, series_id={r.series_id}, "
                f"value={r.value}, date={r.date}, "
                f"created_at (UTC)={r.created_at}"
            )

    print_last_rates("Rates BEFORE API request")

    api = SweaRatesAPI(
        requests_per_minute=requests_per_minute, batch=batch, insert_data=insert_data
    )
    data = api.request_data()
    print(f"\nRequested {len(data)} items")

    print_last_rates("Rates AFTER API request")
