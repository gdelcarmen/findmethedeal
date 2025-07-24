"""Command‑line entry point for generating new affiliate niches.

This script ties together the database and the content agent.  It reads
command‑line arguments for the niche slug and one or more seed keywords,
checks whether the niche already exists, and if not, inserts it into
the database and triggers the agent to generate the site.  If the
niche already exists, it prints a message and exits.  In future
versions this module could also handle refresh scheduling and metrics
collection.
"""

from __future__ import annotations

import argparse
import sys

from .db import init_db, niche_exists, insert_niche, update_niche_status
from content_agent.agent import generate_niche_site


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and generate a niche if it does not exist."""
    parser = argparse.ArgumentParser(
        description="Generate a new affiliate site for a given niche."
    )
    parser.add_argument(
        "slug",
        help="The URL‑friendly slug for the niche (e.g. 'pickleball-shoes').",
    )
    parser.add_argument(
        "keywords",
        nargs="+",
        help="One or more seed keywords to guide content generation.",
    )
    args = parser.parse_args(argv)

    # Initialize the database table if it doesn't already exist
    init_db()

    if niche_exists(args.slug):
        print(f"Niche '{args.slug}' already exists. Skipping generation.")
        return

    print(f"Creating niche '{args.slug}' with keywords: {args.keywords}")
    insert_niche(args.slug, args.keywords)

    # Generate the site via the content agent
    try:
        generate_niche_site(args.slug, args.keywords)
        # Mark as published after successful generation
        update_niche_status(args.slug, "published")
    except Exception as exc:
        # In a real implementation you'd log this exception and update
        # status accordingly; for now just print and exit non‑zero.
        update_niche_status(args.slug, "error")
        print(f"Error generating niche '{args.slug}': {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()