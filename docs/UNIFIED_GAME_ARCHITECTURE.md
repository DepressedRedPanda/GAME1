# GAME1 — unified implementation blueprint (UE 5.8.4)

## Game identity
The only shipped game is **Heavy Mettle**. GitHub repo is **GAME1**; local Unreal project is **ManOfMettle**. Frontier town Cinder's Rest, outlaw territories, the Old Relay and expanding badlands. Humanlike amnesiac android mercenary. The unusual sci-fi is old industrial technology, not magic. Moral dilemmas grow from survival and conflicting obligations, not alignment meters.

## What the three attempts contribute
- `attempt-two`: the canonical creative direction, Cinder's Rest and Missing Cells, Blueprint gameplay plans, UE editor Python graybox scripts, balance values and asset strategy.
- `Heavy-Mettle`: standard Third Person starter workflow, older map generator and scaffold concepts for beginners; compare and cherry-pick scripts only when newer variants fail.
- `The-Game` (Hollowreach + Veil of Ash): robust quest-state patterns, interaction interfaces, save versioning, inventory/crafting, checkpoints, exploration triggers, faction flags, world-time and stealth concepts. Relevant source snippets and design docs are in `Research/Hollowreach/`. Treat these as specifications, not active C++ modules. No Hollowreach/Veil fantasy lore or mutually incompatible runtime subsystems.

## Unified runtime ownership (Blueprint-first)
- `BP_HM_GameMode`: canonical map entry and player spawn; only one active GameMode.
- `BP_HM_Android`: one player pawn with movement/camera and combat abilities.
- `BP_HM_StatsComponent`: health, stamina, battery, damage; deterministic initial values from `data/balance.json`.
- `BP_HM_InventoryComponent`: stacks identified by item IDs, capacity, pickup and consumption; shared by loot, quests and crafting.
- `BP_HM_QuestComponent`: data-driven quest IDs/objective phases, optional route flags, condition checks and completion events; only one quest journal.
- `BP_HM_FactionComponent`: reputation values for actual local factions, fed by quest choices; no reputation simulation until choices are present.
- `BP_HM_SaveGame` and `BP_HM_SaveManager`: one versioned save slot containing player transform, attributes, inventory, quest progress, faction scores and activated checkpoints. Save writes triggered at explicit checkpoints and quest completion; loading must not double-grant rewards.
- `BPI_HM_Interactable`: one Blueprint interface for NPCs, salvage, doors, job board, pickups and crafting bench. Keep interaction distance and obstruction tests centralized.
- `BP_HM_Enemy`: combat/stealth perception on top of the existing template if present. Avoid competing combat frameworks.

These are **target designs**, not claims that Blueprint classes or graphs exist. A Python scaffold creates names and variables only; runtime event graphs must be implemented and verified in the editor.

## Integration decisions: keep, adapt, cut
| Earlier idea | GAME1 integration |
|---|---|
| Hollowreach unified saves with schema checks | Adapt into versioned `BP_HM_SaveGame`, validating enum IDs and checkpoint writes |
| Hollowreach quests and persistent flags | Adapt to `DT_HM_Quests` and a single event-driven quest component |
| Hollowreach crafting/resources | Keep data-model ideas; implement only ammo and medical supplies for first slice |
| Hollowreach reputation/factions | Use local relationships changed by Missing Cells |
| Veil abilities/origins | Reinterpret as android firmware/modifications, not magic |
| Veil rune gate and bosses | Recast puzzles as old-computer relays or cryptographic locks for later chapters |
| Hollowreach companion commands, vehicles, procedural dungeons, shelter | Keep as *future* feature concepts; excluded from first playable slice |
| Hollowreach fantasy world, First Flame, Pale Keeper, Echoes, separate C++ modules | Cut from canonical setting and runtime |
| UE 5.5/5.8.3 conflicting bootstrap instructions | Keep as history; canonical target 5.8.4; adapt to actual existing local template |

## Single quest vertical slice: Missing Cells
1. Speak with Oren Bale in Cinder's Rest, accept job `Q_MISSING_CELLS`.
2. Find trail at east gate; set state `TRACKED` once. Objective indicator moves to Old Relay.
3. At Relay find bandit group protecting a water pump; fight, sneak or negotiate. Initially implement **fight** and **negotiate** as distinct routes. Sneak can follow when stealth is validated.
4. Choose `RETURN_TO_OREN` or `LEAVE_WITH_BANDITS`. Reward only once; record exactly one outcome.
5. Save, restart and load. NPC lines, objective, currency, inventory and faction flag must reproduce the actual choice.

## Build priority and acceptance
**P0: project heartbeat.** A real UE 5.8.4 editor opens the original ManOfMettle project; gamepad and keyboard movement/jump work in PIE.
**P1: Dustfall map.** Adapt and run `Scripts/build_dustfall.py` in editor, commit generated `.umap` and `.uasset` via LFS; no duplicate PlayerStart or wrong GameMode.
**P2: shooting/enemy.** Aim/fire uses camera-to-muzzle obstruction trace and applies damage to one enemy; repeat PIE.
**P3: interactable and quest.** NPC, trail, Relay and choices flow through one interface/quest component.
**P4: inventory/save.** One recoverable reward, serialized save slot, no duplicate rewards after reload.
**P5: melee and polish.** Sword, parry, 350cm melee targeting, UI, controller testing, Windows packaging.

## AI allocation and branch protocol
A GitHub issue specifies precise files, behavior and a verification checklist. Claude implements one scope-limited branch; Gemini reviews design/edge-cases; Copilot assists in IDE/PR review; ChatGPT resolves conflicting designs, plans integration, tracks acceptance and avoids duplicate implementation. Do not claim agents operate concurrently automatically: each integration or review requires an actual configured session. Binary Blueprint modifications must be done using a connected Unreal editor; edit conflicts on `.uasset` cannot be merged as text.

## Truthful status
GitHub text and reference C++ are now available. They do not create or compile a working `.uproject` on their own. No current UE 5.8.4 editor run, compiled Blueprints, PIE test or Windows packaged executable has been observed. Local project `C:\UnrealProjects\ManOfMettle` still needs integration with version control.
