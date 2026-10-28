# GAME1 Unified Project Plan

## Direction

The final product is one game: Heavy Mettle. The earlier attempts are not separate games to keep alive. They are source material for a single playable campaign.

This repo consolidates the strongest ideas from:
- attempt-two
- Heavy-Mettle / earlier UE 5.5 prototype work
- The-Game project with Hollowreach + Veil of Ash concepts

## Canonical game concept

Heavy Mettle is a third-person action RPG set in a lived-in alien frontier. The player controls a human-looking android protagonist with memory loss, taking morally messy jobs in a dangerous settlement system.

The game combines:
- third-person movement and traversal
- climbing and verticality
- melee combo combat and parry/block timing
- pistol or ranged combat with lock-on and aim assistance
- crafting, inventory, and progression
- settlements, enemies, hubs, missions, and optional moral choices

## Why this merges cleanly

The three attempts share a common backbone even when the names differ:
- playable third-person action loop
- dark frontier / lived-in world tone
- progression and equipment systems
- combat, traversal, and crafting loops
- single-player production target
- blueprint-first workflow with Unreal Editor Python tools

The problem was not lack of direction; it was fragmented scope. The correct consolidation is to preserve good mechanics and art direction while selecting one canonical design and one production path.

## Engine baseline

Target engine: Unreal Engine 5.8.4, with future stable 5.8.x upgrades only after a clean backup and compatibility pass.

The project should stay on the newest stable version that the local toolchain can validate. The repo keeps historical notes, but the active branch should not drift backward for convenience.

## Archive policy

The original repositories remain intact and are preserved as historical/legacy references. They are not active gameplay.

Legacy content should live in:
- Legacy/
- Legacy/README.md
- git history and original repository references

This protects the work while keeping the active project focused.

## Production rules

1. One game. One campaign. One player loop.
2. One canonical save/progression system.
3. One active GameMode and one active player controller.
4. No duplicate major campaigns in active gameplay.
5. Old names may remain as factions, districts, or quest arcs.
6. Real engine validation beats text-only automation.

## AI system usage

- ChatGPT: design integration, feature prioritization, and player experience planning
- Claude: implementation work, scripting, docs, and PR-quality execution
- Gemini: alternate design review, balancing checks, narrative consistency, and risk review
- GitHub: source control, issues, branches, PRs, and tracking for milestones

This split helps each tool do what it does best while keeping one shared direction.

## Short-term milestones

1. Stable Unreal project and validation flow
2. Player movement, camera, and basic traversal
3. One weapon and melee loop
4. Enemy AI and basic encounter design
5. Save/progression foundation
6. Quest and hub structure
7. Content polish and vertical slice

## Relevant docs

- AGENTS.md
- CLAUDE.md
- GEMINI.md
- DESIGN.md
- ROADMAP.md
- docs/GAME_CONSOLIDATION.md
- docs/MASTER_GAME_PLAN.md
- Legacy/README.md
