# Handles arg parsing
# Entry point for gleaning
import argparse
import logging

from .helpers import RateLimiter
from .scraper import Gleaner


def main():
    # Parse url and output file
    parser = argparse.ArgumentParser()

    parser.add_argument("url")
    parser.add_argument(
        "-o",
        "--output",
        default="urls.txt",
        help="Output file for urls (default: urls.txt)",
    )
    parser.add_argument(
        "-r",
        "--rps",
        default=10,
        help="Maximum requests per second",
        type=int,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Get rate limiter
    rate_limiter = RateLimiter(rps=args.rps)

    # Define verbosity
    if args.verbose:
        logging.basicConfig(level="INFO")

    # Glean
    print(f"Gleaning: {args.url}")
    gleaner = Gleaner(start_url=args.url, rate_limiter=rate_limiter)
    pages = gleaner.scrape()
    pages = sorted(pages)

    # Store obtained pages
    with open(args.output, "w") as file:
        for page in pages:
            file.write(page + "\n")
    print(f"Output saved to {args.output}")


if __name__ == "__main__":
    main()
