# Fashion & Retail Industry News Tool

A lightweight CLI tool that aggregates industry updates for:

- Fashion
- Design
- Styling
- Retail Tech
- Ecommerce

It uses Google News RSS queries (no API key required), deduplicates headlines, and supports text or JSON output.

## Quick start

```bash
python3 fashion_industry_news_tool.py --limit 10
```

### Filter topics

```bash
python3 fashion_industry_news_tool.py --topics fashion design ecommerce --limit 12
```

### JSON output

```bash
python3 fashion_industry_news_tool.py --json --per-topic 3
```

## Deployment options

Because this tool is a single Python script with only standard-library dependencies, deployment is simple.

### Option 1: Run on a Linux VM with cron (recommended)

1. Copy repository to server:

```bash
git clone <your-repo-url>
cd mm-codex1
```

2. Verify Python version (3.10+ recommended):

```bash
python3 --version
```

3. Smoke test:

```bash
python3 fashion_industry_news_tool.py --topics fashion ecommerce --limit 5
```

4. Create output directory:

```bash
mkdir -p /var/log/fashion-news
```

5. Add cron job (`crontab -e`) to run every hour and write JSON:

```cron
0 * * * * cd /path/to/mm-codex1 && /usr/bin/python3 fashion_industry_news_tool.py --json --limit 30 > /var/log/fashion-news/latest.json 2>> /var/log/fashion-news/error.log
```

This gives you a continuously refreshed `latest.json` feed.

### Option 2: Deploy as a Docker container

Add this `Dockerfile` at the repo root:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . /app
CMD ["python", "fashion_industry_news_tool.py", "--json", "--limit", "30"]
```

Build and run:

```bash
docker build -t fashion-news-tool .
docker run --rm fashion-news-tool
```

For scheduled runs in Kubernetes, use a `CronJob` that runs this container and writes output to object storage or a database.

### Option 3: GitHub Actions scheduled workflow

Use Actions to run hourly and store JSON as an artifact or commit it to a branch.

`.github/workflows/news-digest.yml` example:

```yaml
name: Fashion News Digest

on:
  schedule:
    - cron: "0 * * * *"
  workflow_dispatch:

jobs:
  run-digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Run tool
        run: python fashion_industry_news_tool.py --json --limit 30 > latest.json
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: latest-fashion-news
          path: latest.json
```

## Production hardening tips

- Add retry/backoff in `fetch_rss` for transient network issues.
- Persist previous fetches (SQLite/Postgres) to avoid reprocessing unchanged headlines.
- Export metrics (success/failure counts, fetch latency).
- If running behind a restricted network, configure outbound access to `news.google.com` RSS endpoints.

## Run tests

```bash
python3 -m pytest -q
```
