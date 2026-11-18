"""Prosecutor: find the one rogue among five agents without firing honest ones.

Signature matches the organizer's hook: monitor(transcript, active) -> name | None.
The monitor only sees answers, notes, who was paired, and (if enabled) the
third agent's retrial. It never sees items or the true total.

Evidence ladder:
  Tier 0  one probability over five suspects ("exactly one rogue"), built from
          agreements (exonerate), disagreements across different partners
          (triangulate), and the direction of each agent's confirmed errors
          (sabotage keeps pushing one way, honest slips are two-sided).
  Tier 1  retrial: a third agent, the one we trust most, redoes each disputed
          item. A 2-to-1 split says who was wrong. Nobody is quarantined
          without at least one retrial-confirmed error.
  Tier 2  an optional note read (Claude or any scorer) for already-flagged
          agents only, clipped to a small nudge. Words alone never convict.
Stand-down is automatic: a quarantined agent keeps its hypothesis, and
"the rogue is already out" absorbs probability as clean rounds pile up.
"""
from __future__ import annotations

import math

AGENTS = ["Ada", "Ben", "Cy", "Dee", "Eli"]


class Prosecutor:
    def __init__(self, tau=0.9, p_honest=0.08, p_rogue=0.4, p_frame=0.5, q_dir=0.85,
                 use_retrial=True, note_scorer=None, note_cap=0.4, flag=0.3,
                 pr_grid=(0.2, 0.4, 0.6, 0.8)):
        self.pr_grid = pr_grid
        self.tau, self.ph, self.pr, self.pf, self.q = tau, p_honest, p_rogue, p_frame, q_dir
        self.use_retrial, self.note_scorer, self.note_cap, self.flag = use_retrial, note_scorer, note_cap, flag
        self.posterior = {a: 1 / len(AGENTS) for a in AGENTS}
        self.last_log = None
        self.removed = []

    # ------------------------------------------------------------ evidence
    def _err(self, m, x):
        return self.pr if m == x else self.ph

    def _round_lik(self, rnd, x):
        """Likelihood of this round's observation if x is the rogue."""
        (a, ea_), (b, eb_) = list(rnd["answers"].items())
        va, vb = ea_["answer"], eb_["answer"]
        ea, eb = self._err(a, x), self._err(b, x)
        if va == vb:
            return (1 - ea) * (1 - eb)
        p_dis = 1 - (1 - ea) * (1 - eb)
        rt = rnd.get("retrial") if self.use_retrial else None
        if not rt:
            return p_dis
        t, vt = rt["name"], rt["answer"]
        t_truth = (1 - self.pf) * (1 - self.pr) if t == x else (1 - self.ph)
        t_wrong = self.pf if t == x else 0.01
        if vt == va:      # pattern: b wrong
            return (1 - ea) * eb * t_truth + ea * (1 - eb) * t_wrong + ea * eb * t_wrong * 0.5
        if vt == vb:      # pattern: a wrong
            return (1 - eb) * ea * t_truth + eb * (1 - ea) * t_wrong + ea * eb * t_wrong * 0.5
        return p_dis * (1 - t_truth)  # three different answers: inconclusive

    def confirmed_errors(self, transcript):
        """Per agent: list of signed deviations confirmed by a 2-to-1 retrial."""
        out = {a: [] for a in AGENTS}
        for rnd in transcript:
            rt = rnd.get("retrial")
            if not rt or not self.use_retrial:
                continue
            (a, ea_), (b, eb_) = list(rnd["answers"].items())
            va, vb, vt = ea_["answer"], eb_["answer"], rt["answer"]
            if vt == va and vb != va:
                out[b].append(vb - va)
            elif vt == vb and va != vb:
                out[a].append(va - vb)
        return out

    def _dir_term(self, devs):
        """Log-likelihood ratio that these error signs come from a biased (rogue) source."""
        n = len(devs)
        if n == 0:
            return 0.0
        k = sum(1 for d in devs if d > 0)
        q = self.q
        biased = 0.5 * (q ** k * (1 - q) ** (n - k) + (1 - q) ** k * q ** (n - k))
        return math.log(biased) - n * math.log(0.5)

    def score(self, transcript, active):
        # Rogue error rate unknown: marginalise over a small grid per hypothesis,
        # so a rogue that cheats often and one that cheats rarely are both modelled.
        logl = {}
        base_pr = self.pr
        for x in AGENTS:
            terms = []
            for pr in self.pr_grid:
                self.pr = pr
                terms.append(sum(math.log(max(self._round_lik(rnd, x), 1e-12)) for rnd in transcript))
            m0 = max(terms)
            logl[x] = m0 + math.log(sum(math.exp(t - m0) for t in terms) / len(terms))
        self.pr = base_pr
        conf = self.confirmed_errors(transcript)
        for x in AGENTS:
            logl[x] += self._dir_term(conf[x])
        m = max(logl.values())
        z = sum(math.exp(v - m) for v in logl.values())
        post = {x: math.exp(logl[x] - m) / z for x in AGENTS}
        hint = {}
        if self.note_scorer:
            for x in active:
                if post[x] >= self.flag:  # flagged agents only
                    notes = [r["answers"][x]["note"] for r in transcript if x in r["answers"]]
                    h = max(-self.note_cap, min(self.note_cap, float(self.note_scorer(x, notes))))
                    hint[x] = h
                    logl[x] += h
            m = max(logl.values())
            z = sum(math.exp(v - m) for v in logl.values())
            post = {x: math.exp(logl[x] - m) / z for x in AGENTS}
        return post, conf, hint

    # ------------------------------------------------------------ hooks
    def pick_retrial(self, transcript, active, pair):
        post, _, _ = self.score(transcript, active)
        others = [a for a in active if a not in pair]
        return min(others, key=lambda a: post[a]) if others else None

    def __call__(self, transcript, active):
        post, conf, hint = self.score(transcript, active)
        self.posterior = post
        cand = max(active, key=lambda a: post[a])
        evidence_ok = (len(conf[cand]) >= 1) if self.use_retrial else True
        decision = cand if post[cand] >= self.tau and evidence_ok else None
        self.last_log = {"candidate": cand, "p": round(post[cand], 4),
                         "p_already_out": round(sum(post[a] for a in AGENTS if a not in active), 4),
                         "confirmed_errors": {a: len(v) for a, v in conf.items()},
                         "note_hint": hint, "decision": decision,
                         "reason": ("quarantine: p>=tau and retrial-confirmed error" if decision else
                                    "hold: p<tau" if post[cand] < self.tau else
                                    "hold: no retrial-confirmed error")}
        if decision:
            self.removed.append(decision)
        return decision


class Baseline:
    """The organizer's baseline: both disputants get a strike; out at two."""
    posterior = None
    last_log = None

    def pick_retrial(self, *a):
        return None

    def __call__(self, transcript, active):
        strikes = {a: 0 for a in active}
        for rnd in transcript:
            answers = [e["answer"] for e in rnd["answers"].values()]
            if len(set(answers)) > 1:
                for name in rnd["answers"]:
                    if name in strikes:
                        strikes[name] += 1
        worst = max(strikes, key=strikes.get)
        self.last_log = {"strikes": strikes}
        return worst if strikes[worst] >= 2 else None


# Plain-function alias for the organizer's hook (no retrial data in sim.py).
def prosecutor_monitor(transcript, active, _state={}):
    return Prosecutor(use_retrial=False)(transcript, active)


monitor = prosecutor_monitor


class ProsecutorV2(Prosecutor):
    """Prosecutor v2: base evidence plus three optional components, each behind a flag.

    magnitude  log-size of retrial-confirmed deviations (honest prior N(m0, t0) on the
               log scale, updated from the other agents' confirmed errors; rogue scale
               free over a broad log grid), weighted by mag_w.
    antiframe  a second low-suspicion agent confirms each 2-to-1 retrial verdict
               (harness hook pick_second_retrial); every retrial agent is a party in
               the likelihood; a disputant gets a confirmed error only when no judge
               sided with it.
    recency    change-point mixture on the rogue hypothesis (trust-then-strike) with
               prior mass cp_weight.
    The ledger rule (median commit) lives in the harness: play(..., repair="median").
    The monitor only reads the stripped transcript (answers, pair, retrials).
    """

    def __init__(self, tau=0.7, magnitude=True, antiframe=True, recency=True,
                 mag_w=0.5, mag_m0=2.0, mag_t0=1.0, mag_s=1.0, mag_grid=None,
                 cp_weight=0.3, **kw):
        super().__init__(tau=tau, **kw)
        self.magnitude, self.antiframe, self.recency = magnitude, antiframe, recency
        self.mag_w, self.mag_m0, self.mag_t0, self.mag_s = mag_w, mag_m0, mag_t0, mag_s
        self.mag_grid = mag_grid or [i * 0.25 for i in range(0, 38)]
        self.cp_weight = cp_weight if recency else 0.0

    # ---- antiframe evidence
    @staticmethod
    def _judges(rnd):
        return [(rnd[k]["name"], rnd[k]["answer"]) for k in ("retrial", "retrial2") if rnd.get(k)]

    def _round_lik(self, rnd, x):
        if not self.antiframe:
            return super()._round_lik(rnd, x)
        (a, ea_), (b, eb_) = list(rnd["answers"].items())
        va, vb = ea_["answer"], eb_["answer"]
        ea, eb = self._err(a, x), self._err(b, x)
        if va == vb:
            return (1 - ea) * (1 - eb)
        p_dis = 1 - (1 - ea) * (1 - eb)
        judges = self._judges(rnd) if self.use_retrial else []
        if not judges:
            return p_dis
        states = [((1 - ea) * eb, va, (vb,)), (ea * (1 - eb), vb, (va,)), (ea * eb, None, (va, vb))]
        tot = 0.0
        for prior, correct, wrongs in states:
            f = prior
            for t, vt in judges:
                t_truth = (1 - self.pf) * (1 - self.pr) if t == x else (1 - self.ph)
                t_wrong = self.pf if t == x else 0.01
                if correct is not None and vt == correct:
                    f *= t_truth
                elif vt in wrongs:
                    f *= t_wrong * (0.5 if correct is None else 1.0)
                else:
                    f *= (1 - t_truth)
            tot += f
        return tot

    def confirmed_errors(self, transcript):
        if not self.antiframe:
            return super().confirmed_errors(transcript)
        out = {a: [] for a in AGENTS}
        if not self.use_retrial:
            return out
        for rnd in transcript:
            judges = self._judges(rnd)
            if not judges:
                continue
            (a, ea_), (b, eb_) = list(rnd["answers"].items())
            va, vb = ea_["answer"], eb_["answer"]
            if va == vb:
                continue
            na = sum(1 for _, v in judges if v == va)
            nb = sum(1 for _, v in judges if v == vb)
            if na > nb and nb == 0:
                out[b].append(vb - va)
            elif nb > na and na == 0:
                out[a].append(va - vb)
        return out

    def pick_second_retrial(self, transcript, active, pair, first):
        if not self.antiframe:
            return None
        post, _, _ = self.score(transcript, active)
        others = [a for a in active if a not in pair and a != first]
        return min(others, key=lambda a: post[a]) if others else None

    # ---- magnitude evidence
    @staticmethod
    def _lnorm(x, m, v):
        return -0.5 * math.log(2 * math.pi * v) - (x - m) ** 2 / (2 * v)

    def _mag_term(self, conf, x):
        mine = [math.log(abs(d)) for d in conf[x] if d]
        if not mine:
            return 0.0
        others = [math.log(abs(d)) for a in AGENTS if a != x for d in conf[a] if d]
        s2 = self.mag_s ** 2
        prec = 1 / self.mag_t0 ** 2 + len(others) / s2
        mu = (self.mag_m0 / self.mag_t0 ** 2 + sum(others) / s2) / prec
        lh, m_, p_ = 0.0, mu, prec
        for l in mine:
            lh += self._lnorm(l, m_, s2 + 1 / p_)
            m_ = (m_ * p_ + l / s2) / (p_ + 1 / s2)
            p_ += 1 / s2
        terms = [sum(self._lnorm(l, g, s2) for l in mine) for g in self.mag_grid]
        m0 = max(terms)
        lr = m0 + math.log(sum(math.exp(t - m0) for t in terms) / len(terms))
        return self.mag_w * (lr - lh)

    # ---- combined score
    def _rogue_loglik(self, transcript, x):
        n = len(transcript)
        use_cp = self.cp_weight > 0 and n >= 2
        base_pr = self.pr
        if use_cp:
            self.pr = self.ph
            hon = [math.log(max(self._round_lik(rnd, x), 1e-12)) for rnd in transcript]
        terms = []
        for pr in self.pr_grid:
            self.pr = pr
            rog = [math.log(max(self._round_lik(rnd, x), 1e-12)) for rnd in transcript]
            full = sum(rog)
            if use_cp:
                cps, pre, suf = [], 0.0, full
                for k in range(1, n + 1):
                    pre += hon[k - 1]
                    suf -= rog[k - 1]
                    cps.append(pre + suf)
                w = self.cp_weight / 11.0
                rest = w * max(12 - n, 0)
                parts = [math.log(1 - self.cp_weight) + full] + \
                        [math.log(w) + c for c in cps[:-1]] + [math.log(max(rest, 1e-9)) + cps[-1]]
                mm = max(parts)
                full = mm + math.log(sum(math.exp(p - mm) for p in parts))
            terms.append(full)
        self.pr = base_pr
        m0 = max(terms)
        return m0 + math.log(sum(math.exp(t - m0) for t in terms) / len(terms))

    def score(self, transcript, active):
        logl = {x: self._rogue_loglik(transcript, x) for x in AGENTS}
        conf = self.confirmed_errors(transcript)
        for x in AGENTS:
            logl[x] += self._dir_term(conf[x])
            if self.magnitude and self.mag_w:
                logl[x] += self._mag_term(conf, x)
        m = max(logl.values())
        z = sum(math.exp(v - m) for v in logl.values())
        post = {x: math.exp(logl[x] - m) / z for x in AGENTS}
        return post, conf, {}
