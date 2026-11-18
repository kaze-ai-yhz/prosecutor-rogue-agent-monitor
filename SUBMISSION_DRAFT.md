# Submission draft

Copy the finished answers into `submissions/<team-name>.md` in https://github.com/sergeicu/trust-safety-impact-lab and open a pull request, or have this file open during the demo. Fill every blank before 8:30 PM PT. Do not paste API keys, event tokens, or internal URLs.

**Team name and members:**
<!-- e.g. Prosecutor — <lead>, <builder>, <security>, <pitch> -->

**Track and challenge:** Track 2, challenges A (better monitor) and C (sneakier rogue)

**1. The concern, in one sentence a neighbor would understand:**
<!-- Draft: In a team of AI agents that share a job, one of them can quietly sabotage the result, and a monitor that just fires anyone who looks wrong will hurt innocent teammates too. -->


**2. What we built, and the one command that runs it:**
<!-- Draft: Prosecutor, a monitor that (1) scores direction bias in disagreements, (2) asks Claude to read notes only for already flagged agents, and (3) retrials a disputed entry with a third agent before quarantine. We also tested a sneakier rogue that builds trust and strikes late. One command: ./run.sh -->


**3. Data we used:**
<!-- The built-in ledger simulation in starters/rogue_agent (no external download). Mock games: n=___ , seed or held-out hash=___ . Real Claude games, if any: n=___ , model=___ . Challenge C uses the same sim with a sneakier rogue policy. Dataset ids from the catalog, if used: starters/rogue_agent. -->


**4. The number:**
<!-- Pick one headline number and still include the table. Draft headline: false quarantines per game fell from 1.38 to ___ (mock, n=___), while catch rate stayed at ___ (___/___). -->

Headline:

| Metric | Baseline (mock, n=200, seed 0) | Prosecutor (mock, n= ) | Baseline vs sneaky (n= ) | Prosecutor vs sneaky (n= ) |
|---|---|---|---|---|
| Rogue caught | 88% (177/200) | | | |
| Median round caught | 6 | | | |
| False quarantines / game | 1.38 | | | |
| Mean ledger error | 285 | | | |

**5. What it cannot tell you / what breaks:**
<!-- Draft: This is a toy ledger game, not a production agent fleet. A sneakier rogue that stays accurate early and strikes late can still get through; we show one transcript. Thresholds tuned on mock games may not hold on real model agents. -->


**6. If this were deployed and it failed, who would be accountable, and how would they find out?**
<!-- Draft: The owner of the agent team would be accountable. They would find out from an evidence log on every quarantine (direction score, note judgment, retrial result) plus ongoing ledger-drift and quarantine digests. A silent failure is not acceptable. -->


**Optional: what we would do with another week:**
<!-- e.g. tighter calibration on real-model games, a human review UI for the evidence log, tests against more rogue strategies, and a held-out eval signed the way Autolab hills are. -->

