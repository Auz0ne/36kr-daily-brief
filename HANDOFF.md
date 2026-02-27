# 36kr Daily Brief — Claude Code Handoff

## What This Is
An automated daily email that delivers a curated Chinese tech news brief from 36kr.com, personalized for Antoine's context (AI consumer apps, content platforms, career intelligence).

## Architecture
```
GitHub Actions (cron, 7am Paris / 6am UTC)
  → Python script
    → Scrapes 36kr.com homepage + key articles
    → Calls Claude API (Sonnet) with brief spec + scraped content
    → Formats as HTML email
    → Sends via SMTP (self-sent: Antoine → Antoine)
```

## Files to Create

### 1. `.github/workflows/daily-brief.yml`
GitHub Actions workflow with:
- Cron schedule: `0 6 * * *` (6am UTC = 7am CET Paris)
- Manual trigger (`workflow_dispatch`) for testing
- Python 3.11+ setup
- Install dependencies
- Run `main.py`
- Secrets needed: `ANTHROPIC_API_KEY`, `SMTP_EMAIL`, `SMTP_PASSWORD`

### 2. `main.py`
Main script. Steps:
1. Fetch `https://36kr.com/` and extract article links + headlines
2. Filter for relevant categories (AI, content platforms, big tech startups, etc.)
3. Fetch top 5-8 article pages for full content
4. Call Claude API (claude-sonnet-4-5-20250929) with the BRIEF_SPEC prompt + article content
5. Format Claude's response as HTML email
6. Send via SMTP

### 3. `scraper.py`
36kr scraper module:
- Fetch homepage, parse with BeautifulSoup
- Extract article titles, URLs, brief descriptions
- Fetch individual articles for full text
- Handle Chinese content properly (UTF-8)
- Return structured list of articles
- NOTE: 36kr is a Chinese site, content is in Chinese. Claude can read Chinese and will output the brief in English.

### 4. `emailer.py`
Email sending module:
- Uses `smtplib` + `email.mime`
- HTML email with clean formatting
- Self-sent (FROM = TO = Antoine's email)
- Subject line: `🇨🇳 36kr Daily Brief — {date}` 
- SMTP config: Gmail App Password (port 587, TLS)

### 5. `brief_spec.py`
Contains the Claude API prompt/spec as a constant string. See BRIEF_SPEC section below.

### 6. `requirements.txt`
```
anthropic
beautifulsoup4
requests
lxml
```

## BRIEF_SPEC (Claude API System Prompt)

```
You are a senior tech analyst producing a daily brief from Chinese tech news (36kr.com) for a product/strategy professional working in consumer app publishing in Paris.

RECIPIENT CONTEXT:
- Works at Voodoo (Paris) in consumer app publishing
- Building an AI Personal Trainer iOS app
- Developing "Colony One" — AI-generated serialized content for TikTok
- Targeting senior product/strategy roles at content platforms, AI companies, European scale-ups
- Expertise: product strategy, growth, AI across health/fitness, media, social

TIER 1 — ALWAYS COVER:
- AI Consumer Apps: Doubao, Qwen, Yuanbao growth tactics, monetization, UX, MAU data
- Content Platform Moves: WeChat, Xiaohongshu, Douyin features, creator tools, algorithm changes
- AI-Generated Content/Video: Seedance, Kling, Vidu, AI short drama, generative video

TIER 2 — COVER WHEN RELEVANT:
- Big Tech Exec Startups: ex-ByteDance/Alibaba/Tencent founders, early-stage raises
- EU/Global Expansion: Chinese AI apps going international, cross-border plays
- AI + Health/Fitness: AI fitness apps, health tech, connected wellness

TIER 3 — LEAN (1-2 items max):
- AI Super-App War: agentic search, AI commerce, platform distribution
- AI Hardware + Devices: consumer AI devices, product-content-hardware convergence

EXCLUDED: Pure e-commerce logistics, dating apps, deep enterprise SaaS, chip/infra unless consumer-facing, automotive unless AI-specific

FORMAT:
- 10-minute read (~1500-2000 words)
- 3-6 stories, each with: 2-3 sentence summary → 1 strategic take tied to recipient's context
- End with "So What?" section: 3-5 bullet synthesis (career positioning, AI PT app, Colony One)
- Tone: Direct, analytical, no filler
- Write in English, even though sources are Chinese
- If a day has no relevant stories, say so briefly rather than forcing weak content
```

## Environment Variables / GitHub Secrets

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key |
| `SMTP_EMAIL` | Antoine's Gmail address (sender = receiver) |
| `SMTP_PASSWORD` | Gmail App Password (NOT regular password) |

## Gmail App Password Setup
Antoine needs to:
1. Go to https://myaccount.google.com/apppasswords
2. Generate an app password for "Mail"
3. Use that 16-char password as `SMTP_PASSWORD`
4. 2FA must be enabled on the Google account

## Testing
- Use `workflow_dispatch` to trigger manually from GitHub Actions tab
- Or run locally: `ANTHROPIC_API_KEY=xxx SMTP_EMAIL=xxx SMTP_PASSWORD=xxx python main.py`

## Edge Cases to Handle
- 36kr site down → send brief email saying "36kr unavailable today, will retry tomorrow"
- No relevant articles → send short email: "Quiet day on 36kr, nothing matching your categories"
- Claude API error → retry once, then send error notification email
- Scraping blocked → try with different User-Agent headers, fall back to error email

## Cost
- Claude Sonnet API: ~$0.01-0.03 per brief (input: scraped articles, output: ~2000 words)
- GitHub Actions: free tier (2000 min/month, this uses <5 min/day)
- SMTP: free via Gmail
