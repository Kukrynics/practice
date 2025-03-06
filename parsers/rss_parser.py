# parsers/rss_parser.py
import feedparser
from database.queries import insert_news

def parse_rss(url):
    feed = feedparser.parse(url)
    for entry in feed.entries:
        title = entry.title
        content = entry.summary
        source = 'RSS'
        url = entry.link
        published_at = entry.published
        insert_news(title, content, source, url, published_at)
