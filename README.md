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

## Run tests

```bash
python3 -m pytest -q
```
