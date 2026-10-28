> **CURRENT PRIORITY (2026-10-27):** Use [docs/STATUS.md](docs/STATUS.md) as the verified implementation checklist, and [docs/UNIFIED_GAME_ARCHITECTURE.md](docs/UNIFIED_GAME_ARCHITECTURE.md) as the design authority. The previous roadmap below is an early feature wishlist, not the current build order. **GAME1** is canonical; the real Unreal project has not been uploaded or PIE-verified.

## Production order — one complete 15-minute slice
1. **P0 — Verify local project:** Standard/Combat template, existing movement/jump, Blueprint compile and startup probe; safely connect real project assets to Git LFS. [Issue #1](https://github.com/DepressedRedPanda/GAME1/issues/1)
2. **P1 — Build Cinder's Rest and Old Relay graybox:** reliable collision, spawns and traversal. [Issue #2](https://github.com/DepressedRedPanda/GAME1/issues/2)
3. **P2 — Combat:** camera aim, pistol shot, one enemy and one encounter. [Issue #3](https://github.com/DepressedRedPanda/GAME1/issues/3)
4. **P3 — Missing Cells:** one reusable interactable interface, a linear objective path with two choices, single reward, save/load proof. [Issue #4](https://github.com/DepressedRedPanda/GAME1/issues/4)
5. **Later:** sword combos, extensive crafting, levels, multiple NPC routines, procedural towns, lock-on variants, coat physics and larger faction simulation. Add only if they improve the proven slice.

**Design principle:** no second player pawn/GameMode/quest manager/save subsystem; don't assume C++ parent classes or working Combat-template enemies.

---

# Roadmap & Tasks

Milestones
1) MVP (prototype) — Basic playtestable demo
   - Player movement, camera, aiming
   - Pistol shooting + simple recoil
   - Basic melee + 2-combo system
   - Lock-on within short range
   - One enemy type with AI
   - One small test map with verticality

2) Systems Expansion
   - Crafting, inventory UI
   - XP + leveling
   - Melee combos expanded + parry
   - Cloth jacket + item sockets

3) Content & Polish
   - Additional enemy types
   - Quests (villager NPCs) and simple quest system
   - Procedural/semi-random settlement layout

Initial issues to create (I can open them if you want)
- Issue: Setup project skeleton and folder structure
- Issue: Implement BP_PlayerCharacter base movement
- Issue: Implement basic gun firing (BP_Gun)
- Issue: Implement melee combo system (BP_Melee)
- Issue: Implement lock-on component
- Issue: Create CombatArena test level

Contributing
- Use feature branches and open PRs back to main
- Use descriptive commit messages

