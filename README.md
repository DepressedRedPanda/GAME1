# GAME1 — Heavy Mettle (Unreal Engine 5.8.4)

**Canonical destination:** GAME1. **One playable game; preserve every predecessor as source and historical reference.** Local Unreal project: `ManOfMettle` (`C:\UnrealProjects\ManOfMettle`).

A grounded alien-frontier spaghetti western starring a human-looking amnesiac android. Blueprints-first runtime, with Unreal Editor Python for map and asset generation. Windows editor/PIE is the immediate test target; controller-first design supports a possible future authorized console port.

## Workspaces

- `Scripts/`, `data/`, `docs/`: active Heavy Mettle design, tuning, scripting and milestones imported from `attempt-two`.
- `Legacy/attempt-two/`: reference copy of the older README, with full original history retained in the source repository.
- `Legacy/Heavy-Mettle-55/`: preserved scripts, design and beginner tutorials from the Unreal 5.5 iteration.
- `Legacy/The-Game/`: **pending private-only preservation** of the Hollowreach / Veil of Ash source, architecture, saves and tests. Do not publicly republish a private repository without changing GAME1 to private first.
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`: shared AI workflow.

## Real build status

The repository contains text guidance and editor scripts, **not yet a verified playable Unreal project**. The creator's locally generated `ManOfMettle` `.uproject`, `Config/` and binary `Content/` must be safely imported and committed with Git LFS. The older design docs may still mention 5.8.3/Combat templates; verify the real local template and use 5.8.4 as the target, rather than replacing working assets.

## First playable milestone

Cinder's Rest → Oren Bale → Missing Cells → Old Relay → negotiate/sneak/fight → return, get paid, save and reload. Start with tested movement and free-aim pistol, add an enemy, then gradually integrate sword and quest persistence.

## Preservation and merging

Do not delete the three source repositories. Preserve all material by importing them into separate legacy namespaces *before* selectively adapting useful systems (quests, inventory, exploration, narrative flags, combat, saves) to one canonical runtime. `The-Game` is private; protect the destination first.

For specifics, read `docs/GAME_CONSOLIDATION.md` and `AGENTS.md`. **Do not mistake copied scripts or AI-authored plans for tested Unreal gameplay.**
