"""
lead_scraper_demo — Reddit lead scraper (stripped-down version).

This is a demo of the Reddit lead scraper from the Revenue Automation Playbook.
The full version (~2,050 lines) includes:
  - Multi-subreddit scraping with rate limiting
  - LLM-powered relevance scoring  
  - Pay rate extraction & normalization
  - Deduplication across runs
  - Digest generation (daily top-10 report)
  - Auto-restart & health monitoring

This demo shows the core pattern: scrape → filter → score → report.

Full playbook (3 automation systems + code):
  → https://gumroad.com/dillon/products/revenue-automation-playbook
"""

import json
import time
import re
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict

# ─── Simulated Reddit API (replace with real PRAW in production) ──
# In the full version, this uses: import praw
# reddit = praw.Reddit(client_id=..., client_secret=..., user_agent=...)

SAMPLE_POSTS = [
    {"title": "Looking for Python developer for automation project", "body": "Budget: $80-120/hr. Need someone who can build scrapers and APIs. 6 month contract.", "subreddit": "learnprogramming", "created": time.time() - 3600},
    {"title": "AI chatbot developer needed ASAP", "body": "Pay: $50/hr. Build a simple customer support chatbot. 2 week project.", "subreddit": "ChatGPT", "created": time.time() - 7200},
    {"title": "Anyone experienced with web scraping?", "body": "Have a small project, maybe $20-30. Not urgent.", "subreddit": "learnprogramming", "created": time.time() - 1800},
    {"title": "Full stack engineer for SaaS platform", "body": "Remote, $90-130/hr. React + Node + PostgreSQL. Looking for 3-6 month engagement.", "subreddit": "sidehustle", "created": time.time() - 5400},
    {"title": "Need help with my homework lol", "body": "Can someone just do my Python assignment? It's due tomorrow.", "subreddit": "learnprogramming", "created": time.time() - 900},
    {"title": "Code reviewer wanted — AI startup", "body": "$70-100/hr. Review PRs for our ML pipeline. 10-15 hrs/week.", "subreddit": "Python", "created": time.time() - 2700},
    {"title": "Anyone know how to center a div?", "body": "I've been trying for 3 hours help", "subreddit": "learnprogramming", "created": time.time() - 600},
    {"title": "Machine learning engineer for research project", "body": "Academic pay scale (~$45/hr). 4 months. NLP focus.", "subreddit": "MachineLearning", "created": time.time() - 4000},
]


# ─── DATA MODEL ───────────────────────────────────────────
@dataclass
class Lead:
    title: str
    body: str
    subreddit: str
    pay_min: float
    pay_max: float
    score: float
    tags: list
    created_at: str


# ─── THE FILTER: This is where the real value is ─────────
# In the full version, this uses an LLM for semantic scoring.
# This demo uses keyword heuristics to show the pattern.

KILL_WORDS = ["homework", "assignment", "due tomorrow", "center a div", "free", "volunteer"]
SKILL_WORDS = ["python", "api", "scraper", "automation", "ml", "ai", "react", "node", "full stack", "engineer"]
PAY_PATTERN = re.compile(r'\$(\d+)(?:\s*-\s*\$?(\d+))?(?:/hr|per hour)?', re.IGNORECASE)


def extract_pay(text: str) -> tuple[float, float]:
    """Pull pay range from post text."""
    match = PAY_PATTERN.search(text)
    if match:
        low = float(match.group(1))
        high = float(match.group(2)) if match.group(2) else low
        return low, high
    return 0, 0


def score_lead(post: dict) -> tuple[float, list]:
    """
    Score a post. Returns (score 0-100, list of matched tags).
    
    Scoring logic (simplified):
      - Has pay info?        +30 pts
      - Pay > $50/hr?        +20 pts  
      - Skill keyword match? +20 pts (up to 3 keywords)
      - Kill word present?   -100 pts (instant disqualify)
      - Recent (< 2hrs)?     +10 pts
    """
    text = (post["title"] + " " + post["body"]).lower()
    score = 0.0
    tags = []

    # Kill words → instant disqualify
    for kw in KILL_WORDS:
        if kw in text:
            return -1, ["DISQUALIFIED: " + kw]

    # Pay extraction
    pay_min, pay_max = extract_pay(post["body"])
    if pay_min > 0:
        score += 30
        tags.append(f"pay: ${pay_min}-${pay_max}/hr")
        if pay_min >= 50:
            score += 20
            tags.append("high-pay")

    # Skill match
    matched_skills = [kw for kw in SKILL_WORDS if kw in text][:3]
    score += len(matched_skills) * 7
    tags.extend(matched_skills)

    # Recency
    age_hours = (time.time() - post["created"]) / 3600
    if age_hours < 2:
        score += 10
        tags.append("fresh")

    return score, tags


def scrape_and_filter(posts: list) -> list[Lead]:
    """The core pipeline: posts → scored leads → sorted."""
    leads = []
    for post in posts:
        score, tags = score_lead(post)
        if score < 0:
            continue  # Disqualified

        pay_min, pay_max = extract_pay(post["body"])
        leads.append(Lead(
            title=post["title"],
            body=post["body"][:200] + "..." if len(post["body"]) > 200 else post["body"],
            subreddit=post["subreddit"],
            pay_min=pay_min,
            pay_max=pay_max,
            score=score,
            tags=tags,
            created_at=datetime.fromtimestamp(post["created"]).isoformat()
        ))

    # Sort by score descending
    leads.sort(key=lambda l: l.score, reverse=True)
    return leads


# ─── REPORT ───────────────────────────────────────────────
def generate_report(leads: list[Lead]) -> str:
    """Format the top leads into a readable digest."""
    lines = [
        "=" * 60,
        f"LEAD DIGEST — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Scanned: {len(SAMPLE_POSTS)} posts | Qualified: {len(leads)} leads",
        "=" * 60,
        ""
    ]
    for i, lead in enumerate(leads[:5], 1):  # Top 5
        lines.append(f"#{i} [{lead.score:.0f} pts] {lead.title}")
        lines.append(f"    Sub: r/{lead.subreddit}")
        lines.append(f"    Pay: ${lead.pay_min}-${lead.pay_max}/hr")
        lines.append(f"    Tags: {', '.join(lead.tags)}")
        lines.append(f"    Posted: {lead.created_at}")
        lines.append("")

    lines.append("─" * 60)
    lines.append("Full playbook with LLM scoring + digest automation:")
    lines.append("→ https://gumroad.com/dillon/products/revenue-automation-playbook")
    return "\n".join(lines)


# ─── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Scraping leads...\n")
    leads = scrape_and_filter(SAMPLE_POSTS)
    report = generate_report(leads)
    print(report)

    # Save to file
    output = Path("leads_output.json")
    output.write_text(json.dumps([asdict(l) for l in leads], indent=2))
    print(f"\nFull data saved to {output}")
