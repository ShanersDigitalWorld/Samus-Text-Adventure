from samus.text_adventure.engine import Character, Game, Item, Room


TARGETS = {
    "brass": 0,
    "silver": 1,
    "copper": 0,
}


def make_lever(metal):
    def flip(game):
        key = "lever_" + metal
        game.flags[key] = 1 - game.flags.get(key, 0)
        state = game.flags[key]
        lever.description = "A " + metal + " lever set into the vault wall. It rests at " + str(state) + "."
        return "The " + metal + " lever clicks to " + str(state) + "."
    lever = Item(metal + " lever", "A " + metal + " lever set into the vault wall. It rests at 0.", takeable=False)
    lever.on_use = flip
    return lever


def use_core_door(game):
    wrong = [m for m in ("brass", "silver", "copper") if game.flags.get("lever_" + m, 0) != TARGETS[m]]
    if not wrong:
        game.flags["door_open"] = True
        game.rooms["Vault Antechamber"].unblock("north")
        return "The levers hum in agreement. The core door slides open."
    return "The core door stays sealed. The levers are not all true."


def use_binary_core(game):
    return game.win("You lay your hand on the binary core. Bits cascade into perfect order. Program complete. Second Voyage: complete.")


def talk_to_blake(game):
    if game.flags.get("door_open"):
        return "Blake nods. 'The core is open. Clear logic, clean extraction.'"
    wrong = [m for m in ("brass", "silver", "copper") if game.flags.get("lever_" + m, 0) != TARGETS[m]]
    if not wrong:
        return "Blake smiles. 'Every gate holds true. Use the core door.'"
    hints = {
        "brass": "Blake studies the levers. 'Brass is wrong. Brass is AND. AND is true only when both sides are true. What is 1 AND 0?'",
        "silver": "Blake studies the levers. 'Silver is wrong. Silver is OR. OR is true when any side is true. What is 1 OR 0?'",
        "copper": "Blake studies the levers. 'Copper is wrong. Copper is NOT. NOT flips the bit. What is NOT 1?'",
    }
    if wrong[0] in hints:
        return hints[wrong[0]]
    return "Blake folds his hands. 'Three gates, three truths. Brass is AND, silver is OR, copper is NOT. The manual has the statements.'"


def build():
    game = Game(
        "Second Voyage",
        "The Binary Core has sealed itself behind three gates of pure logic. Blake waits in the Vault Antechamber. Restore the truth of the gates and open the core.",
    )

    antechamber = Room(
        "Vault Antechamber",
        "Dust hangs in the still air. Three levers jut from the vault wall: brass, silver, copper. A heavy core door stands to the north. A hologram of a man in a gray uniform waits by the levers.",
    )
    and_gallery = Room(
        "AND Gallery",
        "Shelves of brass tablets line the walls, each etched with truth tables.",
    )
    or_gallery = Room(
        "OR Gallery",
        "Silver tablets glow softly here, covered in branching diagrams.",
    )
    core_room = Room(
        "Binary Core",
        "The Binary Core fills the chamber, a sphere of shifting light.",
    )

    antechamber.connect("east", and_gallery)
    and_gallery.connect("west", antechamber)
    antechamber.connect("west", or_gallery)
    or_gallery.connect("east", antechamber)
    antechamber.connect("north", core_room)
    antechamber.block("north", "The core door is sealed. Set each lever to the truth of its gate, then use the core door.")
    core_room.connect("south", antechamber)

    for metal in ("brass", "silver", "copper"):
        antechamber.items.append(make_lever(metal))

    manual = Item(
        "vault manual",
        "Vault manual. Brass lever: 1 AND 0. Silver lever: 1 OR 0. Copper lever: NOT 1. Set each lever to 1 for true and 0 for false. Then use the core door. NOT flips the bit, so NOT 1 is false.",
    )
    antechamber.items.append(manual)

    door = Item(
        "core door",
        "A heavy door of dark metal. Three small lamps above it mirror the levers.",
        takeable=False,
    )
    door.on_use = use_core_door
    antechamber.items.append(door)

    and_plaque = Item(
        "and plaque",
        "The AND gate. True only when both inputs are true. 1 AND 1 is true. 1 AND 0 is false.",
        takeable=False,
    )
    and_gallery.items.append(and_plaque)

    or_plaque = Item(
        "or plaque",
        "The OR gate. True when any input is true. 1 OR 0 is true. 0 OR 0 is false.",
        takeable=False,
    )
    or_gallery.items.append(or_plaque)

    core = Item(
        "binary core",
        "A sphere of shifting light. Ones and zeroes flow across its surface.",
        takeable=False,
    )
    core.on_use = use_binary_core
    core_room.items.append(core)

    blake = Character("Blake", "Blake, the binary logician, extractor of clean knowledge from noisy data.")
    blake.on_talk = talk_to_blake
    antechamber.characters.append(blake)

    game.add_room(antechamber)
    game.add_room(and_gallery)
    game.add_room(or_gallery)
    game.add_room(core_room)
    return game
