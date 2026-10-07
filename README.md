# Obzue Agent Graph

Independent clone of the "Opus 5.5 + JEV agent graph" pattern from the
`@wavaai.feeds` screenshot. This is not that product, and it does not call Jev.

The original prompt splits work into a slow brain, a fast reflex, and
deterministic code that owns every hard limit. This repo keeps that split and
binds the nodes to the skills already installed for ObzueAI.

## What this is

- A graph, not one long agent.
- Nodes are loops. Edges are typed handoffs. Gates have numeric thresholds.
- Models may advise. Code decides retries, stops, and irreversible actions.
- Unattended mode is refused until the final check is clean.

## What this is not

- Not a Jev SDK install. No key is stored. No probability is invented as if Jev returned it.
- Not a 24/7 Mac Mini or VPS deploy. Deploy is a runbook, not a running host.
- Not a Telegram bot. Alerts are a sink interface until a BotFather token is supplied.
- Linear and Notion are named slots. GitHub is the only connector used here.

## Layout

| Path | Function |
|---|---|
| `agent_graph.xml` | Our prompt, same block shape as the source, Obzue bindings |
| `graph.md` | Nodes, edges, back-edges, gates |
| `thresholds.json` | Code-owned numbers |
| `src/obzue_graph.py` | Runner: score, route, retry, gate, report |
| `examples/session.json` | Sample forks, including one that must wait |
| `skills/SKILL_SCAN.md` | Scan of installed skills mapped onto nodes |
| `source/ORIGINAL.md` | Transcription of the screenshot |
| `WHAT_COULD_BREAK.md` | Required refusal section |

## Run

```bash
python src/obzue_graph.py examples/session.json --out report.json
```

Open `src/dashboard.html` and load `report.json`. The page is static. It does not phone home.

## Layers

1. Slow brain — plan, write, review. Bound to idea-articulation, tutorial-instructor, and the specialist skill for the job.
2. Fast reflex — fixed-outcome scores from compact state. Today this is `ForkScorer` in code. A calibrated model may be plugged in later; a missing key abstains.
3. Deterministic owner — thresholds, retry caps, irreversible gates, trail rows.

Company name is ObzueAI. Do not spell it any other way.
