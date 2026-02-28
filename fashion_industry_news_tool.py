#!/usr/bin/env python3
"""Fashion, design, styling, retail tech, and ecommerce news aggregator.

This CLI fetches headlines from Google News RSS topic searches and prints
ranked, de-duplicated updates.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import textwrap
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Iterable

TOPICS = {
    "fashion": "fashion industry",
    "design": "fashion design trends",
    "styling": "personal styling trends",
    "retail-tech": "retail technology",
    "ecommerce": "fashion ecommerce",
}


@dataclasses.dataclass(frozen=True)
class NewsItem:
    topic: str
    title: str
    source: str
    link: str
    published: datetime | None


def build_google_news_rss_url(query: str, language: str = "en-US", region: str = "US") -> str:
    """Build a Google News RSS URL for a search query."""
    encoded_query = urllib.parse.quote_plus(query)
    return (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}&hl={language}&gl={region}&ceid={region}:{language.split('-')[0]}"
    )


def fetch_rss(url: str, timeout: int = 15) -> bytes:
    """Download RSS XML bytes from URL."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def parse_rss_items(xml_data: bytes, topic: str) -> list[NewsItem]:
    """Parse RSS XML into NewsItem rows."""
    root = ET.fromstring(xml_data)
    items: list[NewsItem] = []

    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        source = (item.findtext("source") or "Unknown").strip()
        pub_date_raw = (item.findtext("pubDate") or "").strip()

        published: datetime | None = None
        if pub_date_raw:
            try:
                published = parsedate_to_datetime(pub_date_raw)
            except (TypeError, ValueError):
                published = None

        if title and link:
            items.append(
                NewsItem(
                    topic=topic,
                    title=title,
                    source=source,
                    link=link,
                    published=published,
                )
            )

    return items


def dedupe_items(items: Iterable[NewsItem]) -> list[NewsItem]:
    """Remove duplicates by normalized title and link."""
    seen: set[tuple[str, str]] = set()
    result: list[NewsItem] = []
    for item in items:
        key = (item.title.lower(), item.link)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def fetch_news(selected_topics: list[str], per_topic: int) -> list[NewsItem]:
    """Fetch and parse news across selected topics."""
    combined: list[NewsItem] = []
    for topic in selected_topics:
        query = TOPICS[topic]
        url = build_google_news_rss_url(query)
        xml = fetch_rss(url)
        combined.extend(parse_rss_items(xml, topic=topic)[:per_topic])

    combined = dedupe_items(combined)
    combined.sort(key=lambda x: x.published or datetime.min, reverse=True)
    return combined


def render_text(items: list[NewsItem], max_items: int) -> str:
    """Render human-readable digest."""
    if not items:
        return "No news items found."

    lines: list[str] = []
    for idx, item in enumerate(items[:max_items], start=1):
        published = item.published.isoformat() if item.published else "unknown-date"
        lines.append(
            textwrap.dedent(
                f"""
                {idx}. {item.title}
                   topic: {item.topic}
                   source: {item.source}
                   published: {published}
                   link: {item.link}
                """
            ).strip()
        )
    return "\n\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Get fashion/design/styling/retail-tech/ecommerce industry news updates."
    )
    parser.add_argument(
        "--topics",
        nargs="+",
        choices=sorted(TOPICS.keys()),
        default=sorted(TOPICS.keys()),
        help="Topics to include (default: all).",
    )
    parser.add_argument("--per-topic", type=int, default=5, help="Max items fetched per topic.")
    parser.add_argument("--limit", type=int, default=15, help="Max items in final output.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        news = fetch_news(args.topics, per_topic=args.per_topic)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to fetch news: {exc}", file=sys.stderr)
        return 1

    if args.json:
        payload = [
            {
                "topic": item.topic,
                "title": item.title,
                "source": item.source,
                "published": item.published.isoformat() if item.published else None,
                "link": item.link,
            }
            for item in news[: args.limit]
        ]
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(news, max_items=args.limit))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
