from samus.text_adventure.engine import Character, Game, Item, Room


def use_power_cell(game):
    if game.current.name == "Engineering":
        game.flags["power"] = True
        game.rooms["Engineering"].unblock("north")
        return "You slot the power cell into the relay. The warp core hums back to life and the turbolift doors slide open."
    return "There is nothing to power here."


def use_tricorder(game):
    if game.flags.get("power"):
        return "The tricorder chirps. All systems nominal. The Bridge is ready."
    return "The tricorder chirps. Power failure in the Engineering relays. The Bridge turbolift is offline."


def use_helm(game):
    if game.flags.get("power"):
        return game.win("You take the helm. Stars streak across the viewscreen. Program complete. First Voyage: complete.")
    return "The helm is dead without power."


def talk_to_adam(game):
    if game.flags.get("power"):
        return "Adam smiles. 'Power is restored. The turbolift to the Bridge is waiting north of Engineering.'"
    for item in game.inventory:
        if item.name == "power cell":
            return "Adam nods at the cell. 'Take it east to Engineering and restore the relays.'"
    return "Adam folds his hands. 'The relays in Engineering are dark. You will need a power cell. Check the holodeck storage alcove.'"


def build():
    game = Game(
        "First Voyage",
        "The holodeck doors close behind you and the grid flickers to life. Somewhere a relay has failed. Restore the program and reach the Bridge.",
    )

    holodeck = Room(
        "Holodeck Grid",
        "Yellow grid lines stretch in every direction, flickering at the edges. A storage alcove is set into one wall.",
    )
    corridor = Room(
        "Ship Corridor",
        "A starship corridor. The lights are dim but holding. A hologram of a man in a blue uniform stands by the wall.",
    )
    engineering = Room(
        "Engineering",
        "The warp core sits dark and silent. Dead relay panels line the walls.",
    )
    bridge = Room(
        "Bridge",
        "The viewscreen shows open stars. The helm console blinks, waiting for orders.",
    )

    holodeck.connect("north", corridor)
    corridor.connect("south", holodeck)
    corridor.connect("east", engineering)
    engineering.connect("west", corridor)
    engineering.connect("north", bridge)
    engineering.block("north", "The turbolift has no power. Restore the relays first.")
    bridge.connect("south", engineering)

    cell = Item("power cell", "A compact power cell, humming faintly.")
    cell.on_use = use_power_cell
    holodeck.items.append(cell)

    tricorder = Item("tricorder", "A standard issue tricorder. It chirps when activated.")
    tricorder.on_use = use_tricorder
    corridor.items.append(tricorder)

    helm = Item("helm console", "The helm console. Without power it is just a dark panel.", takeable=False)
    helm.on_use = use_helm
    bridge.items.append(helm)

    adam = Character("Adam", "Adam, the ship's analytical hologram, here to guide lost travelers.")
    adam.on_talk = talk_to_adam
    corridor.characters.append(adam)

    game.add_room(holodeck)
    game.add_room(corridor)
    game.add_room(engineering)
    game.add_room(bridge)
    return game
