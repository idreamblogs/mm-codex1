from fashion_industry_news_tool import build_google_news_rss_url, dedupe_items, parse_rss_items

SAMPLE_XML = b"""<?xml version='1.0' encoding='UTF-8'?>
<rss version='2.0'>
  <channel>
    <item>
      <title>Headline One</title>
      <link>https://example.com/1</link>
      <source>Source A</source>
      <pubDate>Mon, 26 Feb 2024 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Headline Two</title>
      <link>https://example.com/2</link>
      <source>Source B</source>
      <pubDate>Tue, 27 Feb 2024 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""


def test_build_google_news_rss_url():
    url = build_google_news_rss_url("fashion ecommerce")
    assert "q=fashion+ecommerce" in url
    assert "news.google.com/rss/search" in url


def test_parse_rss_items():
    items = parse_rss_items(SAMPLE_XML, topic="ecommerce")
    assert len(items) == 2
    assert items[0].title == "Headline One"
    assert items[1].source == "Source B"


def test_dedupe_items():
    items = parse_rss_items(SAMPLE_XML, topic="ecommerce")
    deduped = dedupe_items(items + [items[0]])
    assert len(deduped) == 2
