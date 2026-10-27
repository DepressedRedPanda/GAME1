# MASTER GAME PLAN

## Summary

This repository is the merged production direction for Heavy Mettle and the earlier world concepts that appeared in the other attempts. The goal is not to preserve three parallel projects; it is to combine their best ideas in one coherent game.

## Consolidated scope

### Core loop
- move through the frontier
- climb and navigate vertical space
- fight with melee and ranged weapons
- craft or scavenge gear
- clear small missions and patrol zones
- level up and improve character build

### Content pillars
- hostile frontier settlements
- dangerous vertical encounters
- morally complicated jobs
- a grounded, lived-in sci-fi western tone
- clear progression hooks without overbuilding too early

## Source retention plan

### Keep active
- the best playable prototype systems from attempt-two
- the strongest third-person and combat ideas from Heavy-Mettle
- the save/progression, quest, and world-structure concepts from The-Game

### Preserve as archive
- old fantasy or alternate campaign logic
- legacy git histories and prototype structures
- incomplete or experimental systems that do not fit the final vision

### Rule
No active asset or gameplay branch may be built around a legacy campaign if it conflicts with the canonical project.

## Final canonical identity

The active project should be called:
- Heavy Mettle
- with repository name GAME1 / GAME as the production umbrella

Legacy names become:
- factions
- districts
- quest arcs
- world events
- flavor lines or references in lore

This retains the story history while removing duplicate gameplay states.

## Engine and workflow

Target:
- Unreal Engine 5.8.4 baseline
- newest stable 5.8.x build available after clean validation

Production workflow:
- GitHub issues for features
- feature branches per system
- code review before merge
- Unreal Editor validation before claiming completion
- docs and scripts updated alongside gameplay changes

## AI committee model

### ChatGPT
- design integration and product direction
- clarifying scope and deciding what gets merged
- translating multiple prototypes into one working game design

### Claude
- actual implementation, scripts, automation, and coding changes
- technical iteration on gameplay systems
- architecture cleanup and engineering tasks

### Gemini
- independent design critique
- narrative, enemy, pacing, and world consistency review
- balancing sanity checks and alternative direction analysis

### GitHub
- issue tracking, PR workflow, branch protection, project management
- source of truth for what ships and what remains archive

## Recommended first milestone

Build the smallest valid slice before expanding:
- movement
- camera control
- climbing
- one melee loop
- one ranged weapon
- one enemy type
- one small vertical encounter map

Once that works in-editor, expand to progression, questing, and larger world systems.

## Final principle

This repository is the one place where all previous work becomes a single game. The earlier attempts should not compete. They should contribute.
