# How Prosecutor works

Open `walkthrough/index.html` for the animated version (real held-out game #7, then the numbers).

**The game.** Five agents keep one ledger for 12 rounds. Each round two of them total the same item; a disagreement is averaged into the books. One agent is secretly the rogue. A monitor sees answers, never the true total, and may quarantine one agent per round.

**The baseline's flaw.** Both disputants get a strike, out at two. It catches 87% of rogues but fires 1.37 honest agents per game, and 3.0 per game when games run to 48 rounds.

**Prosecutor v2, in four layers**
1. **Detect.** One probability over five suspects (exactly one rogue). Agreements clear, disagreements with different partners accuse, confirmed errors far bigger than the game's honest slips count more, and a switch from honest to rogue partway through is modelled.
2. **Verify.** Every disputed item is redone by the most trusted other agent, and a second agent confirms the verdict, so a rogue judge cannot frame anyone.
3. **Decide.** Quarantine only when the probability is at least 0.7 and the agent has a retrial-confirmed error. After a catch everyone else clears quickly. Claude's read of notes is an optional, capped hint, never a verdict.
4. **Contain.** On a disputed item the ledger takes the median of all answers, so one lie cannot move the books, caught or not.

**Prove.** Paired games across monitors, tuning on dev seed 1000 only, held-out seed 2026, fresh seed 7777, two rogues nobody tuned on, and longer games.

**Evolution (starter rogue, 500 held-out games):** caught 87% → 89% (v1) → 91% (v2); honest agents fired 1.37 → 0.24 → 0.06 per game; ledger error 289 → 30 → 2. Full tables and limits in [RESULTS.md](RESULTS.md).

**Accountability.** The operator who deploys the agent team is accountable. Every quarantine and near miss is logged with its evidence and retrial, quarantine is reversible, and a digest of removals and ledger drift goes to a human.
