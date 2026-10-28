"""Regression tests for the scaffold spec and generator, runnable without Unreal.

    python -m unittest discover -s Scripts/tests -v

The generator test runs Scripts/create_blueprint_scaffolds.py against a small
FAKE `unreal` module. That checks the script's own logic (which Blueprints it
creates, parents, defaults, re-run safety, template handling). It cannot prove
the real Unreal Python API behaves the same — only running it in the editor can.
"""
import copy
import os
import runpy
import sys
import tempfile
import types
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(REPO, "Scripts")
sys.path.insert(0, SCRIPTS)
import hm_scaffold_spec as spec_tools  # noqa: E402


class SpecTests(unittest.TestCase):
    def setUp(self):
        self.spec = spec_tools.load_spec(REPO)
        self.balance = spec_tools.load_balance(REPO)

    def test_real_spec_is_valid(self):
        self.assertEqual(spec_tools.validate_spec(self.spec, self.balance), [])

    def test_second_inventory_is_rejected(self):
        spec = copy.deepcopy(self.spec)
        spec["scaffolds"].append({"name": "BP_HM_Backpack", "owner": "inventory", "parent": "engine:ActorComponent"})
        problems = spec_tools.validate_spec(spec, self.balance)
        self.assertTrue(any("already owned by BP_HM_InventoryComponent" in p for p in problems), problems)

    def test_missing_balance_key_is_reported(self):
        spec = copy.deepcopy(self.spec)
        spec["scaffolds"][2]["variables"][0]["default"] = {"balance": "combat.doesNotExist"}
        problems = spec_tools.validate_spec(spec, self.balance)
        self.assertTrue(any("combat.doesNotExist" in p for p in problems), problems)

    def test_bad_type_and_parent_are_reported(self):
        spec = copy.deepcopy(self.spec)
        spec["scaffolds"].append({"name": "BP_HM_Odd", "parent": "Character",
                                  "variables": [{"name": "X", "type": "map:name"}]})
        problems = spec_tools.validate_spec(spec, self.balance)
        self.assertTrue(any("prefix" in p for p in problems), problems)
        self.assertTrue(any("unsupported type" in p for p in problems), problems)

    def test_defaults_come_from_balance(self):
        android = next(e for e in self.spec["scaffolds"] if e["name"] == "BP_HM_Android")
        lock = next(v for v in android["variables"] if v["name"] == "LockOnRangeCm")
        self.assertEqual(spec_tools.resolve_default(lock["default"], self.balance),
                         self.balance["player"]["lockOnRangeCm"])


# ---------------------------------------------------------------- fake unreal
class FakeClass:
    def __init__(self, name):
        self.name = name

    def static_class(self):
        return self

    def static_struct(self):
        return self

    def __repr__(self):
        return "<class " + self.name + ">"


class FakeCDO:
    def __init__(self):
        self.props = {}

    def set_editor_property(self, name, value):
        # Mimic Unreal Python: snake_case names, and bools lose their 'b' ('bCanFire' -> 'can_fire').
        if any(c.isupper() for c in name) or name.startswith("b_"):
            raise AttributeError(name)
        self.props[name] = value


class FakeBlueprint:
    def __init__(self, path, parent):
        self.path, self.parent = path, parent
        self.variables, self.functions = {}, []
        self._class = FakeClass(path.rsplit("/", 1)[-1] + "_C")
        self.cdo = FakeCDO()

    def generated_class(self):
        return self._class


def make_fake_unreal(template_assets, saved_dir, project_dir):
    store = {}  # asset path -> FakeBlueprint
    for path in template_assets:
        store[path.split(".")[0]] = FakeBlueprint(path.split(".")[0], "template")
    cdos = {}
    u = types.ModuleType("unreal")
    u.logs = []
    u.log = lambda m: u.logs.append(("log", m))
    u.log_warning = lambda m: u.logs.append(("warn", m))
    u.log_error = lambda m: u.logs.append(("error", m))
    u.Name = str
    u.Blueprint = FakeBlueprint
    for cls in ("Actor", "Pawn", "ActorComponent", "Character", "GameModeBase", "SaveGame", "Transform", "Vector", "Rotator"):
        setattr(u, cls, FakeClass(cls))
    u.BlueprintInterfaceFactory = lambda: "interface-factory"
    u.Paths = types.SimpleNamespace(project_dir=lambda: project_dir, project_saved_dir=lambda: saved_dir)

    def load_asset(path):
        return store.get(path.split(".")[0])

    def does_asset_exist(path):
        return path.split(".")[0] in store

    u.load_asset = load_asset
    u.EditorAssetLibrary = types.SimpleNamespace(
        does_directory_exist=lambda p: True, make_directory=lambda p: True,
        list_assets=lambda root, recursive=True, include_folder=False: list(template_assets),
        does_asset_exist=does_asset_exist, save_loaded_asset=lambda a: True)

    def create_with_parent(path, parent):
        bp = FakeBlueprint(path, parent)
        store[path] = bp
        return bp

    def create_asset(name, folder, cls, factory):
        return create_with_parent(folder + "/" + name, "interface")

    u.AssetToolsHelpers = types.SimpleNamespace(
        get_asset_tools=lambda: types.SimpleNamespace(create_asset=create_asset))
    u.BlueprintEditorLibrary = types.SimpleNamespace(
        get_basic_type_by_name=lambda n: str(n),
        get_set_type=lambda t: "set<" + t + ">",
        get_map_type=lambda k, v: "map<" + k + "," + v + ">",
        get_struct_type=lambda s: "struct<" + s.name + ">",
        get_object_reference_type=lambda c: "object<" + c.name + ">",
        create_blueprint_asset_with_parent=create_with_parent,
        add_member_variable=lambda bp, n, t: bp.variables.setdefault(n, t) is not None,
        add_function_graph=lambda bp, f: bp.functions.append(f),
        compile_blueprint=lambda bp: None)

    def get_default_object(cls):
        return cdos.setdefault(cls.name, FakeCDO())

    u.get_default_object = get_default_object
    u.store, u.cdos = store, cdos
    return u


STANDARD = ["/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter",
            "/Game/ThirdPerson/Blueprints/BP_ThirdPersonGameMode.BP_ThirdPersonGameMode",
            "/Game/ThirdPerson/Maps/Lvl_ThirdPerson.Lvl_ThirdPerson"]
COMBAT = STANDARD + ["/Game/Variant_Combat/Blueprints/BP_CombatCharacter.BP_CombatCharacter",
                     "/Game/Variant_Combat/Blueprints/BP_CombatGameMode.BP_CombatGameMode",
                     "/Game/Variant_Combat/Blueprints/AI/BP_CombatEnemy.BP_CombatEnemy"]
ROOT = "/Game/HeavyMettle/Blueprints/"


class GeneratorTests(unittest.TestCase):
    def run_script(self, fake):
        sys.modules["unreal"] = fake
        try:
            return runpy.run_path(os.path.join(SCRIPTS, "create_blueprint_scaffolds.py"), run_name="__main__")
        finally:
            del sys.modules["unreal"]

    def fake(self, assets):
        self.saved = tempfile.mkdtemp()
        return make_fake_unreal(assets, self.saved, REPO)

    def test_standard_template_creates_everything(self):
        u = self.fake(STANDARD)
        result = self.run_script(u)
        self.assertEqual(result["errors"], [])
        names = [e["name"] for e in spec_tools.load_spec(REPO)["scaffolds"]]
        self.assertEqual(sorted(result["created"]), sorted(names))
        android = u.store[ROOT + "BP_HM_Android"]
        self.assertEqual(android.parent.name, "BP_ThirdPersonCharacter_C")  # child, not a copy
        self.assertEqual(u.store[ROOT + "BP_HM_Enemy"].parent.name, "Character")  # no template enemy -> fallback
        self.assertIn("map<name,int>", u.store[ROOT + "BP_HM_QuestComponent"].variables.values())
        self.assertNotIn("ReturnedCells", u.store[ROOT + "BP_HM_QuestComponent"].variables)
        stats = u.cdos["BP_HM_StatsComponent_C"].props
        self.assertEqual(stats["max_health"], 100.0)
        self.assertEqual(u.cdos["BP_HM_Android_C"].props["can_fire"], True)
        self.assertEqual(u.cdos["BP_HM_GameMode_C"].props["default_pawn_class"].name, "BP_HM_Android_C")
        self.assertTrue(os.path.exists(os.path.join(self.saved, "HM_ScaffoldReport.md")))

    def test_second_run_changes_nothing(self):
        u = self.fake(STANDARD)
        self.run_script(u)
        u.cdos["BP_HM_StatsComponent_C"].props["max_health"] = 250.0  # player tuned it
        result = self.run_script(u)
        self.assertEqual(result["created"], [])
        self.assertEqual(u.cdos["BP_HM_StatsComponent_C"].props["max_health"], 250.0)

    def test_two_templates_means_ask_not_guess(self):
        u = self.fake(COMBAT)
        result = self.run_script(u)
        self.assertNotIn("BP_HM_Android", result["created"])
        self.assertNotIn("BP_HM_GameMode", result["created"])  # no silent GameModeBase fallback
        self.assertEqual(u.store[ROOT + "BP_HM_Enemy"].parent.name, "BP_CombatEnemy_C")
        self.assertTrue(any("TEMPLATE_CHARACTER" in step for step in result["manual"]))

    def test_old_scaffolds_are_flagged_not_deleted(self):
        u = self.fake(STANDARD + ["/Game/HeavyMettle/Blueprints/BP_HM_QuestTracker.BP_HM_QuestTracker"])
        result = self.run_script(u)
        self.assertIn(ROOT + "BP_HM_QuestTracker", u.store)
        self.assertTrue(any("BP_HM_QuestTracker" in step and "BP_HM_QuestComponent" in step
                            for step in result["manual"]))


if __name__ == "__main__":
    unittest.main()
