"""High‑level content generation for affiliate niches.

This module exposes functions that coordinate calls to large language
models and media APIs to produce outlines, full articles and media
assets.  External services are abstracted into individual helper
functions so they can be stubbed during development or replaced with
other providers.  By default, OpenAI’s ChatCompletion API is used for
text generation; set the `OPENAI_API_KEY` environment variable or
modify `call_llm` to integrate with another model.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, List, Dict, Any

import openai


# Load environment variables (you can also use python‑dotenv)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


def call_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4o") -> str:
    """Call a chat model with a system and user prompt and return the response.

    Args:
        system_prompt (str): The system prompt that sets the context and tone.
        user_prompt (str): The user’s instruction or input message.
        model (str, optional): The model name. Defaults to "gpt-4o".

    Returns:
        str: The assistant’s reply content.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["choices"][0]["message"]["content"].strip()


def load_prompt(name: str) -> str:
    """Load a prompt template from the `prompts` directory."""
    prompts_dir = Path(__file__).resolve().parent / "prompts"
    with open(prompts_dir / name, "r", encoding="utf-8") as f:
        return f.read()


def generate_outline(slug: str, keywords: Iterable[str]) -> Dict[str, Any]:
    """Generate a structured outline for the given niche.

    Args:
        slug (str): Niche slug for naming purposes.
        keywords (Iterable[str]): Seed keywords.

    Returns:
        dict: A dictionary with keys `sections`, `faqs` and `products`.
    """
    system_prompt = "You are an expert content strategist."
    outline_prompt = load_prompt("outline_prompt.txt")
    user_content = f"niche: {slug}\nkeywords: {', '.join(keywords)}"
    response = call_llm(system_prompt, outline_prompt + "\n\n" + user_content)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # If the model fails to return valid JSON, fall back to a simple outline
        return {
            "sections": [{"title": "Introduction", "subsections": []}],
            "faqs": [],
            "products": [],
        }


def generate_section(section: Dict[str, Any], products: List[str]) -> str:
    """Generate prose for a single outline section.

    Args:
        section (dict): A section dict with a title and optional bullet points.
        products (list[str]): Product identifiers to mention.

    Returns:
        str: Markdown content for the section.
    """
    system_prompt = "You are a helpful writer producing affiliate content."
    section_prompt = load_prompt("section_prompt.txt")
    # Compose a structured user message
    bullet_points = section.get("bullet_points", [])
    user_content = json.dumps({
        "title": section["title"],
        "bullet_points": bullet_points,
        "products": products,
    }, indent=2)
    response = call_llm(system_prompt, section_prompt + "\n\n" + user_content)
    return response


def polish_copy(draft: str) -> str:
    """Run the Grammarly/Spacy polishing step via the LLM.

    Args:
        draft (str): The unpolished Markdown text.

    Returns:
        str: Polished Markdown with improved tone and citation placeholders.
    """
    system_prompt = "You are an editor improving AI‑generated prose."
    polish_prompt = load_prompt("polish_prompt.txt")
    response = call_llm(system_prompt, polish_prompt + "\n\n" + draft)
    return response


def fetch_images(keywords: Iterable[str], count: int = 3) -> List[str]:
    """Fetch royalty‑free images matching the given keywords.

    The default implementation returns placeholder filenames.  You can
    integrate the Unsplash API or OpenAI’s image models here.  If you
    choose to use an API, remember to respect license terms and store
    proof of provenance as suggested by the reference design.

    Args:
        keywords (Iterable[str]): Keywords to search for images.
        count (int, optional): Number of images to fetch. Defaults to 3.

    Returns:
        list[str]: List of local image filenames.
    """
    # Placeholder implementation: return generic file names
    return [f"image_{i + 1}.jpg" for i in range(count)]


def generate_niche_site(slug: str, keywords: Iterable[str]) -> None:
    """Generate a new niche site by orchestrating outline, section and polish steps.

    This function creates a directory under `sites/<slug>` and writes an
    `index.md` file containing the article.  In a real implementation
    you would create multiple pages, copy the Astro template and
    write JSON‑LD metadata.  For demonstration purposes we assemble
    a single Markdown file.
    """
    slug = slug.strip().lower()
    site_dir = Path(__file__).resolve().parents[1] / "sites" / slug
    site_dir.mkdir(parents=True, exist_ok=True)

    outline = generate_outline(slug, keywords)
    sections = outline.get("sections", [])
    faqs = outline.get("faqs", [])
    products = outline.get("products", [])

    # Generate content for each section
    article_parts: List[str] = []
    for section in sections:
        # The LLM may not return bullet points; default to using the title as a bullet
        content = generate_section(section, products)
        polished = polish_copy(content)
        article_parts.append(f"## {section['title']}\n\n" + polished.strip() + "\n")

    # Assemble FAQs
    faq_md = ""
    if faqs:
        faq_md += "\n## Frequently Asked Questions\n\n"
        for q in faqs:
            faq_md += f"**{q}**\n\n" + "[Answer pending]\n\n"

    # Write the Markdown file
    with open(site_dir / "index.md", "w", encoding="utf-8") as f:
        title = slug.replace("-", " ").title()
        f.write(f"# {title}\n\n")
        for part in article_parts:
            f.write(part + "\n")
        f.write(faq_md)

    print(f"Generated content for niche '{slug}' in {site_dir}")