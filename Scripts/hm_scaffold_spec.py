"""Shared, Unreal-free helpers for data/blueprint_scaffolds.json.

Used by Scripts/create_blueprint_scaffolds.py (inside the Unreal Editor) and by
Scripts/validate_repo.py (on any PC or in GitHub Actions), so both read the
scaffold list and data/balance.json the same way.
"""
import json
import os

SPEC_PATH = os.path.join("data", "blueprint_scaffolds.json")
BALANCE_PATH = os.path.join("data", "balance.json")

BASIC_TYPES = {"bool", "int", "real", "name", "string", "text"}
STRUCT_TYPES = {"Transform", "Vector", "Rotator"}
OBJECT_TYPES = {"Actor", "Pawn"}
ENGINE_PARENTS = {"Actor", "ActorComponent", "Character", "GameModeBase", "SaveGame"}
TEMPLATE_ROLES = {"Character", "GameMode", "Enemy"}


def load_json(repo_root, relative_path):
    with open(os.path.join(repo_root, relative_path), encoding="utf-8") as handle:
        return json.load(handle)


def load_spec(repo_root):
    return load_json(repo_root, SPEC_PATH)


def load_balance(repo_root):
    return load_json(repo_root, BALANCE_PATH)


def balance_value(balance, dotted_path):
    """Return balance['a']['b'] for 'a.b', or raise KeyError with the path."""
    node = balance
    for part in dotted_path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(dotted_path)
        node = node[part]
    return node


def resolve_default(default, balance):
    """Turn a spec default (literal or {"balance": "a.b"}) into a plain value."""
    if isinstance(default, dict) and "balance" in default:
        return balance_value(balance, default["balance"])
    return default


def split_type(type_string):
    """'map:name:int' -> ('map', ['name', 'int']); 'real' -> ('real', [])."""
    parts = type_string.split(":")
    return parts[0], parts[1:]


def type_problem(type_string):
    """Return None if the variable type is supported, else a short reason."""
    kind, args = split_type(type_string)
    if kind in BASIC_TYPES and not args:
        return None
    if kind == "set" and len(args) == 1 and args[0] in BASIC_TYPES:
        return None
    if kind == "map" and len(args) == 2 and all(a in BASIC_TYPES for a in args):
        return None
    if kind == "struct" and len(args) == 1 and args[0] in STRUCT_TYPES:
        return None
    if kind == "object" and len(args) == 1 and args[0] in OBJECT_TYPES:
        return None
    return "unsupported type '" + type_string + "'"


def parent_problem(parent):
    """Parents look like 'engine:ActorComponent' or 'template:Character'."""
    if parent is None:
        return None
    if ":" not in parent:
        return "parent '" + str(parent) + "' needs a 'engine:' or 'template:' prefix"
    source, name = parent.split(":", 1)
    if source == "engine" and name in ENGINE_PARENTS:
        return None
    if source == "template" and name in TEMPLATE_ROLES:
        return None
    return "unknown parent '" + parent + "'"


def validate_spec(spec, balance):
    """Return a list of human-readable problems (empty list = OK)."""
    problems = []
    seen_names = set()
    owners = {}
    for entry in spec.get("scaffolds", []):
        name = entry.get("name", "<missing name>")
        where = name + ": "
        if name in seen_names:
            problems.append(where + "listed twice")
        seen_names.add(name)
        if not (name.startswith("BP_HM_") or name.startswith("BPI_HM_")):
            problems.append(where + "name must start with BP_HM_ or BPI_HM_")

        owner = entry.get("owner")
        if owner:
            if owner in owners:
                problems.append(where + "owns '" + owner + "', already owned by " + owners[owner]
                                + " (one system = one owner; no second inventory/quest/save)")
            owners[owner] = name

        kind = entry.get("kind", "blueprint")
        if kind == "interface":
            if not name.startswith("BPI_"):
                problems.append(where + "interfaces must be named BPI_HM_*")
            if entry.get("variables"):
                problems.append(where + "interfaces cannot have variables")
        elif kind == "blueprint":
            for key in ("parent", "fallback_parent"):
                reason = parent_problem(entry.get(key))
                if reason:
                    problems.append(where + reason)
            if entry.get("parent") is None:
                problems.append(where + "missing parent")
        else:
            problems.append(where + "unknown kind '" + str(kind) + "'")

        var_names = set()
        for variable in entry.get("variables", []):
            var_name = variable.get("name", "")
            if var_name in var_names:
                problems.append(where + "variable " + var_name + " listed twice")
            var_names.add(var_name)
            reason = type_problem(variable.get("type", ""))
            if reason:
                problems.append(where + var_name + ": " + reason)
            if "default" in variable:
                try:
                    value = resolve_default(variable["default"], balance)
                except KeyError as missing:
                    problems.append(where + var_name + ": balance.json has no '" + str(missing.args[0]) + "'")
                    continue
                kind_of_var = split_type(variable["type"])[0]
                if kind_of_var in ("int", "real") and not isinstance(value, (int, float)):
                    problems.append(where + var_name + ": default is not a number")
                if kind_of_var == "int" and isinstance(value, float) and not value.is_integer():
                    problems.append(where + var_name + ": int default " + str(value) + " is fractional")
                if kind_of_var == "bool" and not isinstance(value, bool):
                    problems.append(where + var_name + ": default is not true/false")

        function_names = entry.get("functions", [])
        if len(function_names) != len(set(function_names)):
            problems.append(where + "a function is listed twice")
    return problems
