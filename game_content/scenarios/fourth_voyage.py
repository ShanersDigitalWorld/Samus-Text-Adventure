from samus.text_adventure.engine import Character, Game, Item, Room

ROUTES = ["dead", "hub", "alpha", "beta", "uplink"]

DISPLAY = {"hub": "Hub", "alpha": "Alpha", "beta": "Beta", "uplink": "Uplink", "dead": "dead end"}


def trace(game):
    nodes = ["hub"]
    seen = {"hub"}
    node = "alpha"
    for _ in range(12):
        nodes.append(node)
        if node == "uplink":
            return nodes, "uplink"
        if node == "dead":
            return nodes, "dead"
        if node in seen:
            return nodes, "loop"
        seen.add(node)
        node = game.flags.get("route_" + node, "dead")
    return nodes, "loop"


def use_relay(key):
    def use(game):
        current = game.flags.get("route_" + key, "dead")
        nxt = ROUTES[(ROUTES.index(current) + 1) % len(ROUTES)]
        game.flags["route_" + key] = nxt
        return DISPLAY[key] + " relay now routes to " + DISPLAY[nxt] + "."
    return use


def use_transmitter(game):
    nodes, end = trace(game)
    shown = " to ".join(DISPLAY[n] for n in nodes)
    game.flags["trace"] = shown
    game.flags["trace_end"] = end
    if end == "uplink":
        game.flags["linked"] = True
        game.rooms["Network Hub"].unblock("north")
        return "Trace: " + shown + ". Signal locked. The uplink is open north of the hub."
    if end == "dead":
        return "Trace: " + shown + ". Signal lost in dead air."
    return "Trace: " + shown + ". Signal looping. The network is chasing its own tail."


def use_uplink_core(game):
    return game.win("You jack into the uplink core. The network sings at full throughput. Fourth Voyage: complete.")


def talk_to_dante(game):
    if game.flags.get("linked"):
        return "Dante grins. 'Full throughput. The uplink is open north of the hub.'"
    shown = game.flags.get("trace")
    if not shown:
        return "Dante folds his arms. 'Run the transmitter. I will read the trace and tell you where the signal dies.'"
    end = game.flags.get("trace_end")
    if end == "dead":
        return "Dante studies the trace. 'Last trace: " + shown + ". The signal dies in dead air. Reroute the relay that feeds it.'"
    return "Dante studies the trace. 'Last trace: " + shown + ". It loops back on itself. Break the cycle.'"


def build():
    game = Game(
        "Fourth Voyage",
        "The relay network is chaos. Signals die in dead air and chase their own tails. Dante waits in the Network Hub. Trace the routes, adapt, and open the uplink.",
    )

    hub = Room(
        "Network Hub",
        "Cable runs converge on a central transmitter. Dante, the ship's network runner, watches the trace display.",
    )
    relay_alpha = Room(
        "Relay Alpha",
        "The Alpha relay hums against the west wall, its route dial spinning slowly.",
    )
    relay_beta = Room(
        "Relay Beta",
        "The Beta relay blinks against the east wall, its route dial spinning slowly.",
    )
    uplink = Room(
        "Core Uplink",
        "The uplink core towers here, dark until the network locks.",
    )

    hub.connect("west", relay_alpha)
    hub.connect("east", relay_beta)
    hub.connect("north", uplink)
    hub.block("north", "The uplink is dark. The network has no clean route.")
    relay_alpha.connect("east", hub)
    relay_beta.connect("west", hub)
    uplink.connect("south", hub)

    transmitter = Item("transmitter", "The hub transmitter. It always sends to Relay Alpha first.", takeable=False)
    transmitter.on_use = use_transmitter
    hub.items.append(transmitter)

    manual = Item(
        "network manual",
        "Network manual. The transmitter always sends to Relay Alpha first. Using a relay cycles its route: dead air, Hub, Alpha, Beta, Uplink, then dead air again. Target path: Hub to Alpha to Beta to Uplink. Dante reads every trace.",
        takeable=False,
    )
    hub.items.append(manual)

    alpha = Item("alpha relay", "The Alpha relay. Its route dial shows where it sends the signal.", takeable=False)
    alpha.on_use = use_relay("alpha")
    relay_alpha.items.append(alpha)

    beta = Item("beta relay", "The Beta relay. Its route dial shows where it sends the signal.", takeable=False)
    beta.on_use = use_relay("beta")
    relay_beta.items.append(beta)

    core = Item("uplink core", "The uplink core. It needs a locked signal to engage.", takeable=False)
    core.on_use = use_uplink_core
    uplink.items.append(core)

    dante = Character("Dante", "Dante, the ship's network runner, reader of traces and router of chaos.")
    dante.on_talk = talk_to_dante
    hub.characters.append(dante)

    game.add_room(hub)
    game.add_room(relay_alpha)
    game.add_room(relay_beta)
    game.add_room(uplink)
    return game
