# Heavy Mettle — 2026-10-27 daily lesson (under 30 minutes)

## Objective
Verify the actual existing ManOfMettle starter project and run one deliberately disposable Blueprint Actor. Do not switch GameMode, assume C++ classes, or overwrite the original player.

### Setup (about 5 minutes)
1. Open Epic Games Launcher > Unreal Engine > Library, or open the existing project directly at `C:\UnrealProjects\ManOfMettle\ManOfMettle.uproject`. If the editor requests conversion, back up first, then use a copy.
2. In Content Drawer, find the existing Third Person character asset; note its actual name/path and whether the project is Standard or Combat. Do not rename it. Keep existing startup map.
3. Click Play and check movement and jumping; Stop. If player does not spawn/move, stop and capture exact error before making more assets.

### Blueprint smoke test (about 10–15 minutes)
4. Content Drawer > Add (+) > New Folder: `HeavyMettle` if absent. Open it > Add (+) > New Folder: `Blueprints`.
5. Inside `Blueprints`: Add (+) > Blueprint Class > Actor > name `BP_HM_StartupProbe`. Double-click.
6. My Blueprint > Variables > + > name `bProbeEnabled` > Boolean. Compile once, set its Default Value = True in Details.
7. Event Graph: connect `Event BeginPlay` execution to `Branch`. Drag `bProbeEnabled` as Get into Branch Condition.
8. Drag from Branch True > search `Print String`. Set In String = `HEAVY METTLE: BLUEPRINT READY`, Duration = `3.0`, Print to Screen = true. Do not use Tick.
9. Click Compile (verify green check) > Save. Return to level, drag `BP_HM_StartupProbe` from Content Drawer into the visible floor of the level. Save level.
10. Hit Play (PIE). Watch the top left for the three-second message, and use move/jump. Stop when done.

### Exactly three PIE tests
1. Startup: click Play. Expected player pawn spawns in original map (otherwise fail and record).
2. Movement: move, rotate camera, jump. Expected existing controls still function (otherwise fail and record).
3. Custom Blueprint: on Play the message appears once per session for three seconds. Expected compile check is green, no errors in Output Log (otherwise fail and record).

**Commit message (after real assets are committed):** `test(unreal): verify ManOfMettle template and Blueprint startup probe`

**Progress log, fill only after testing:** `2026-10-27 | VERIFIED/FAILED | P0 template [Standard/Combat], actor [actual path], movement [pass/fail], probe [pass/fail], compile [pass/fail] | Next [blocker/next milestone]`

**Notes:** Unreal starter asset paths vary. Never assume `BP_HM_Player` is a child of a pre-existing C++ class; GAME1 is Blueprint-first. The probe is a temporary diagnostic, not required for the finished game.
