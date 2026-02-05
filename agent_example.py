"""
ai-agent-starter — A minimal autonomous agent skeleton.

This is the free sample from the AI Agent Starter Kit.
It demonstrates the 4 core properties of a real agent:
  1. Event-driven triggers (not human input)
  2. Persistent memory (state survives restarts)
  3. State modification (writes to external systems)
  4. Autonomous looping (runs itself, no human per iteration)

Full kit (10 chapters, 10 agent templates, MCP + A2A):
  → https://gumroad.com/dillon/products/ai-agent-starter-kit
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────
STATE_FILE = Path("agent_state.json")
LOG_FILE   = Path("agent_log.txt")
INTERVAL_SECONDS = 60  # How often the agent loops (trigger interval)


# ─── MEMORY: Persistent state across restarts ────────────
def load_state() -> dict:
    """Load state from disk. Survives restarts."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"runs": 0, "last_run": None, "items_collected": []}


def save_state(state: dict):
    """Write state to disk after every loop."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ─── LOGGING ──────────────────────────────────────────────
def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ─── PERCEPTION: What does the agent "see"? ──────────────
def perceive() -> dict:
    """
    This is where your agent reads the world.
    Replace this with: API calls, file reads, webhook payloads, etc.
    
    Example real implementations:
      - Reddit API → scrape new posts in a subreddit
      - File watcher → detect new files in a directory  
      - Webhook → receive events from another service
    """
    # Demo: just return the current time as a "signal"
    return {
        "timestamp": datetime.now().isoformat(),
        "signal": "heartbeat",
        # In production, this would be real data:
        # "new_posts": reddit_api.get_new(subreddit="learnprogramming", limit=10),
    }


# ─── DECISION: What should the agent do? ─────────────────
def decide(perception: dict, state: dict) -> str:
    """
    The agent's brain. Takes what it sees + its memory, returns an action.
    
    In the full kit, this is where LLM routing happens:
      - Simple tasks → local model (fast, cheap)
      - Complex tasks → cloud model (capable)
      - Ambiguous tasks → human-in-the-loop checkpoint
    """
    if state["runs"] == 0:
        return "initialize"
    elif len(state["items_collected"]) < 5:
        return "collect"
    else:
        return "report"


# ─── ACTION: Do something in the world ───────────────────
def act(action: str, perception: dict, state: dict) -> dict:
    """
    Execute the decision. This modifies external state.
    
    Replace with real actions:
      - POST to an API
      - Write a file
      - Send a notification
      - Call an LLM with a prompt
    """
    if action == "initialize":
        log("Agent initialized. Starting collection loop.")
        state["items_collected"] = []
        return state

    elif action == "collect":
        # Demo: "collect" the timestamp as an item
        item = {"collected_at": perception["timestamp"], "data": "sample_item"}
        state["items_collected"].append(item)
        log(f"Collected item #{len(state['items_collected'])}: {item['data']}")
        return state

    elif action == "report":
        log(f"REPORT: Collected {len(state['items_collected'])} items total.")
        log("Report would go here: send email, post to Slack, update dashboard...")
        # In production: actually send the report somewhere
        # Reset for next cycle
        state["items_collected"] = []
        return state

    return state


# ─── THE LOOP: The heart of any real agent ───────────────
def run():
    """
    The autonomous loop. This is what makes it an AGENT, not a script.
    
    Pattern:
      1. Load state (memory from last run)
      2. Perceive (read the world)
      3. Decide (what to do)
      4. Act (do it)
      5. Save state (persist for next loop)
      6. Sleep (wait for next trigger)
      7. Repeat forever
    """
    log("=" * 50)
    log("Agent starting. Press Ctrl+C to stop.")
    log("=" * 50)

    while True:
        state = load_state()
        state["runs"] = state.get("runs", 0) + 1
        state["last_run"] = datetime.now().isoformat()

        # 1. Perceive
        perception = perceive()
        log(f"Run #{state['runs']} — perceived: {perception['signal']}")

        # 2. Decide
        action = decide(perception, state)
        log(f"Decision: {action}")

        # 3. Act
        state = act(action, perception, state)

        # 4. Save state (persistence!)
        save_state(state)

        # 5. Sleep until next trigger
        log(f"Sleeping {INTERVAL_SECONDS}s until next loop...")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
