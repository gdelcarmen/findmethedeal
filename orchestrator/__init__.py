"""Initialization for the orchestrator package.

This package contains the database helpers, the command-line entry point and
 task definitions used to manage the lifecycle of affiliate niches.  The
 orchestrator is responsible for deciding when a new niche should be
 generated, scheduling refreshes and persisting metadata.  See README.md
 for details on how to use these modules.
"""

from .db import init_db, niche_exists, insert_niche  # re-export for convenience
