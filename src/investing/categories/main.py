import argparse

from async_client import Client
from get_logger import get_logger
from worker import worker


def main():
    parser = argparse.ArgumentParser(
        description="Async client for Investing news parser"
    )
    parser.add_argument("urls_file", help="File containing Categories and URLs")
    parser.add_argument(
        "-c", "--task_count", default=3, type=int, help="Count of asynchronous requests"
    )
    parser.add_argument("-l", "--logging", action="store_true", help="Enable logging")

    args = parser.parse_args()
    if args.logging:
        logger = get_logger()
    else:
        logger = None

    client = Client(
        db=None,
        task_count=args.task_count,
        urls_file=args.urls_file,
        worker=worker,
        logger=logger,
    )
    client.start()


if __name__ == "__main__":
    main()
