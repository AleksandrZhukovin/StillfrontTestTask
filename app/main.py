from app.scheduler.tasks import test_request


def main(requests_per_minute, batch, insert_data):
    """
    Run this script to test the API and DB on a small batch.

    Args:
        requests_per_minute (int): Number of API requests per minute
        batch (int): Number of rates to request
        insert_data (bool): Whether to insert rates into the DB

    Returns:
        list: List of requested rates
    """
    data = test_request(requests_per_minute, batch, insert_data)
    print("Returned rates:", data)


if __name__ == "__main__":
    main(requests_per_minute=60, batch=3, insert_data=True)
