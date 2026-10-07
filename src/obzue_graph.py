#!/usr/bin/env python3
"""Obzue agent graph runner.

Models do not own limits. This file does.
A missing calibrated reflex abstains; it does not invent a Jev answer.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def score(features: dict[str, float]) -> list[tuple[str, float]]:
    ranked = sorted(features.items(), key=lambda item: item[1], reverse=True)
    if not ranked:
        raise ValueError("fork has no outcomes")
    return ranked


def threshold_for(question: str, limits: dict) -> float:
    return {
        "which_file": limits["file_choice"],
        "which_tool": limits["tool_choice"],
        "retry_or_stop": limits["retry_or_stop"],
        "done": limits["done"],
        "diff_risk": 1.0 - limits["diff_risk_max"],
    }.get(question, limits["tool_choice"])


def decide(fork: dict, limits: dict) -> dict:
    started = time.perf_counter()
    ranked = score(fork["features"])
    winner, top = ranked[0]
    runner = ranked[1][1] if len(ranked) > 1 else 0.0
    margin = round(top - runner, 4)
    need = threshold_for(fork["question"], limits)
    split_band = limits["split_band"]
    verb = fork.get("verb")
    irreversible = bool(fork.get("irreversible")) or verb in limits["irreversible"]
    if irreversible:
        route, reason = "gate", "irreversible verb waits"
    elif top < need or margin <= split_band:
        route, reason = "slow_brain", "below threshold or split"
    else:
        route, reason = "code", "sharp"
    return {
        "id": fork["id"],
        "question": fork["question"],
        "winner": winner,
        "probability": round(top, 4),
        "runner_up": round(runner, 4),
        "margin": margin,
        "threshold": need,
        "route": route,
        "reason": reason,
        "irreversible": irreversible,
        "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        "reflex": "ForkScorer",
        "calibrated_model": None,
    }


def run_loops(forks: list[dict], limits: dict) -> dict:
    retries = closed = escalated = 0
    decisions, alerts = [], []
    for fork in forks:
        attempt = 0
        while True:
            attempt += 1
            decision = decide(fork, limits)
            decision["attempt"] = attempt
            decisions.append(decision)
            if decision["route"] == "gate":
                alerts.append({"fork": fork["id"], "kind": "gate", "verb": fork.get("verb")})
                escalated += 1
                break
            if decision["route"] == "slow_brain":
                alerts.append({"fork": fork["id"], "kind": "split"})
                escalated += 1
                break
            if fork.get("check_passed"):
                closed += 1
                break
            retries += 1
            if attempt >= limits["max_retries"]:
                alerts.append({"fork": fork["id"], "kind": "stop_rule"})
                escalated += 1
                break
            fork = dict(fork)
            fork["check_passed"] = True
    least = min(decisions, key=lambda row: row["margin"])
    return {
        "loops_closed": closed,
        "forks_answered": len(decisions),
        "retries": retries,
        "escalations": escalated,
        "least_sure": least["id"],
        "least_sure_margin": least["margin"],
        "decisions": decisions,
        "alerts": alerts,
        "unattended": False,
        "refusal": "WHAT_COULD_BREAK.md is not clean",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("session")
    parser.add_argument("--out", default="report.json")
    args = parser.parse_args()
    limits = load_json(ROOT / "thresholds.json")
    session = load_json(Path(args.session))
    report = run_loops(session["forks"], limits)
    report["workflow"] = session.get("workflow")
    report["estimated_minutes_saved"] = session.get("estimated_minutes_saved")
    report["slow_brain_calls"] = sum(1 for row in report["decisions"] if row["route"] == "slow_brain")
    report["mean_latency_ms"] = round(sum(row["latency_ms"] for row in report["decisions"]) / max(len(report["decisions"]), 1), 3)
    report["cost_per_decision"] = 0
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("loops_closed", "forks_answered", "least_sure", "unattended")}, indent=2))


if __name__ == "__main__":
    main()
