# Quest trigger and interaction flow (design for issue #4)

**Status: DESIGN.** Nothing here is built or tested in Unreal yet. Scaffolds come from `Scripts/create_blueprint_scaffolds.py`; every graph below still has to be wired and passed in Play In Editor.

## 1. The clean design, in plain terms

Three pieces, each with one job:

1. **One interface** (`BPI_HM_Interactable`) — anything you can press Interact on: Oren, the crate, the crafting bench, a pickup. The player never needs to know *what* it is.
2. **One quest component** (`BP_HM_QuestComponent`, on the player) — the only place quest state lives: a stage number per quest, plus flags for choices. Everything else *asks* it or *tells* it; nothing keeps its own copy.
3. **One reusable trigger** (`BP_HM_QuestTrigger`) — walking into an area advances a quest. Configure it per placement (QuestID, RequiredStage, NewStage) instead of making a new Blueprint for each step.

Things *listen* for changes (event dispatchers) instead of checking every frame (Tick). That's the main performance rule.

## 2. Class and component structure

```
BP_HM_Android (child of your template character)
 ├─ BP_HM_StatsComponent      health / stamina / battery / XP
 ├─ BP_HM_InventoryComponent  Items: Map<Name,int>, Chits
 ├─ BP_HM_QuestComponent      QuestStages, QuestFlags, CompletedQuests, GrantedRewards
 └─ BP_HM_FactionComponent    Reputation: Map<Name,int>
BP_HM_GameMode
 └─ BP_HM_SaveManager         the only thing that calls Save/Load Game to Slot
BP_HM_SaveGame                plain data copied from the components above
Implements BPI_HM_Interactable:  BP_HM_QuestGiver · BP_HM_LootPickup · BP_HM_CraftingBench
Level actors:                    BP_HM_QuestTrigger (box overlap)
```

## 3. Variables, inputs, states, events

**Input:** `IA_Interact` (keyboard E / gamepad face-bottom). Bind the **Started** trigger, not Triggered, so one press = one call.

**Interface functions:** `Interact(Interactor)`, `CanInteract(Interactor) → bCanInteract`, `GetInteractPrompt() → Prompt`.

**Quest component state:**

| Variable | Type | Meaning |
| --- | --- | --- |
| QuestStages | Map Name→Int | stage per quest; missing = not started |
| QuestFlags | Set of Name | choices and facts, e.g. `MC_PARLEY`, `MC_RETURNED` |
| CompletedQuests | Set of Name | finished quests |
| GrantedRewards | Set of Name | rewards already paid, so a reload can't pay twice |

**Event:** `OnQuestUpdated(QuestID, Stage)` — the journal, NPC dialogue and objective marker bind to this.

**Missing Cells stages** (gaps of 10 so new steps can be inserted later without breaking saves):

| Stage | Meaning | Set by |
| --- | --- | --- |
| 10 | Accepted job from Oren | QuestGiver Interact |
| 20 | Found trail at east gate (`TRACKED`) | QuestTrigger at east gate |
| 30 | Reached the Old Relay | QuestTrigger at Relay |
| 40 | Relay resolved — flag `MC_FIGHT` or `MC_PARLEY` | last bandit dies / parley choice |
| 50 | Chose outcome — flag `MC_RETURNED` or `MC_LEFT_WITH_BANDITS` | crate Interact / Oren dialogue |
| 100 | Complete, reward paid once | Oren Interact |

## 4. Logic flow

```
IA_Interact (Started)
  -> TryInteract on BP_HM_Android:
       SphereTrace from camera, radius 30, length InteractRangeCm, ignore self
       hit actor implements BPI_HM_Interactable?  -> CanInteract?  -> Interact(self)

BP_HM_QuestGiver.Interact(Interactor):
  Quest = Interactor's BP_HM_QuestComponent
  stage = Quest.GetStage(QuestID)
  if stage == 0:       Quest.StartQuest(QuestID)          # -> 10
  elif stage == 50:    Quest.CompleteQuest(QuestID)       # -> 100
                       if Quest.GrantRewardOnce("MC_PAY"):
                           Inventory.Chits += (MC_RETURNED ? 60 : 0) ; Stats.AddExperience(questXP)
  else:                say the line for this stage

BP_HM_QuestTrigger.OnBeginOverlap(Other):
  if Other is not the player: return
  Quest = Other's BP_HM_QuestComponent
  if Quest.GetStage(QuestID) == RequiredStage:
      Quest.SetStage(QuestID, NewStage); if FlagToSet: Quest.SetFlag(FlagToSet)
      if bTriggerOnce: disable collision

QuestComponent.SetStage(ID, Stage):
  if Stage <= GetStage(ID): return        # never go backwards
  QuestStages[ID] = Stage ; OnQuestUpdated.Broadcast(ID, Stage)

QuestComponent.GrantRewardOnce(RewardID) -> bool:
  if RewardID in GrantedRewards: return false
  GrantedRewards.Add(RewardID) ; ask SaveManager to save ; return true
```

## 5. Data-driven vs hard-coded

- **Data now:** all numbers (`data/balance.json`: interact range, quest XP), per-placement trigger settings (Details panel), QuestIDs/flags as Names.
- **Data later:** `DT_HM_Quests` (stage text, objective marker target) once there is a second quest. One quest doesn't justify a DataTable yet.
- **Hard-coded on purpose:** the stage numbers in the table above, written in exactly one place (this doc + the QuestGiver graph comments).

## 6. Cut first if it gets slow or confusing

The on-screen **"Press E" prompt**. Use a Print String in `Interact` until the whole quest works. If you do add a prompt, check it with a 0.1-second looping Timer, not Tick.

## 7. Next working session checklist

- [ ] Run `Scripts/create_blueprint_scaffolds.py`; work through `Saved/HM_ScaffoldReport.md` (interface pins, dispatchers, components).
- [ ] `IA_Interact` input action + mapping; call `TryInteract` on Started.
- [ ] `BP_HM_QuestComponent`: implement `GetStage`, `SetStage`, `SetFlag`, `HasFlag`.
- [ ] `BP_HM_QuestGiver` (Oren) → stage 10. Print the stage on `OnQuestUpdated`.
- [ ] Place two `BP_HM_QuestTrigger`s (east gate 10→20, Relay 20→30).
- [ ] PIE tests below. Only then: outcomes, reward, save.

## 8. Likely failure points

- Interface added to the Blueprint but **not** in Class Settings → Implemented Interfaces, so `Does Implement Interface` is false.
- Trace hits the player's own capsule → add self to *Actors to Ignore*.
- Interact fires twice → input bound to **Triggered** instead of **Started**.
- Name typos: `Q_MISSING_CELLS` vs `Q_MissingCells` in two places. Copy-paste the Name.
- Reward paid again after Load → the reward wasn't added to `GrantedRewards` *before* the save.
- Trigger fires for enemies → check the overlapping actor is the player pawn.

## 9. Debugging

- On the trace node set **Draw Debug Type = For Duration** to see the interaction ray.
- Click a node, press **F9** for a breakpoint; hover variables while paused in PIE.
- Bind `OnQuestUpdated` to a Print String showing `QuestID : Stage` — a live quest log for free.
- Output Log filter `LogBlueprintUserMessages` to see only your prints.

## 10. Play In Editor test plan

1. **Interact:** walk to Oren, press E. *Expected:* `Q_MISSING_CELLS : 10` printed once. Pressing E again prints Oren's "go look at the east gate" line, stage stays 10.
2. **Trigger order:** walk into the Relay trigger *before* the east-gate trigger. *Expected:* nothing happens. Then east gate → `: 20`, Relay → `: 30`.
3. **Once only:** walk back through the east-gate trigger. *Expected:* no print, stage stays 30.
