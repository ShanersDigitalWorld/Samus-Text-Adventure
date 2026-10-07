from samus.text_adventure.engine import Character, Game, Item, Room

PROCESSES = {
    "alpha scanner": {"key": "alpha", "cost": 4, "critical": True},
    "beta scanner": {"key": "beta", "cost": 4, "critical": False},
    "gamma archive": {"key": "gamma", "cost": 3, "critical": True},
    "delta archive": {"key": "delta", "cost": 3, "critical": False},
    "epsilon beacon": {"key": "epsilon", "cost": 2, "critical": True},
}

THRESHOLD = 9


def load(game):
    total = 0
    for spec in PROCESSES.values():
        if game.flags.get("run_" + spec["key"], True):
            total += spec["cost"]
    return total


def fault(game):
    for spec in PROCESSES.values():
        if spec["critical"] and not game.flags.get("run_" + spec["key"], True):
            return True
    return False


def check_streamline(game):
    if game.flags.get("streamlined"):
        return None
    if fault(game):
        return None
    if load(game) <= THRESHOLD:
        game.flags["streamlined"] = True
        game.rooms["Control Deck"].unblock("north")
        return " Load at " + str(load(game)) + ". Optimal. The core chamber slides open."
    return None


def use_process(name):
    def use(game):
        spec = PROCESSES[name]
        key = "run_" + spec["key"]
        running = game.flags.get(key, True)
        game.flags[key] = not running
        if not running:
            msg = "You restart the " + name + "."
        elif spec["critical"]:
            msg = "You shut down the " + name + ". The deck shudders. Fault. That process is critical."
        else:
            msg = "You shut down the " + name + ". Redundant load shed."
        opened = check_streamline(game)
        if opened:
            msg += opened
        return msg
    return use


def use_panel(game):
    msg = "Status panel. Load: " + str(load(game)) + ". Threshold: " + str(THRESHOLD) + " or below."
    if fault(game):
        msg += " Fault: a critical process is offline."
    else:
        msg += " No faults."
    return msg


def use_core(game):
    return game.win("You engage the optimization core. The system hums at peak efficiency. Fifth Voyage: complete.")


def talk_to_elias(game):
    if game.flags.get("streamlined"):
        return "Elias nods. 'Load optimal. The core is open north of the deck.'"
    parts = []
    if fault(game):
        off = [name for name, spec in PROCESSES.items() if spec["critical"] and not game.flags.get("run_" + spec["key"], True)]
        parts.append("Fault: " + ", ".join(off) + " is critical and offline. Restart it.")
    dupes = [name for name, spec in PROCESSES.items() if not spec["critical"] and game.flags.get("run_" + spec["key"], True)]
    if dupes:
        parts.append("Redundant and still running: " + ", ".join(dupes) + ".")
    parts.append("Load at " + str(load(game)) + ". Target " + str(THRESHOLD) + " or below.")
    return "Elias checks his readouts. " + " ".join(parts)


def build():
    game = Game(
        "Fifth Voyage",
        "The system is bloated and slow. Five processes grind where three would do. Elias waits on the Control Deck. Streamline the system and open the optimization core.",
    )

    deck = Room(
        "Control Deck",
        "Status lights blink across the master console. Elias, the ship's efficiency analyst, studies the load readouts.",
    )
    bay_west = Room(
        "Process Bay West",
        "Two scanner rigs thrum side by side, doing the same job twice.",
    )
    bay_east = Room(
        "Process Bay East",
        "The gamma archive spins in its cradle, cataloging everything twice over.",
    )
    core = Room(
        "Optimization Core",
        "The optimization core waits in the center, dark until the system is lean.",
    )

    deck.connect("west", bay_west)
    deck.connect("east", bay_east)
    deck.connect("north", core)
    deck.block("north", "The core chamber is sealed. Streamline the system first.")
    bay_west.connect("east", deck)
    bay_east.connect("west", deck)
    core.connect("south", deck)

    home = {
        "alpha scanner": deck,
        "beta scanner": bay_west,
        "gamma archive": bay_east,
        "delta archive": bay_west,
        "epsilon beacon": deck,
    }
    for name, room in home.items():
        proc = Item(name, "A running system process. Use it to shut it down or restart it.", takeable=False)
        proc.on_use = use_process(name)
        room.items.append(proc)

    panel = Item("status panel", "The master status panel. It reports system load.", takeable=False)
    panel.on_use = use_panel
    deck.items.append(panel)

    manual = Item(
        "operations manual",
        "Operations manual. Five processes, one bloated system. The beta scanner duplicates the alpha scanner. The delta archive duplicates the gamma archive. Redundancy is waste. Critical processes must never stop. Target load: 9 or below.",
        takeable=False,
    )
    deck.items.append(manual)

    opt_core = Item("optimization core", "The optimization core. It needs a lean system to engage.", takeable=False)
    opt_core.on_use = use_core
    core.items.append(opt_core)

    elias = Character("Elias", "Elias, the ship's efficiency analyst, pruner of waste and watcher of loads.")
    elias.on_talk = talk_to_elias
    deck.characters.append(elias)

    game.add_room(deck)
    game.add_room(bay_west)
    game.add_room(bay_east)
    game.add_room(core)
    return game
