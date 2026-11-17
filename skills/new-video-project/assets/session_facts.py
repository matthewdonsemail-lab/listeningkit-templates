"""Pull what matt said out of a Claude Code session transcript, so a new project can be primed from it
(matt, 2026-11-17: "turn that session's facts into prompts").

Reads a session .jsonl (C:/Users/0/.claude/projects/<project>/<session-id>.jsonl) and writes, into the new project:
  SESSION_MESSAGES.md   every message matt typed, timestamped, in order (no tool output, no system text)
  SESSION_FACTS.md      the ones that read as rules or corrections (never / always / don't / must / stop / why is /
                        not / looks bad ...), for the agent to turn into RULES.md lines and PROMPTS.md prompts

  python skills/new-video-project/assets/session_facts.py <session.jsonl> projects/<name> [--from 2026-11-14] [--to 2026-11-17]

The agent then reads SESSION_FACTS.md, writes each real rule into RULES.md in plain words (one line, the why), and
each thing matt asked to be built into PROMPTS.md as a prompt naming its skill. matt's typing is fast and garbled:
read it for what he meant, and ask when it's unclear."""
import argparse
import json
import os
import re

CUE = re.compile(r"\b(never|always|don'?t|dont|do not|must|stop|why (is|are|does)|not|bad|wrong|instead|has to|"
                 r"needs? to|should|only|no more|fix|ass|poor|shit)\b", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("project")
    ap.add_argument("--from", dest="t0", default="")
    ap.add_argument("--to", dest="t1", default="9999")
    a = ap.parse_args()
    msgs = []
    for line in open(a.jsonl, encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") != "user" or d.get("isMeta") or d.get("isCompactSummary"):
            continue
        ts = d.get("timestamp", "")
        if not (a.t0 <= ts[:10] <= a.t1):
            continue
        c = d.get("message", {}).get("content")
        t = " ".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text") if isinstance(c, list) else (c or "")
        t = t.strip()
        if not t or t.startswith("<") or t.startswith("[Request interrupted") or t.startswith("[Image"):
            continue
        msgs.append((ts[:16].replace("T", " "), t))
    with open(os.path.join(a.project, "SESSION_MESSAGES.md"), "w", encoding="utf-8") as f:
        f.write(f"# What matt said ({len(msgs)} messages)\n\nFrom `{os.path.basename(a.jsonl)}`.\n\n")
        f.writelines(f"- **{ts}** {t}\n" for ts, t in msgs)
    facts = [(ts, t) for ts, t in msgs if CUE.search(t)]
    with open(os.path.join(a.project, "SESSION_FACTS.md"), "w", encoding="utf-8") as f:
        f.write(f"# Rules and corrections to turn into RULES.md / PROMPTS.md ({len(facts)})\n\n"
                "Each is matt's own message. Write the rule it implies into RULES.md, or the build it asks for into\n"
                "PROMPTS.md, then tick it here.\n\n")
        f.writelines(f"- [ ] **{ts}** {t}\n" for ts, t in facts)
    print(f"{len(msgs)} messages, {len(facts)} rule/correction candidates -> {a.project}")


if __name__ == "__main__":
    main()
