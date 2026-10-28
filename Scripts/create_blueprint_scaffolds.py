"""Create the Heavy Mettle Blueprint scaffolds in Unreal Editor 5.8.

Run: Tools > Execute Python Script > Scripts/create_blueprint_scaffolds.py
(needs the Python Editor Script Plugin and Editor Scripting Utilities).

What it does
- Reads the Blueprint list from data/blueprint_scaffolds.json (names follow
  docs/UNIFIED_GAME_ARCHITECTURE.md) and starting values from data/balance.json.
- Creates each missing Blueprint with its variables and EMPTY function graphs.
  Nothing is wired up: you build the graphs yourself and test them in PIE.
- BP_HM_Android and BP_HM_GameMode are made as CHILDREN of your project's own
  template character / GameMode, so the template's working movement, camera and
  input are inherited instead of copied.

Safe to run again: existing Blueprints are never changed (only re-compiled),
so your edits and tuned values are kept. It never deletes anything and never
changes Project Settings or World Settings.

At the end it prints a checklist of the few steps Python can't do (adding
components, event dispatchers, interface pins) and saves it to
Saved/HM_ScaffoldReport.md in your project folder.
"""
import os
import sys

import unreal

# ---- Optional: paste the asset paths you recorded during the P0 check ------
# Leave "" to auto-detect. Example: "/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter"
TEMPLATE_CHARACTER = ""
TEMPLATE_GAMEMODE = ""
TEMPLATE_ENEMY = ""
# ---------------------------------------------------------------------------

try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:  # some editor execution paths don't define __file__
    SCRIPT_DIR = os.path.join(unreal.Paths.project_dir(), "Scripts")
sys.path.insert(0, SCRIPT_DIR)
import hm_scaffold_spec as spec_tools  # noqa: E402  (shared with validate_repo.py)

LIB = unreal.BlueprintEditorLibrary
ASSETS = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()

created, compiled, skipped, manual, errors = [], [], [], [], []


def find_repo_root():
    """Folder that contains data/blueprint_scaffolds.json."""
    candidates = [os.path.dirname(SCRIPT_DIR), unreal.Paths.project_dir()]
    for folder in candidates:
        if os.path.exists(os.path.join(folder, spec_tools.SPEC_PATH)):
            return folder
    raise RuntimeError("Can't find data/blueprint_scaffolds.json next to the Scripts folder or in the project folder.")


REPO = find_repo_root()
SPEC = spec_tools.load_spec(REPO)
BALANCE = spec_tools.load_balance(REPO)
ROOT = SPEC["root"]

problems = spec_tools.validate_spec(SPEC, BALANCE)
if problems:
    for problem in problems:
        unreal.log_error("HM scaffold spec: " + problem)
    raise RuntimeError("data/blueprint_scaffolds.json has problems (see Output Log). Nothing was created.")

if not ASSETS.does_directory_exist(ROOT):
    ASSETS.make_directory(ROOT)


# ---- Template lookup (done once, not per Blueprint) -------------------------
TEMPLATE_OVERRIDES = {"Character": TEMPLATE_CHARACTER, "GameMode": TEMPLATE_GAMEMODE, "Enemy": TEMPLATE_ENEMY}
TEMPLATE_MATCH = {
    "Character": lambda n: "Character" in n and "Enemy" not in n and "NPC" not in n,
    "GameMode": lambda n: "GameMode" in n,
    "Enemy": lambda n: "Enemy" in n,
}
_template_cache = {}
AMBIGUOUS = object()  # several template candidates: stop and ask, never guess


def _blueprint_candidates():
    """Blueprint asset paths under /Game, excluding our own folder. Listed once."""
    if "_all" not in _template_cache:
        paths = [p for p in ASSETS.list_assets("/Game", recursive=True, include_folder=False)
                 if not p.startswith("/Game/HeavyMettle/") and os.path.basename(p).startswith("BP_")]
        _template_cache["_all"] = paths
    return _template_cache["_all"]


def template_class(role):
    """Template Blueprint class for this role; None if there is none; AMBIGUOUS if several."""
    if role in _template_cache:
        return _template_cache[role]
    result = None
    override = TEMPLATE_OVERRIDES.get(role, "")
    if override:
        asset = unreal.load_asset(override)
        if asset is None:
            errors.append("TEMPLATE_" + role.upper() + " path not found: " + override)
        else:
            result = asset.generated_class()
    else:
        matches = []
        for path in _blueprint_candidates():
            asset_name = os.path.basename(path).split(".")[0]
            if TEMPLATE_MATCH[role](asset_name):
                matches.append(path)
        if len(matches) == 1:
            asset = unreal.load_asset(matches[0])
            if isinstance(asset, unreal.Blueprint):
                result = asset.generated_class()
                unreal.log("HM scaffold: using template " + role + " " + matches[0])
        elif len(matches) > 1:
            result = AMBIGUOUS
            manual.append("Several template " + role + " Blueprints found: " + ", ".join(matches)
                          + ". Paste the one your game uses into TEMPLATE_" + role.upper()
                          + " at the top of this script and run it again.")
    _template_cache[role] = result
    return result


def engine_class(name):
    return getattr(unreal, name)


def resolve_parent(entry):
    for key in ("parent", "fallback_parent"):
        parent = entry.get(key)
        if not parent:
            continue
        source, name = parent.split(":", 1)
        cls = template_class(name) if source == "template" else engine_class(name)
        if cls is AMBIGUOUS:
            return None  # don't fall back to a bare engine class; the report says what to set
        if cls is not None:
            if key == "fallback_parent":
                unreal.log_warning("HM scaffold: " + entry["name"] + " uses fallback parent " + name)
            return cls
    return None


# ---- Variable types ---------------------------------------------------------
def pin_type(type_string):
    """Unreal pin type for 'real', 'map:name:int', 'struct:Transform', ... or None."""
    kind, args = spec_tools.split_type(type_string)
    if kind in spec_tools.BASIC_TYPES:
        return LIB.get_basic_type_by_name(unreal.Name(kind))
    if kind == "set":
        return LIB.get_set_type(pin_type(args[0]))
    if kind == "map":
        return LIB.get_map_type(pin_type(args[0]), pin_type(args[1]))
    if kind == "struct":
        return LIB.get_struct_type(getattr(unreal, args[0]).static_struct())
    if kind == "object":
        return LIB.get_object_reference_type(getattr(unreal, args[0]).static_class())
    return None


def to_unreal_value(type_string, value):
    kind = spec_tools.split_type(type_string)[0]
    if kind == "name":
        return unreal.Name(str(value))
    if kind == "int":
        return int(value)
    if kind == "real":
        return float(value)
    return value


def python_names(variable):
    """Spellings Unreal's Python may use for a Blueprint variable: as written,
    snake_case ('MaxHealth' -> 'max_health', 'XP' -> 'xp') and, for booleans,
    without the 'b' prefix ('bCanFire' -> 'can_fire')."""
    words, current = [], ""
    for i, char in enumerate(variable):
        nxt = variable[i + 1] if i + 1 < len(variable) else ""
        if current and char.isupper() and (not current[-1].isupper() or (nxt and nxt.islower())):
            words.append(current)
            current = ""
        current += char
    words.append(current)
    snake = "_".join(w.lower() for w in words)
    names = [variable]
    if len(words) > 1 and words[0] == "b":
        names.append("_".join(w.lower() for w in words[1:]))  # Unreal drops the bool 'b'
    names.append(snake)
    return names


def set_default(blueprint, variable, value):
    """Set a variable's default on the compiled Blueprint's class defaults."""
    cdo = unreal.get_default_object(blueprint.generated_class())
    for property_name in python_names(variable):
        try:
            cdo.set_editor_property(property_name, value)
            return True
        except Exception:
            continue
    return False


# ---- Creation ---------------------------------------------------------------
def create_interface(entry):
    factory = getattr(unreal, "BlueprintInterfaceFactory", None)
    if factory is None:
        return None
    return TOOLS.create_asset(entry["name"], ROOT, unreal.Blueprint, factory())


def create(entry):
    name, path = entry["name"], ROOT + "/" + entry["name"]
    if ASSETS.does_asset_exist(path):
        bp = unreal.load_asset(path)
        skipped.append(name)
        return bp, False

    if entry.get("kind") == "interface":
        try:
            bp = create_interface(entry)
        except Exception as exc:
            bp = None
            unreal.log_warning("HM scaffold: interface creation failed: " + str(exc))
        if bp is None:
            manual.append("Create " + name + " by hand: Content Browser > Add > Blueprint > Blueprint Interface, "
                          "name it " + name + ", in " + ROOT + ". Add functions: " + ", ".join(entry.get("functions", [])))
            return None, False
    else:
        parent = resolve_parent(entry)
        if parent is None:
            role = entry["parent"].split(":", 1)[1]
            manual.append("Skipped " + name + ": template " + role + " not found or not chosen yet. "
                          "Finish the P0 check, set TEMPLATE_" + role.upper() + " at the top of this script, run again.")
            return None, False
        bp = LIB.create_blueprint_asset_with_parent(path, parent)
        if bp is None:
            errors.append("Cannot create " + path)
            return None, False

    for variable in entry.get("variables", []):
        try:
            pin = pin_type(variable["type"])
            if pin is None or not LIB.add_member_variable(bp, unreal.Name(variable["name"]), pin):
                raise RuntimeError("rejected")
        except Exception as exc:
            manual.append(name + ": add variable " + variable["name"] + " (" + variable["type"]
                          + ") by hand [" + str(exc) + "]")
    for function in entry.get("functions", []):
        try:
            LIB.add_function_graph(bp, function)
        except Exception as exc:
            manual.append(name + ": add function " + function + " by hand [" + str(exc) + "]")
    created.append(name)
    return bp, True


def apply_defaults(entry, bp):
    for variable in entry.get("variables", []):
        if "default" not in variable:
            continue
        value = spec_tools.resolve_default(variable["default"], BALANCE)
        if not set_default(bp, variable["name"], to_unreal_value(variable["type"], value)):
            manual.append(entry["name"] + ": set default " + variable["name"] + " = " + str(value)
                          + " in Class Defaults / the variable's Details panel")


new_blueprints = {}
for entry in SPEC["scaffolds"]:
    bp, is_new = create(entry)
    if bp is None:
        continue
    try:
        # compile_blueprint returns nothing; open the Blueprint to see the green tick.
        LIB.compile_blueprint(bp)
        if is_new and entry.get("kind") != "interface":
            apply_defaults(entry, bp)
            LIB.compile_blueprint(bp)
        ASSETS.save_loaded_asset(bp)
        compiled.append(entry["name"])
    except Exception as exc:
        errors.append(entry["name"] + ": compile/save failed: " + str(exc))
    if is_new:
        new_blueprints[entry["name"]] = bp
        manual.extend(entry["name"] + ": " + step for step in entry.get("manual", []))

# A NEW BP_HM_GameMode spawns BP_HM_Android (an existing GameMode is never touched).
android = new_blueprints.get("BP_HM_Android") or unreal.load_asset(ROOT + "/BP_HM_Android")
if "BP_HM_GameMode" in new_blueprints and android is not None:
    try:
        game_mode = new_blueprints["BP_HM_GameMode"]
        cdo = unreal.get_default_object(game_mode.generated_class())
        cdo.set_editor_property("default_pawn_class", android.generated_class())
        LIB.compile_blueprint(game_mode)
        ASSETS.save_loaded_asset(game_mode)
    except Exception as exc:
        manual.append("BP_HM_GameMode: set Default Pawn Class = BP_HM_Android by hand [" + str(exc) + "]")

# Warn about scaffolds made by the old version of this script.
for old, new in SPEC.get("legacy_names", {}).items():
    if ASSETS.does_asset_exist(ROOT + "/" + old) or ASSETS.does_asset_exist("/Game/HeavyMettle/" + old):
        manual.append("Old scaffold " + old + " exists; its replacement is " + new
                      + ". Move any work you did into the new one, then delete the old one yourself.")

# ---- Report -----------------------------------------------------------------
report = ["# Heavy Mettle scaffold report", "",
          "Created: " + (", ".join(created) or "none"),
          "Already existed (left unchanged): " + (", ".join(skipped) or "none"),
          "Compiled and saved (open each one to confirm the green tick): " + (", ".join(compiled) or "none"), "",
          "## Do these by hand (" + str(len(manual)) + ")"] + ["- [ ] " + step for step in manual]
if errors:
    report += ["", "## Errors"] + ["- " + e for e in errors]
report += ["", "Function graphs are EMPTY. Nothing here is gameplay until you build it and it passes Play In Editor."]
for line in report:
    unreal.log(line)
for error in errors:
    unreal.log_error("HM scaffold: " + error)
try:
    report_path = os.path.join(unreal.Paths.project_saved_dir(), "HM_ScaffoldReport.md")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(report) + "\n")
    unreal.log("HM scaffold checklist saved to " + report_path)
except Exception as exc:
    unreal.log_warning("Could not save report file: " + str(exc))
if errors:
    raise RuntimeError("Some scaffolds failed; see the Output Log / Saved/HM_ScaffoldReport.md.")
