# Heavy Mettle — verified implementation status
Updated 2026-10-27. Canonical repository: DepressedRedPanda/GAME1; local project: C:\UnrealProjects\ManOfMettle; target UE 5.8.4.

**Evidence rule:** Only check an item after actual evidence (saved editor assets, screenshots, Play In Editor, test logs). Repository descriptions, AI-created instructions, or proposals are NOT proof of implementation.

## P0 — Project heartbeat (current milestone)
- [ ] Confirm local ManOfMettle.uproject opens in the installed UE 5.8.x editor without replacing assets.
- [ ] Record whether its Third Person template is Standard or Combat, and the actual existing player Blueprint path/class (do not assume a C++ parent).
- [ ] Verify existing player spawns, moves, and jumps in Play In Editor.
- [ ] Create, compile, and place a small BP_HM_StartupProbe Blueprint Actor; confirm BeginPlay Print String executes in PIE.
- [ ] Back up local project and safely connect .uproject, Config and Content to GAME1 with Git LFS; verify a clean clone can open.

## P1 — Dustfall
- [ ] Generate L_Dustfall.umap using editor script in existing project; inspect collision/spawn and PIE.

## P2 — Shooting
- [ ] Pistol aim, damage and one working enemy verified in PIE.

## P3 — Interact/quest/save
- [ ] Missing Cells has two paths and one reproducible saved outcome.

## P4 — Polish
- [ ] Sword/melee improvement, controller validation and Windows package smoke test.

### Daily lesson selection
Pick the first unchecked task in the current milestone. Several P0 checks can be validated during a single <=30-minute session. Do not skip P0 because newer story or design documents exist.
