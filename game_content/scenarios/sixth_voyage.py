from samus.text_adventure.engine import Character, Game, Item, Room

INDEX = {"logic plate": 1, "resonant crystal": 2, "ferrite coil": 3}


def use_catalog(game):
    carried = [item.name for item in game.inventory if item.name in INDEX]
    if len(carried) < 3:
        missing = [name for name in INDEX if name not in carried]
        ordered = sorted(carried, key=lambda n: INDEX[n])
        msg = "Catalog hums. "
        if ordered:
            msg += "Indexed: " + ", ".join(n + " at index " + str(INDEX[n]) for n in ordered) + ". "
        msg += "Missing: " + ", ".join(missing) + ". The vaults hold the rest."
        return msg
    game.flags["indexed"] = True
    game.rooms["Foundry Floor"].unblock("north")
    return "Catalog complete. Logic plate at index 1, resonant crystal at index 2, ferrite coil at index 3. The fabrication lab slides open."


def use_fabricator(game):
    if not game.flags.get("indexed"):
        return "The fabricator idles. Nothing is indexed."
    return game.win("You feed the indexed components to the fabricator. The prototype rises, perfect and new. Sixth Voyage: complete.")


def use_rig(game):
    for item in game.inventory:
        if item.name in INDEX:
            return "The rig hums. The " + item.name + " resonates at index " + str(INDEX[item.name]) + ". Promising."
    return "The rig sits idle. Carry a component to test it."


def talk_to_felix(game):
    if game.flags.get("indexed"):
        return "Felix grins. 'All three indexed. The lab is open north. Build the prototype.'"
    carried = [item.name for item in game.inventory if item.name in INDEX]
    missing = [name for name in INDEX if name not in carried]
    msg = "Felix taps the catalog. "
    if carried:
        msg += "You carry: " + ", ".join(carried) + ". "
    msg += "Missing: " + ", ".join(missing) + ". The vaults hold the rest. Experiment freely."
    return msg


def build():
    game = Game(
        "Sixth Voyage",
        "The foundry is quiet, waiting for a new idea. Three components sleep in the vaults. Felix leans on the catalog. Index everything, then build the prototype.",
    )

    foundry = Room(
        "Foundry Floor",
        "A wide floor of workbenches and quiet machines. Felix, the ship's experimental engineer, leans on the component catalog.",
    )
    vault_west = Room(
        "Component Vault West",
        "Shelves of spare parts. A logic plate and a ferrite coil rest in labeled cradles.",
    )
    vault_east = Room(
        "Component Vault East",
        "A single resonant crystal glows softly on a pedestal.",
    )
    lab = Room(
        "Fabrication Lab",
        "The fabricator dominates the lab, ready to build what the catalog describes.",
    )

    foundry.connect("west", vault_west)
    foundry.connect("east", vault_east)
    foundry.connect("north", lab)
    foundry.block("north", "The fabrication lab is sealed. Index the components first.")
    vault_west.connect("east", foundry)
    vault_east.connect("west", foundry)
    lab.connect("south", foundry)

    plate = Item("logic plate", "A logic plate, etched with fine circuits.")
    vault_west.items.append(plate)

    coil = Item("ferrite coil", "A ferrite coil, wound tight and heavy.")
    vault_west.items.append(coil)

    crystal = Item("resonant crystal", "A resonant crystal, humming a faint note.")
    vault_east.items.append(crystal)

    catalog = Item("catalog", "The component catalog. It indexes what you carry.", takeable=False)
    catalog.on_use = use_catalog
    foundry.items.append(catalog)

    rig = Item("test rig", "An experimental test rig. It never judges a result.", takeable=False)
    rig.on_use = use_rig
    foundry.items.append(rig)

    manual = Item(
        "foundry manual",
        "Foundry manual. Three components, three index numbers. Logic plate is index 1. Resonant crystal is index 2. Ferrite coil is index 3. Index them all at the catalog, then build at the fabricator. Experiment freely. The rig never judges.",
        takeable=False,
    )
    foundry.items.append(manual)

    fabricator = Item("fabricator", "The fabricator. It builds from a complete index.", takeable=False)
    fabricator.on_use = use_fabricator
    lab.items.append(fabricator)

    felix = Character("Felix", "Felix, the ship's experimental engineer, indexer of foundations and builder of new things.")
    felix.on_talk = talk_to_felix
    foundry.characters.append(felix)

    game.add_room(foundry)
    game.add_room(vault_west)
    game.add_room(vault_east)
    game.add_room(lab)
    return game
