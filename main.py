"""36kr Daily Brief — Main Script
Scrapes 36kr → Calls Claude API → Sends email.
"""

import os
import sys
import anthropic
from scraper import scrape_daily_articles
from emailer import send_brief_email, send_error_email
from brief_spec import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def generate_brief(articles_content: str) -> str:
    """Call Claude API to generate the brief from scraped articles."""
    client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var
    
    user_prompt = USER_PROMPT_TEMPLATE.format(articles_content=articles_content)
    
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    
    return response.content[0].text


def main():
    print("=" * 50)
    print("36kr Daily Brief — Starting")
    print("=" * 50)
    
    try:
        # Step 1: Scrape 36kr
        print("\n📡 Scraping 36kr.com...")
        articles_content = scrape_daily_articles(max_articles=8)
        
        if "NO RELEVANT ARTICLES" in articles_content:
            print("No relevant articles found today")
            brief = "Quiet day on 36kr — nothing matching your target categories (AI consumer apps, content platforms, AI video, big tech startups). Will check again tomorrow."
        else:
            # Step 2: Generate brief via Claude
            print("\n🤖 Generating brief via Claude API...")
            brief = generate_brief(articles_content)
        
        # Step 3: Send email
        print("\n📧 Sending email...")
        send_brief_email(brief)
        
        print("\n✅ Done!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        try:
            send_error_email(str(e))
        except Exception as email_err:
            print(f"Failed to send error email: {email_err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
