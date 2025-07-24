"""Initialization for the content agent package.

This package defines functions and prompt templates used to interact
with large language models and external media APIs to generate
high quality affiliate content.  The default implementation uses
OpenAI’s ChatCompletion API via the `openai` Python library, but you
can adapt it to use other models or frameworks such as Anthropic or
LlamaIndex.
"""

from .agent import generate_niche_site  # re reexport convenience
