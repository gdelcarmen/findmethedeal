# FindMeTheDeal Affiliate‑Site Factory

This repository contains a skeleton implementation of a multi‑niche affiliate‑site generator designed around the high‑level architecture described in the accompanying reference design.  It is intended to automate the research, content creation and deployment of small, targeted affiliate sites while staying within Google’s 2025 policies on AI and scaled content.

## Why this project?

Google’s June 2025 core update introduced strict spam‑policies against **scaled content abuse**, where unoriginal, low‑value pages are mass‑produced for search manipulation【748452214409322†L651-L664】.  Affiliate pages that simply copy merchant descriptions are considered **thin affiliation**; Google recommends adding unique value via price information, original product reviews and comparisons【748452214409322†L770-L786】.  Analysis of pages that improved after the update highlights that successful sites offer super helpful content with first‑hand experience, clear structure and useful visuals【960291052940405†L60-L66】.

This project therefore focuses on:

* Tracking niches in a small database so that no topic is duplicated.
* Generating outlines and articles through a structured prompt chain and adding tables, statistics and external citations.
* Producing clean, static sites using [Astro](https://astro.build) and injecting FAQ and Product schemas for SEO.
* Adding affiliate disclosures, human review hooks and refresh cadences to comply with Google and FTC guidance.

## Repository structure

```
findmethedeal/
├── orchestrator/        # DB access, task scheduling and CLI entry point
│   ├── __init__.py
│   ├── db.py            # SQLite helpers for the `niches` table
│   ├── orchestrator.py  # CLI that registers niches and triggers the agent
│   └── tasks.py         # Stub for Celery/Temporal task definitions
├── content_agent/       # Agent that interacts with language models and media APIs
│   ├── __init__.py
│   ├── agent.py         # High‑level functions to generate outlines and pages
│   └── prompts/         # Prompt templates for the LLM
│       ├── outline_prompt.txt
│       ├── section_prompt.txt
│       └── polish_prompt.txt
├── templates/
│   └── site_template/   # Minimal Astro starter used as a base for new sites
│       ├── package.json
│       ├── astro.config.mjs
│       └── src/
│           ├── layouts/
│           │   └── BaseLayout.astro
│           └── pages/
│               └── index.astro
├── sites/               # Generated sites appear here as `sites/<slug>`
├── .github/
│   └── workflows/
│       └── build.yml    # GitHub Actions workflow to build and deploy
├── requirements.txt     # Python dependencies
├── LICENSE              # MIT license for this repository
├── README.md            # This file
└── .gitignore
```

### Orchestrator

The orchestrator layer maintains a simple SQLite database of niches and coordinates calls to the content agent.  It exposes a CLI entry point:

```
python -m orchestrator.orchestrator <slug> <keyword> [<keyword> …]
```

If the slug is not already in the database, a new row is inserted with status `planned` and the content agent is invoked to generate a site.  Future enhancements could integrate Celery, Temporal or a cron job to manage refresh cadences and track metrics.

### Content agent

The agent script encapsulates calls to large language models (LLMs) and media APIs.  It follows a multi‑step prompt chain: generate an outline, expand each section into prose, enrich with statistics and citations, fetch royalty‑free images and finally polish the text.  Calls to external services (OpenAI, Grammarly, Unsplash, etc.) are stubbed out so that you can add API keys as environment variables.

The agent writes Markdown files into `sites/<slug>/` and returns control to the orchestrator.  You can extend it to inject JSON‑LD for FAQPage and Product schema and to build the internal link graph.

### Static site template

Under `templates/site_template` you’ll find a minimal [Astro](https://astro.build) project configured to use the `@astrojs/sitemap` integration.  The `BaseLayout.astro` defines a simple HTML structure with SEO meta tags, a byline and a disclosure component.  When a new niche is generated, the agent copies this template into `sites/<slug>` and writes the generated Markdown into the appropriate folder (`src/pages/`).

### GitHub Actions workflow

A sample workflow (`.github/workflows/build.yml`) is provided to demonstrate how you might build and deploy your sites.  It checks out the code, installs Node.js and Python dependencies, builds each site in `sites/`, commits the generated `dist` directories and can be extended to deploy to Netlify, Vercel or AWS S3/CloudFront.

## Getting started

1. **Install dependencies**

   ```bash
   cd findmethedeal
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Initialize the database**

   The orchestrator will automatically create the `niches` table when first run.  You can also run:

   ```bash
   python -c "from orchestrator.db import init_db; init_db()"
   ```

3. **Generate your first niche**

   ```bash
   python -m orchestrator.orchestrator pickleball-shoes "pickleball shoes" "best court shoes" "top pickleball sneakers"
   ```

4. **Build the site**

   From within `sites/pickleball-shoes`, install the Node dependencies and run Astro:

   ```bash
   cd sites/pickleball-shoes
   npm install
   npx astro build
   ```

   The compiled site will be in `dist/`.  A CDN or Netlify deployment can serve this folder.

5. **Deployment and monitoring**

   To deploy automatically when a new site is generated, configure the provided GitHub Actions workflow with your hosting provider’s credentials.  You can also integrate Google Search Console and your affiliate networks’ reporting APIs to monitor traffic, revenue and SEO health.

## Extending this project

* **Memory & Scheduling** – integrate a proper workflow engine like Temporal or Celery to queue new niches and schedule refreshes.  Add a Streamlit dashboard to inspect niche status, traffic and revenue metrics.
* **Enhanced prompts** – refine the prompt chain to insert evidence, tables and citations.  Use a language tool API and Spacy to polish copy and sanity‑check entities.  Always ensure that each article provides unique analysis or comparison to comply with Google’s spam policies【748452214409322†L651-L664】.
* **Affiliate integration** – add wrappers around the Amazon Product Advertising API, Impact and CJ with caching.  Inject FTC disclosures automatically.
* **SEO hardening** – implement an internal link graph, alt‑text for images, JSON‑LD for FAQ and product schemas and an automated `sitemap.xml`.
* **Governance** – set guardrails such as limiting new niches per day and requiring manual approval before publishing.

## License

This project is released under the MIT License – see the [LICENSE](LICENSE) file for details.