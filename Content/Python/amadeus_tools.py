import unreal

MATERIAL_PACKAGE_PATH = "/Game/AMADEUS/Materials"
MATERIAL_ASSET_NAME = "M_AMADEUS_Earth_v13"
MATERIAL_OBJECT_PATH = f"{MATERIAL_PACKAGE_PATH}/{MATERIAL_ASSET_NAME}"
EARTH_BLOCK_CLASS_PATH = "/Script/EarthFoundation.EarthBlockActor"


def _log(message: str, warning: bool = False) -> None:
    (unreal.log_warning if warning else unreal.log)(f"[AMADEUS] {message}")


def _class_name(obj) -> str:
    try:
        return obj.get_class().get_name()
    except Exception:
        return type(obj).__name__


def _create_earth_material():
    if unreal.EditorAssetLibrary.does_asset_exist(MATERIAL_OBJECT_PATH):
        material = unreal.EditorAssetLibrary.load_asset(MATERIAL_OBJECT_PATH)
        if material:
            return material

    unreal.EditorAssetLibrary.make_directory(MATERIAL_PACKAGE_PATH)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    material = asset_tools.create_asset(
        MATERIAL_ASSET_NAME,
        MATERIAL_PACKAGE_PATH,
        unreal.Material,
        unreal.MaterialFactoryNew(),
    )
    if not material:
        raise RuntimeError("Could not create the earth material asset.")

    color = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant3Vector, -420, -120
    )
    color.set_editor_property("constant", unreal.LinearColor(0.18, 0.055, 0.015, 1.0))

    roughness = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant, -420, 40
    )
    roughness.set_editor_property("r", 0.95)

    metallic = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant, -420, 150
    )
    metallic.set_editor_property("r", 0.0)

    unreal.MaterialEditingLibrary.connect_material_property(color, "", unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
    unreal.MaterialEditingLibrary.connect_material_property(metallic, "", unreal.MaterialProperty.MP_METALLIC)
    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(MATERIAL_OBJECT_PATH, only_if_is_dirty=False)
    return material


def _is_landscape(actor) -> bool:
    return "landscape" in _class_name(actor).lower()


def _landscape_root(actor):
    if not _is_landscape(actor):
        return None
    try:
        root = actor.get_editor_property("landscape_actor_ref")
        if root:
            return root
    except Exception:
        pass
    return actor


def _same_landscape_family(actor, root) -> bool:
    if not _is_landscape(actor):
        return False
    if actor == root:
        return True
    try:
        return actor.get_editor_property("landscape_actor_ref") == root
    except Exception:
        return False


def _set_landscape_material(actor, material) -> bool:
    try:
        actor.modify()
    except Exception:
        pass
    try:
        setter = getattr(actor, "editor_set_landscape_material", None)
        if callable(setter):
            setter(material)
            return True
    except Exception as exc:
        _log(f"Landscape editor setter failed on {actor.get_name()}: {exc}", True)
    try:
        actor.set_editor_property("landscape_material", material)
        return True
    except Exception as exc:
        _log(f"Landscape property assignment failed on {actor.get_name()}: {exc}", True)
        return False


def _force_component_refresh(actor) -> None:
    try:
        components = actor.get_components_by_class(unreal.LandscapeComponent)
    except Exception:
        components = []
    for component in components:
        for method_name in ("mark_render_state_dirty", "mark_render_dynamic_data_dirty"):
            try:
                method = getattr(component, method_name, None)
                if callable(method):
                    method()
            except Exception:
                pass


def make_selected_ground_earth() -> None:
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    selected = actor_subsystem.get_selected_level_actors()
    if not selected:
        unreal.EditorDialog.show_message("AMADEUS Tools", "Nothing selected. Click the terrain and run this command again.", unreal.AppMsgType.OK)
        return

    target = selected[0]
    if not _is_landscape(target):
        unreal.EditorDialog.show_message("AMADEUS Tools", f"Selected actor is {_class_name(target)}, not a Landscape.", unreal.AppMsgType.OK)
        return

    material = _create_earth_material()
    root = _landscape_root(target)
    all_actors = actor_subsystem.get_all_level_actors()
    family = [a for a in all_actors if _same_landscape_family(a, root)]
    if root and root not in family:
        family.insert(0, root)
    if not family:
        family = [target]

    changed = []
    with unreal.ScopedEditorTransaction("AMADEUS - Earth Entire Landscape"):
        for actor in family:
            if _set_landscape_material(actor, material):
                changed.append(actor.get_name())
                _force_component_refresh(actor)

    try:
        unreal.EditorLevelLibrary.editor_invalidate_viewports()
    except Exception:
        pass

    unreal.EditorDialog.show_message(
        "AMADEUS Tools",
        f"Earth material applied to {len(changed)} loaded Landscape actor(s). Press Ctrl+S to save.",
        unreal.AppMsgType.OK,
    )


def _earth_block_class():
    try:
        return unreal.load_class(None, EARTH_BLOCK_CLASS_PATH)
    except Exception:
        return None


def create_deformable_earth_block() -> None:
    earth_class = _earth_block_class()
    if not earth_class:
        unreal.EditorDialog.show_message(
            "AMADEUS - Earth Foundation",
            "EarthFoundation C++ module is not loaded yet.\n\nClose Unreal, reopen the project, and allow Unreal to build the new EarthFoundation module. If Unreal reports a compiler/toolchain error, send me that exact message.",
            unreal.AppMsgType.OK,
        )
        return

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = actor_subsystem.get_all_level_actors()

    # Put the test patch near PlayerStart and approximately flush with the playable ground.
    spawn_location = unreal.Vector(1200.0, 0.0, -140.0)
    for actor in all_actors:
        if _class_name(actor) == "PlayerStart":
            p = actor.get_actor_location()
            spawn_location = unreal.Vector(p.x + 1200.0, p.y, p.z - 230.0)
            break

    earth = actor_subsystem.spawn_actor_from_class(earth_class, spawn_location, unreal.Rotator(0.0, 0.0, 0.0), transient=False)
    if not earth:
        unreal.EditorDialog.show_message("AMADEUS - Earth Foundation", "Could not spawn EarthBlockActor.", unreal.AppMsgType.OK)
        return

    earth.set_actor_label("Earth_Deformable_Test_Block")
    material = _create_earth_material()
    try:
        earth.set_earth_visual_material(material)
    except Exception as exc:
        _log(f"Could not apply visual material: {exc}", True)

    actor_subsystem.set_selected_level_actors([earth])

    unreal.EditorDialog.show_message(
        "AMADEUS - Earth Foundation",
        "Created Earth_Deformable_Test_Block.\n\nThis is now a subtractive material body, not a vertex-dent surface.\n\nUse the 4m projectile target command for the kinetic-energy test.\n\nMaterialState owns generic material properties (Density, Hardness, Cohesion, Plasticity, Friction, Restitution, Toughness, Rigidity, Temperature) plus Earth Moisture.",
        unreal.AppMsgType.OK,
    )


def test_dent_selected_earth_block() -> None:
    unreal.EditorDialog.show_message(
        "AMADEUS - Earth Foundation",
        "V0.3 replaced vertex dents with physical volume subtraction. Use Create 4m Earth Subtraction Target, press Play, and fire with E.",
        unreal.AppMsgType.OK,
    )


def create_4m_earth_target() -> None:
    earth_class = _earth_block_class()
    if not earth_class:
        unreal.EditorDialog.show_message(
            "AMADEUS - Earth Physics Test",
            "EarthFoundation module is not loaded. Close Unreal, reopen, and allow the C++ modules to build.",
            unreal.AppMsgType.OK,
        )
        return

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    all_actors = actor_subsystem.get_all_level_actors()

    spawn_location = unreal.Vector(900.0, 0.0, 200.0)
    for actor in all_actors:
        if _class_name(actor) == "PlayerStart":
            p = actor.get_actor_location()
            try:
                fwd = actor.get_actor_forward_vector()
            except Exception:
                fwd = unreal.Vector(1.0, 0.0, 0.0)
            spawn_location = unreal.Vector(
                p.x + (fwd.x * 900.0),
                p.y + (fwd.y * 900.0),
                p.z + 105.0,
            )
            break

    earth = actor_subsystem.spawn_actor_from_class(
        earth_class, spawn_location, unreal.Rotator(0.0, 0.0, 0.0), transient=False
    )
    if not earth:
        unreal.EditorDialog.show_message("AMADEUS - Earth Physics Test", "Could not spawn Earth target.", unreal.AppMsgType.OK)
        return

    earth.set_actor_label("Earth_4m_Subtraction_Target")

    try:
        geometry = earth.get_editor_property("geometry")
        geometry.set_editor_property("block_size_cm", unreal.Vector(400.0, 400.0, 400.0))
        geometry.set_editor_property("surface_resolution", 25)
        geometry.set_editor_property("vertical_resolution", 25)
        earth.rebuild_earth_block()
    except Exception as exc:
        _log(f"Could not configure 4m target geometry: {exc}", True)

    try:
        earth.set_earth_visual_material(_create_earth_material())
    except Exception as exc:
        _log(f"Could not apply Earth visual material: {exc}", True)

    actor_subsystem.set_selected_level_actors([earth])
    unreal.EditorDialog.show_message(
        "AMADEUS - Earth Physics Test",
        "Created a 4m x 4m x 4m subtractive Earth target.\n\nPress Play, face the block, and press E to fire.\n\nProjectile defaults: size 44 cm, mass 100 kg, hardness 0.70, speed 30 m/s. Density is derived from mass / volume.\n\nThe projectile carries PhysicalBody + MaterialCore data only. ImpactSystem calculates contact, energy, target damage, source integrity and post-impact motion; Earth performs the Boolean subtraction.\n\nIn Play mode, press F1 (or TAB) to unlock the mouse and change Speed / Size / Mass / Hardness / Restitution / Toughness / Rigidity. Press F1 (or TAB) again to aim, then E to fire. Gravity is always enabled.",
        unreal.AppMsgType.OK,
    )


def inspect_selected_actor() -> None:
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    selected = actor_subsystem.get_selected_level_actors()
    if not selected:
        unreal.EditorDialog.show_message("AMADEUS Tools", "Nothing selected.", unreal.AppMsgType.OK)
        return
    actor = selected[0]
    lines = [f"Actor: {actor.get_name()}", f"Class: {_class_name(actor)}"]
    if _is_landscape(actor):
        try:
            root = _landscape_root(actor)
            lines.append(f"Landscape root: {root.get_name() if root else 'None'}")
        except Exception as exc:
            lines.append(f"Landscape root lookup failed: {exc}")
        try:
            mat = actor.get_editor_property("landscape_material")
            lines.append(f"Landscape material: {mat.get_path_name() if mat else 'None'}")
        except Exception as exc:
            lines.append(f"Landscape material lookup failed: {exc}")
    component_names = []
    try:
        for component in actor.get_components_by_class(unreal.ActorComponent):
            component_names.append(_class_name(component))
    except Exception:
        pass
    if component_names:
        lines.append("Components: " + ", ".join(component_names[:16]))
    unreal.EditorDialog.show_message("AMADEUS - Selected Actor", "\n".join(lines), unreal.AppMsgType.OK)
