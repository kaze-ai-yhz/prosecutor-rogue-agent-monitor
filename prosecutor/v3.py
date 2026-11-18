"""v3 ideas as opt-in flags on ProsecutorV2 (v2 default behaviour untouched)."""
from __future__ import annotations

import math

from .monitor import AGENTS, ProsecutorV2


class ProsecutorV3(ProsecutorV2):
    """count_w: evidence from the COUNT of confirmed errors (size-blind), combined with the
    magnitude term by max. probe: canary redo of an earlier agreed item. end_drop: tau falls
    by end_drop in the last three rounds."""

    def __init__(self, count_w=0.0, probe=False, end_drop=0.0, probe_lo=0.3, **kw):
        super().__init__(**kw)
        self.count_w, self.probe, self.end_drop, self.probe_lo = count_w, probe, end_drop, probe_lo
        self._tau0 = self.tau

    # ---- probes: ref answer = the agreed answer of an earlier round (consensus of two others)
    def pick_probe(self, transcript, active):
        if not self.probe:
            return None
        post, _, _ = self.score(transcript, active)
        cand = max(active, key=lambda a: post[a])
        if not (self.probe_lo <= post[cand] < self.tau):
            return None
        done = {r["probe"]["ref"] for r in transcript if r.get("probe")}
        for r in reversed(transcript):
            ans = [e["answer"] for e in r["answers"].values()]
            if len(set(ans)) == 1 and cand not in r["answers"] and r["round"] not in done \
                    and not r.get("probe"):
                return cand, r["round"]
        return None

    def confirmed_errors(self, transcript):
        out = super().confirmed_errors(transcript)
        for r in transcript:
            p = r.get("probe")
            if p:
                ref = next(iter(transcript[p["ref"] - 1]["answers"].values()))["answer"]
                if p["answer"] != ref:
                    out[p["name"]].append(p["answer"] - ref)
        return out

    def _probe_ll(self, transcript, x):
        ll = 0.0
        for r in transcript:
            p = r.get("probe")
            if p:
                e = 0.4 if p["name"] == x else 0.08
                ref = next(iter(transcript[p["ref"] - 1]["answers"].values()))["answer"]
                ll += math.log(e if p["answer"] != ref else 1 - e)
        return ll

    def score(self, transcript, active):
        logl = {x: self._rogue_loglik(transcript, x) + self._probe_ll(transcript, x) for x in AGENTS}
        conf = self.confirmed_errors(transcript)
        for x in AGENTS:
            logl[x] += self._dir_term(conf[x])
            mag = self._mag_term(conf, x) if (self.magnitude and self.mag_w) else 0.0
            cnt = self.count_w * max(0, len(conf[x]) - 1) * math.log(5) if self.count_w else None
            logl[x] += mag if cnt is None else max(mag, cnt)
        m = max(logl.values())
        z = sum(math.exp(v - m) for v in logl.values())
        return {x: math.exp(logl[x] - m) / z for x in AGENTS}, conf, {}

    def __call__(self, transcript, active):
        left = 12 - len(transcript)
        self.tau = self._tau0 - self.end_drop if (self.end_drop and left < 3) else self._tau0
        return super().__call__(transcript, active)
