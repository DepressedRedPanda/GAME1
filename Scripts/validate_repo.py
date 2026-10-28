#!/usr/bin/env python3
"""Repository checks that run WITHOUT Unreal (on your PC or in GitHub Actions).

    python Scripts/validate_repo.py

Checks:
  1. data/balance.json values are present and sensible.
  2. data/blueprint_scaffolds.json is valid, every default it pulls from
     balance.json exists, and no two Blueprints own the same system
     (no second inventory / quest tracker / save system).
  3. Every Blueprint named in docs/UNIFIED_GAME_ARCHITECTURE.md
     "Unified runtime ownership" has a scaffold, and vice versa.
  4. Every Python script in Scripts/ has valid syntax.
  5. File paths mentioned in active docs exist (Legacy/ and Research/ are skipped).
  6. Nothing that looks like an API key is committed.

A pass means the text in the repo is consistent. It does NOT mean anything
compiles or works in Unreal: that still needs the editor and Play In Editor.
"""
import os
import py_compile
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "Scripts"))
import hm_scaffold_spec as spec_tools  # noqa: E402

errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


# 1. balance.json ------------------------------------------------------------
def check_balance(balance):
    required = {
        "player.baseHealth": (1, 10000), "player.baseStamina": (1, 10000),
        "player.baseBattery": (1, 10000), "player.walkSpeed": (50, 2000),
        "player.sprintSpeed": (50, 3000), "player.lockOnRangeCm": (50, 350),
        "player.mantleMaxHeightCm": (50, 400), "player.interactRangeCm": (50, 600),
        "player.inventorySlots": (1, 500),
        "combat.pistolDamage": (1, 1000), "combat.magazine": (1, 100),
        "combat.reserveAmmo": (0, 1000), "combat.fireCooldownSeconds": (0.03, 3),
        "combat.lightDamage": (1, 1000), "combat.heavyDamage": (1, 1000),
        "combat.lightStamina": (0, 1000), "combat.heavyStamina": (0, 1000),
        "combat.parryWindowSeconds": (0.05, 0.5), "combat.guardStaminaPerSecond": (0, 1000),
        "combat.banditHP": (1, 10000), "combat.banditXP": (0, 10000),
        "progression.questXP": (0, 100000), "progression.baseXPToLevel": (1, 100000),
        "progression.xpStepPerLevel": (0, 100000),
    }
    for path, (low, high) in required.items():
        try:
            value = spec_tools.balance_value(balance, path)
        except KeyError:
            errors.append("balance.json: missing " + path)
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append("balance.json: " + path + " must be a number")
        elif not low <= value <= high:
            errors.append("balance.json: " + path + " = " + str(value) + " is outside " + str(low) + "-" + str(high))
    try:
        check(balance["player"]["sprintSpeed"] > balance["player"]["walkSpeed"],
              "balance.json: sprintSpeed should be faster than walkSpeed")
        check(balance["combat"]["heavyDamage"] > balance["combat"]["lightDamage"],
              "balance.json: heavyDamage should be more than lightDamage")
    except (KeyError, TypeError):
        pass  # already reported above
    recipe_ids = set()
    for recipe in balance.get("recipes", []):
        rid = recipe.get("id")
        check(rid and rid not in recipe_ids, "balance.json: recipe id missing or duplicated: " + str(rid))
        recipe_ids.add(rid)
        check(isinstance(recipe.get("output"), int) and recipe["output"] > 0,
              "balance.json: recipe " + str(rid) + " output must be a whole number above 0")
        cost = recipe.get("cost", {})
        check(bool(cost), "balance.json: recipe " + str(rid) + " has no cost")
        for item, amount in cost.items():
            check(isinstance(amount, int) and amount > 0,
                  "balance.json: recipe " + str(rid) + " cost of " + item + " must be a whole number above 0")


# 3. architecture <-> scaffolds ---------------------------------------------
def architecture_names():
    path = os.path.join(REPO, "docs", "UNIFIED_GAME_ARCHITECTURE.md")
    text = open(path, encoding="utf-8").read()
    match = re.search(r"## Unified runtime ownership.*?(?=\n## )", text, re.S)
    if not match:
        errors.append("UNIFIED_GAME_ARCHITECTURE.md: section 'Unified runtime ownership' not found")
        return set()
    return set(re.findall(r"`(BPI?_HM_[A-Za-z]+)`", match.group(0)))


# 5. doc paths -----------------------------------------------------------------
PATH_TOKEN = re.compile(r"(?<![\w/.])((?:docs|Scripts|data|Research|Legacy|\.github)/[\w./-]+\.(?:md|py|json|yml|sh))")
MD_LINK = re.compile(r"\]\(([^)#\s]+)\)")


def active_docs():
    for folder, dirs, files in os.walk(REPO):
        rel = os.path.relpath(folder, REPO)
        top = rel.split(os.sep)[0]
        if top in (".git", "Legacy", "Research"):
            dirs[:] = []
            continue
        for name in files:
            if name.endswith(".md"):
                yield os.path.join(folder, name)


def check_doc_paths():
    for doc in active_docs():
        text = open(doc, encoding="utf-8").read()
        here = os.path.dirname(doc)
        rel_doc = os.path.relpath(doc, REPO)
        for target in MD_LINK.findall(text):
            if "://" in target or target.startswith("mailto:"):
                continue
            check(os.path.exists(os.path.normpath(os.path.join(here, target))),
                  rel_doc + ": link to missing file " + target)
        for target in PATH_TOKEN.findall(text):
            target = target.rstrip(".")
            check(os.path.exists(os.path.join(REPO, target)) or os.path.exists(os.path.join(here, target)),
                  rel_doc + ": mentions missing file " + target)


# 6. secrets -------------------------------------------------------------------
SECRET = re.compile(r"(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|AIza[0-9A-Za-z_-]{35}|ghp_[A-Za-z0-9]{36})")


def tracked_files():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True).stdout
        return [os.path.join(REPO, f) for f in out.splitlines()]
    except Exception:
        return [os.path.join(d, f) for d, _, fs in os.walk(REPO) if ".git" not in d for f in fs]


def main():
    balance = spec_tools.load_balance(REPO)
    spec = spec_tools.load_spec(REPO)
    check_balance(balance)

    errors.extend("blueprint_scaffolds.json: " + p for p in spec_tools.validate_spec(spec, balance))
    scaffold_names = {entry["name"] for entry in spec.get("scaffolds", [])}
    owned = {entry["name"] for entry in spec.get("scaffolds", []) if entry.get("owner")}
    for name in sorted(architecture_names() - scaffold_names):
        errors.append("architecture lists " + name + " but data/blueprint_scaffolds.json has no scaffold for it")
    for name in sorted(owned - architecture_names()):
        errors.append(name + " owns a system but is not in the architecture's 'Unified runtime ownership' list")
    for old in spec.get("legacy_names", {}):
        check(old not in scaffold_names, "blueprint_scaffolds.json: retired name " + old + " is still being created")

    scripts = os.path.join(REPO, "Scripts")
    for name in sorted(os.listdir(scripts)):
        if name.endswith(".py"):
            try:
                py_compile.compile(os.path.join(scripts, name), doraise=True)
            except py_compile.PyCompileError as exc:
                errors.append("Scripts/" + name + ": syntax error: " + str(exc.msg).strip())

    check_doc_paths()

    for path in tracked_files():
        if not os.path.isfile(path) or os.path.getsize(path) > 2_000_000:
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        if SECRET.search(text):
            errors.append(os.path.relpath(path, REPO) + ": looks like it contains an API key. Remove it and rotate the key.")

    print("Scaffolds: " + str(len(scaffold_names)) + " | balance values checked | docs scanned")
    unique = list(dict.fromkeys(errors))  # same problem twice in one file -> report once
    errors[:] = unique
    if errors:
        print("\n" + str(len(errors)) + " problem(s):")
        for error in errors:
            print("  - " + error)
        print("\nThis checks repo text only; Unreal compile and PIE are separate.")
        return 1
    print("OK. Repo text is consistent. (Not proof of an Unreal compile or PIE.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
