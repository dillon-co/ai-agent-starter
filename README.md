# ai-agent-starter

Free starter code from the [AI Agent Starter Kit](https://gumroad.com/dillon/products/ai-agent-starter-kit).

Two files. Both runnable. Both demonstrate real patterns — not pseudocode.

---

## What's in here

### `agent_example.py` — A minimal autonomous agent
The skeleton of a real agent. Has all 4 properties that separate an agent from a chatbot:

| Property | What it does here |
|----------|-------------------|
| **Event-driven trigger** | Loops on an interval (configurable) |
| **Persistent memory** | State saved to `agent_state.json` — survives restarts |
| **State modification** | Collects items, generates reports |
| **Autonomous looping** | Runs forever: perceive → decide → act → save → sleep |

```bash
python3 agent_example.py
# Runs forever. Ctrl+C to stop.
# Check agent_state.json and agent_log.txt after a few loops.
```

### `lead_scraper_demo.py` — A Reddit lead scraper
Stripped-down version of the scraper from the Revenue Automation Playbook. Shows the core pipeline:

```
Posts → Extract pay → Score (kill words, skill match, recency) → Sort → Report
```

```bash
python3 lead_scraper_demo.py
# Scores 8 sample posts, prints a ranked digest.
# Check leads_output.json for the full scored data.
```

---

## What's NOT in here (what the paid products add)

| This repo | Full products |
|-----------|---------------|
| Demo data (8 posts) | Live Reddit scraping via PRAW |
| Keyword scoring | LLM-powered semantic relevance scoring |
| Single agent pattern | 10 agent templates (cron, webhook, A2A, multi-agent) |
| Basic loop | MCP server toolkit, A2A communication, trust & security |
| — | Upwork Alert Engine (~2,050 lines) |
| — | B2B Pricing Monitor (~3,100 lines) |
| — | Daily digest generation & email delivery |

---

## Products

- **[AI Agent Starter Kit — $29](https://gumroad.com/dillon/products/ai-agent-starter-kit)**  
  Zero to autonomous agent in 48 hours. 10 chapters, 10 templates, MCP + A2A.

- **[Revenue Automation Playbook — $39](https://gumroad.com/dillon/products/revenue-automation-playbook)**  
  3 working automation systems. $0/month infrastructure. Real ROI.

- **[Full Stack Bundle — $69](https://gumroad.com/dillon/products/full-stack-bundle)**  
  Everything. Agents + revenue + crypto. Saves $27.

---

*Built by [Dillon](https://gumroad.com/dillon) · Austin, TX · Feb 2026*
