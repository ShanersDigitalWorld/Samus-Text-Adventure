from samus.text_adventure.engine import Character, Game, Item, Room

TARGETS = {"alpha": 2, "beta": 3, "gamma": 1}

NAMES = {"alpha": "alpha dial", "beta": "beta dial", "gamma": "gamma dial"}


def use_dial(key):
    def use(game):
        level = game.flags.get(key, 1)
        level = level % 3 + 1
        game.flags[key] = level
        if all(game.flags.get(k, 1) == TARGETS[k] for k in TARGETS):
            if not game.flags.get("yield"):
                game.flags["yield"] = True
                game.rooms["Synthesis Deck"].unblock("north")
                return NAMES[key] + " clicks to " + str(level) + ". The deck hums. Yield optimal. The core chamber slides open."
        return NAMES[key] + " clicks to " + str(level) + "."
    return use


def use_core(game):
    if game.flags.get("yield"):
        return game.win("You engage the synthesis core. Yield peaks and holds. Third Voyage: complete.")
    return "The core sputters. Yield too low to engage."


def talk_to_cyrus(game):
    if game.flags.get("yield"):
        return "Cyrus nods. 'Yield is optimal. The core chamber is open north of the deck.'"
    parts = []
    for key in ("alpha", "beta", "gamma"):
        level = game.flags.get(key, 1)
        target = TARGETS[key]
        if level != target:
            parts.append(NAMES[key].capitalize() + " reads " + str(level) + ". Optimal is " + str(target) + ".")
    if not parts:
        return "Cyrus checks his readouts. 'All conduits optimal.'"
    return "Cyrus checks his readouts. " + " ".join(parts)


def build():
    game = Game(
        "Third Voyage",
        "The synthesis deck drones at low power. The yield core is starving. Calibrate the three conduits and bring the yield back to optimal.",
    )
    game.flags["alpha"] = 1
    game.flags["beta"] = 1
    game.flags["gamma"] = 3

    deck = Room(
        "Synthesis Deck",
        "A wide deck of humming conduits. The alpha dial juts from the master console. Cyrus, the ship's cyberneticist, watches the readouts.",
    )
    coolant = Room(
        "Coolant Exchange",
        "Cold mist curls around pipes. The beta dial is mounted on the coolant regulator.",
    )
    manifold = Room(
        "Plasma Manifold",
        "Heat shimmers off the plasma lines. The gamma dial glows on the manifold housing.",
    )
    core = Room(
        "Yield Core Chamber",
        "The synthesis core towers in the center, dark and waiting.",
    )

    deck.connect("west", coolant)
    deck.connect("east", manifold)
    deck.connect("north", core)
    deck.block("north", "The core chamber is sealed. Yield below optimal.")
    coolant.connect("east", deck)
    manifold.connect("west", deck)
    core.connect("south", deck)

    for key, room in (("alpha", deck), ("beta", coolant), ("gamma", manifold)):
        dial = Item(NAMES[key], "A calibration dial. It clicks through levels 1, 2, 3.", takeable=False)
        dial.on_use = use_dial(key)
        room.items.append(dial)

    manual = Item("deck manual", "Deck manual. Alpha conduit: optimal at level 2. Beta and gamma calibrations are posted in the side galleries.", takeable=False)
    deck.items.append(manual)

    plaque_beta = Item("efficiency plaque", "Efficiency plaque. Beta conduit: resonance peaks at level 3.", takeable=False)
    coolant.items.append(plaque_beta)

    plaque_gamma = Item("resonance plaque", "Resonance plaque. Gamma conduit: idle stability at level 1.", takeable=False)
    manifold.items.append(plaque_gamma)

    synthesis_core = Item("synthesis core", "The synthesis core. It needs optimal yield to engage.", takeable=False)
    synthesis_core.on_use = use_core
    core.items.append(synthesis_core)

    cyrus = Character("Cyrus", "Cyrus, the ship's cyberneticist, tuner of systems and yields.")
    cyrus.on_talk = talk_to_cyrus
    deck.characters.append(cyrus)

    game.add_room(deck)
    game.add_room(coolant)
    game.add_room(manifold)
    game.add_room(core)
    return game
