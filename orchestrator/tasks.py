"""Task definitions for asynchronous execution.

In a production deployment you will likely want to offload content
generation, site builds, deployments and refreshes to a durable
workflow engine such as [Celery](https://docs.celeryq.dev/),
[Temporal](https://temporal.io/) or [Airflow](https://airflow.apache.org/).
This module provides stubs for such tasks.  If Celery is installed and
configured, the `@app.task` decorator can be uncommented to make
`generate_niche_task` run asynchronously.
"""

from __future__ import annotations

# Example Celery configuration (commented out by default)
# from celery import Celery
# app = Celery('findmethedeal', broker='redis://localhost:6379/0')

from orchestrator.db import insert_niche, niche_exists, update_niche_status
from content_agent.agent import generate_niche_site


def generate_niche_task(slug: str, keywords: list[str]) -> None:
    """Wrapper task to generate a niche asynchronously.

    This function inserts the niche into the database (if necessary) and
    calls the content agent.  Hook it into your workflow engine of
    choice to run generation jobs on a schedule or in response to
    user input.
    """
    if niche_exists(slug):
        return
    insert_niche(slug, keywords)
    try:
        generate_niche_site(slug, keywords)
        update_niche_status(slug, "published")
    except Exception:
        update_niche_status(slug, "error")


__all__ = ["generate_niche_task"]