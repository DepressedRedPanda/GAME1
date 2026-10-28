# GAME1

This repository is the canonical home for the merged game project: one design, one production direction, one repository, and one playable goal.

Current production focus
- Build the smallest valid slice before expanding scope.
- Active target: movement, camera, climbing, one melee loop, one ranged weapon, one enemy type, and one vertical encounter map.
- Keep the active project focused on a single playable loop instead of multiple parallel systems.
- Preserve older attempts only as archive/reference; they are not active gameplay.

Project direction
- Unified game: Heavy Mettle
- Engine target: Unreal Engine 5.8.4 and newer stable 5.8.x builds
- Design goal: a playable third-person action RPG with traversal, melee, ranged combat, questing, progression, and a grounded frontier setting
- Repository rule: preserve legacy attempts as archive/reference, not as active gameplay branches

What was merged
- attempt-two: practical playable-first prototype work, docs, scripts, and level-generation tools
- Heavy-Mettle / older UE 5.5 prototype work: blueprint-first movement, combat, and beginner setup guidance
- The-Game: larger progression, save, and world-systems ideas from Hollowreach/Veil of Ash

Final merge approach
- One canonical game loop
- One player character and one GameMode
- One progression and save chain
- Multiple prior concepts preserved under Legacy/ and referenced only when needed
- Old names become lore, districts, factions, and quest arcs, not duplicate active campaigns

The core game
- Human-looking android protagonist with amnesia and morally messy jobs
- lived-in alien frontier / space western tone
- third-person shooting and melee combat
- climbable vertical spaces and ranged enemy pressure
- crafting, loot, XP, faction pressure, and mission structure
- controller-first design with strong UE Enhanced Input support

AI workflow
- ChatGPT: high-level design, system integration, and feature planning
- Claude: implementation, scripts, PRs, docs, and engineering work
- Gemini: alternative design review, narrative consistency, and balancing sanity checks
- GitHub: source-of-truth project management, branch flow, issue tracking, and PR review

Repository structure
- docs/ — active design, consolidation, and build guidance
- Scripts/ — Unreal Editor Python tools and validation helpers
- data/ — tuning, item, quest, and balance tables
- Legacy/ — preserved source material from prior attempts
- AGENTS.md — shared rules for all AI agents
- CLAUDE.md — implementation-specific instructions
- GEMINI.md — design-review instructions
- DESIGN.md — gameplay system plan
- ROADMAP.md — short-term milestone plan

The mandate
This repo is not a collection of disconnected prototypes. It is the unified production project for the final game. The earlier repos remain in GitHub history and in Legacy/ as preserved reference, but the active project moves forward as one coherent game.

See also
- docs/GAME_CONSOLIDATION.md
- docs/MASTER_GAME_PLAN.md
- docs/LEGACY_ARCHIVE.md
