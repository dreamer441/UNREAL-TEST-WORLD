import unreal


def _add_entry(menu, section, name, label, tooltip, command):
    entry = unreal.ToolMenuEntry(name=name, type=unreal.MultiBlockType.MENU_ENTRY)
    entry.set_label(label)
    entry.set_tool_tip(tooltip)
    entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "", command)
    menu.add_menu_entry(section, entry)


def register_amadeus_menu():
    menus = unreal.ToolMenus.get()
    tools_menu = menus.extend_menu("LevelEditor.MainMenu.Tools")
    section_name = "AMADEUS"
    try:
        tools_menu.add_section(section_name, "AMADEUS")
    except Exception:
        pass

    reload_prefix = "import importlib, amadeus_tools; importlib.reload(amadeus_tools); "

    _add_entry(
        tools_menu, section_name,
        "AMADEUS.MakeSelectedGroundEarth",
        "Make Selected Ground Earth",
        "Apply the brown Earth visual material to the selected Landscape family.",
        reload_prefix + "amadeus_tools.make_selected_ground_earth()")

    _add_entry(
        tools_menu, section_name,
        "AMADEUS.CreateDeformableEarthBlock",
        "Create Earth Material Block",
        "Spawn the modular Earth block with physical properties and subtractive runtime geometry.",
        reload_prefix + "amadeus_tools.create_deformable_earth_block()")

    _add_entry(
        tools_menu, section_name,
        "AMADEUS.Create4mEarthTarget",
        "Create 4m Earth Subtraction Target",
        "Spawn a 4m x 4m x 4m Earth block for kinetic-energy material subtraction testing.",
        reload_prefix + "amadeus_tools.create_4m_earth_target()")

    _add_entry(
        tools_menu, section_name,
        "AMADEUS.InspectSelectedActor",
        "Inspect Selected Actor",
        "Show the selected actor class and components.",
        reload_prefix + "amadeus_tools.inspect_selected_actor()")

    menus.refresh_all_widgets()
    unreal.log("[AMADEUS] Unreal Tools + Material Interaction v0.1 + Earth Foundation v0.3 loaded.")


register_amadeus_menu()
