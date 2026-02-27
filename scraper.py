"""36kr.com scraper — fetches articles via native RSS feed."""

import requests
from bs4 import BeautifulSoup
from lxml import etree
from typing import List, Dict

RSS_URL = "https://36kr.com/feed"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# Keywords that signal relevance to our categories (Chinese + English)
RELEVANCE_KEYWORDS = [
    # AI consumer apps
    "豆包", "doubao", "通义", "qwen", "元宝", "yuanbao", "AI助手", "AI搜索",
    "大模型", "智能体", "agent", "AI应用", "月活", "MAU", "DAU",
    # Content platforms
    "微信", "wechat", "小红书", "xiaohongshu", "抖音", "douyin", "快手",
    "创作者", "creator", "内容平台", "直播", "短视频",
    # AI video/content generation
    "AI视频", "AI生成", "Seedance", "Kling", "可灵", "Vidu", "AI短剧",
    "AIGC", "生成式", "Sora", "视频生成", "图像生成",
    # Big tech exec startups
    "离职创业", "前字节", "前阿里", "前腾讯", "前美团", "融资", "创始人",
    # Health/fitness AI
    "健身", "健康", "fitness", "运动", "AI健身", "智能穿戴",
    # AI hardware
    "AI硬件", "智能设备", "AI手机", "AI眼镜", "具身智能",
    # Super-app / agentic
    "超级应用", "AI搜索", "agentic", "AI电商",
]


def fetch_rss_articles() -> List[Dict]:
    """Fetch 36kr RSS feed and extract articles with full text."""
    resp = requests.get(RSS_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    resp.encoding = "utf-8"

    root = etree.fromstring(resp.content)
    articles = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()
        description_html = item.findtext("description", "").strip()

        # Extract plain text from the HTML description
        if description_html:
            soup = BeautifulSoup(description_html, "lxml")
            content = soup.get_text(separator="\n", strip=True)
        else:
            content = ""

        if title and link:
            articles.append({
                "title": title,
                "url": link,
                "pub_date": pub_date,
                "description": content[:200],  # Short desc for relevance scoring
                "content": content[:3000],      # Full text, capped for Claude context
            })

    return articles


def score_relevance(article: Dict) -> int:
    """Score how relevant an article is to our categories."""
    text = f"{article['title']} {article.get('description', '')} {article.get('content', '')[:500]}".lower()
    score = 0
    for kw in RELEVANCE_KEYWORDS:
        if kw.lower() in text:
            score += 1
    return score


def filter_relevant(articles: List[Dict], min_score: int = 1, max_articles: int = 10) -> List[Dict]:
    """Filter and rank articles by relevance."""
    scored = [(score_relevance(a), a) for a in articles]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [a for score, a in scored if score >= min_score][:max_articles]


def scrape_daily_articles(max_articles: int = 8) -> str:
    """Main entry point: fetch 36kr RSS and return formatted article content for Claude."""
    print("Fetching 36kr RSS feed...")
    all_articles = fetch_rss_articles()
    print(f"Found {len(all_articles)} articles in RSS feed")

    relevant = filter_relevant(all_articles, max_articles=max_articles)
    print(f"Filtered to {len(relevant)} relevant articles")

    if not relevant:
        return "NO RELEVANT ARTICLES FOUND TODAY on 36kr matching the target categories."

    output_parts = []
    for i, article in enumerate(relevant):
        output_parts.append(
            f"### Article {i+1}: {article['title']}\n"
            f"URL: {article['url']}\n"
            f"Published: {article['pub_date']}\n\n"
            f"{article['content']}\n"
        )

    return "\n---\n\n".join(output_parts)


if __name__ == "__main__":
    # Test scraper standalone
    result = scrape_daily_articles()
    print("\n" + "=" * 60)
    print(result[:2000])
