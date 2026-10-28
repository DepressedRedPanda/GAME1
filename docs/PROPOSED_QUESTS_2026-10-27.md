# Proposed quests and story beats — 2026-10-27

**ALL IDEAS HERE ARE PROPOSED, NOT CANON.** They require player approval and do not change any existing saved Quest.* or Item.* IDs. Don't instantiate unique gameplay frameworks. Reuse the single interaction/quest/save chain defined in docs/UNIFIED_GAME_ARCHITECTURE.md. Battery is technology/fuel, not magic.

## PROPOSED 01 — The Last Lantern (side job)
**Who/where:** Nima Voss at a one-room clinic, Cinder's Rest.
**Action:** Inspect a dying backup lantern and find an intact Battery from nearby salvage. Choose to donate it or sell it to Oren's freight office.
**Two outcomes:** Donate -> clinic remains lit and Nima provides one future small healing service. Sell -> gain chits, clinic is dark for a later scene; avoid an irreversible global morality penalty.
**Reuse:** BPI_HM_Interactable, quest objective flag, reward transaction, persisted local boolean. No crafting UI needed.

## PROPOSED 02 — A Fair Measure (moral choice)
**Who/where:** Oren Bale and displaced miner representative near the Cinder's Rest loading dock.
**Action:** Examine an inaccurate freight scale, confront Oren, and choose to report a measurement fraud or accept a payout to stay quiet.
**Two outcomes:** Report -> small trust gain with miners, Oren charges slightly more later; Silence -> short-term credits and a suspicious encounter later.
**Reuse:** investigate/inspect, two-option dialogue, simple stored outcome. No simulated economy: one hand-authored price/dialogue variant at most.

## PROPOSED 03 — Dead Signal (ancient-technology clue)
**Who/where:** A nameless technician at Old Relay.
**Action:** Restore one Battery connection, interact with one terminal, and interpret a fragmentary serial number.
**Two outcomes:** Give the log to technician -> earn a practical repair kit and a future information source; keep it -> unlock a private protagonist memory clue.
**Reuse:** usable actor, flag/counter, quest reward, saved outcome; do not build a hacking minigame. "Hollow technology" remains unapproved naming, not established canon.

## Two PROPOSED story beats
1. At Old Relay the android recognizes an obsolete Battery connector it has never consciously seen. Tiny glitch, no explanation; links mechanical maintenance to missing identity.
2. Silt Jack counters the label "thief": the freight company's surplus power once sustained a miners' pump. Oren can be both honest about lost cargo and complicit in rationing. A local choice affects two NPC reactions, not a galaxy-wide faction meter.

## Scope note
The first 15-minute slice remains **Missing Cells**. Only reuse these ideas as optional one-minute test encounters after the first mission works. Do not create a second quest manager, dialogue framework or special currencies. No new IDs have been committed.
