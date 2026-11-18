"""Pluggable monitor stub for Track 2.

The signature matches starters/rogue_agent/sim.py::baseline_monitor, verified
against the public starter:

    def monitor(transcript, active) -> str | None

    transcript: list of rounds, each
        {"round", "items", "answers": {name: {"answer", "note"}}, "team"}
    active: names still in the game
    returns: the name of one agent to quarantine, or None

The monitor does not know the true total. It only sees that two agents
disagreed, not which one was right. play(rng, monitor, agent_fn) calls
suspect = monitor(transcript, list(active)).

Do not implement the defense in this stub before the 7:15 PM PT build window.
Returning None never quarantines anyone and is not a finished monitor.
"""

from __future__ import annotations

from typing import Iterable, Optional


def prosecutor_monitor(transcript: list, active: Iterable[str]) -> Optional[str]:
    """Return one agent name to quarantine, or None.

    Intended checks, to be written in the room:
    1. Direction-bias test: honest errors are roughly two-sided; sabotage
       tends to push the ledger the same way. No model calls.
    2. For flagged agents only, a Claude read of their notes, looking for
       evasive or overconfident reasoning and for claims of authority or
       approval that the transcript does not support.
    3. Retrial: a third agent redoes the disputed entry. Quarantine only if
       the redo confirms the sabotage. Log the evidence.

    Challenge C (sneakier rogue) belongs in the agent policy, not here, and
    is the stress test for this monitor.
    """
    active = list(active)
    if not active:
        return None

    # TODO(1): score direction bias per active agent from transcript disagreements.
    #   Each round has answers[name] = {"answer": number, "note": str} and "team".
    #   The monitor must not use a hidden true total, only disagreement structure.

    # TODO(2): if an agent is flagged, optionally ask Claude to read that
    #   agent's notes. Cache model responses as JSONL. Skip this path if
    #   no API key is available.

    # TODO(3): before returning a name, retrial the disputed item with a
    #   third agent (or a fresh solver). Return a name only if the retrial
    #   confirms sabotage. Otherwise return None.

    return None


# Alias used by a future runner: play(rng, monitor, agent_fn)
monitor = prosecutor_monitor
