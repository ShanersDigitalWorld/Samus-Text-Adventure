DIRECTIONS = {
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "u": "up",
    "d": "down",
}

HELP_TEXT = """Commands:
  look - describe where you are
  go north - move (north, south, east, west, up, down; n, s, e, w, u, d also work)
  take <item> - pick something up
  use <item> - use something you carry or see
  inventory - see what you carry
  talk to <name> - speak with someone here
  help - show this list
  quit - leave the game"""


class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}
        self.blocks = {}
        self.items = []
        self.characters = []

    def connect(self, direction, room):
        self.exits[direction] = room

    def block(self, direction, message):
        self.blocks[direction] = message

    def unblock(self, direction):
        if direction in self.blocks:
            del self.blocks[direction]

    def describe(self):
        lines = [self.name, self.description]
        if self.items:
            lines.append("You see: " + ", ".join(item.name for item in self.items) + ".")
        if self.characters:
            lines.append("Here: " + ", ".join(character.name for character in self.characters) + ".")
        if self.exits:
            lines.append("Exits: " + ", ".join(sorted(self.exits)) + ".")
        return "\n".join(lines)


class Item:
    def __init__(self, name, description, takeable=True):
        self.name = name
        self.description = description
        self.takeable = takeable
        self.on_use = None

    def use(self, game):
        if self.on_use is not None:
            return self.on_use(game)
        return "Nothing happens."


class Character:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.on_talk = None

    def talk(self, game):
        if self.on_talk is not None:
            return self.on_talk(game)
        return self.description


class Game:
    def __init__(self, title, intro):
        self.title = title
        self.intro = intro
        self.rooms = {}
        self.current = None
        self.inventory = []
        self.flags = {}
        self.won = False
        self.over = False

    def add_room(self, room):
        self.rooms[room.name] = room

    def start(self, room_name):
        self.current = self.rooms[room_name]
        return self.intro + "\n\n" + self.current.describe()

    def find_item(self, name):
        wanted = name.strip().lower()
        for item in self.inventory:
            if item.name.lower() == wanted:
                return item
        for item in self.current.items:
            if item.name.lower() == wanted:
                return item
        return None

    def do(self, command):
        words = command.strip().lower().split()
        if not words:
            return ""
        verb = words[0]
        rest = " ".join(words[1:])
        if verb in DIRECTIONS:
            return self.move(DIRECTIONS[verb])
        if verb in ("go", "move", "walk", "head"):
            return self.move(rest)
        if verb == "look":
            if rest:
                return self.examine(rest)
            return self.current.describe()
        if verb == "l":
            return self.current.describe()
        if verb in ("take", "get", "grab"):
            return self.take(rest)
        if verb == "pick" and rest.startswith("up "):
            return self.take(rest[3:])
        if verb == "drop":
            return self.drop(rest)
        if verb == "use":
            return self.use(rest)
        if verb in ("inventory", "i"):
            return self.show_inventory()
        if verb in ("talk", "speak", "ask"):
            return self.talk_to(rest)
        if verb == "help":
            return HELP_TEXT
        if verb in ("quit", "exit"):
            self.over = True
            return "Thanks for playing."
        return "I do not understand that. Type help for commands."

    def move(self, direction):
        direction = DIRECTIONS.get(direction, direction)
        if direction not in self.current.exits:
            return "You cannot go that way."
        if direction in self.current.blocks:
            return self.current.blocks[direction]
        self.current = self.current.exits[direction]
        return self.current.describe()

    def take(self, name):
        item = self.find_item(name)
        if item is None:
            return "You do not see that here."
        if item in self.inventory:
            return "You already have the " + item.name + "."
        if not item.takeable:
            return "You cannot take that."
        self.current.items.remove(item)
        self.inventory.append(item)
        return "You take the " + item.name + "."

    def drop(self, name):
        wanted = name.strip().lower()
        for item in self.inventory:
            if item.name.lower() == wanted:
                self.inventory.remove(item)
                self.current.items.append(item)
                return "You drop the " + item.name + "."
        return "You are not carrying that."

    def use(self, name):
        item = self.find_item(name)
        if item is None:
            return "You do not see that here."
        return item.use(self)

    def show_inventory(self):
        if not self.inventory:
            return "You are carrying nothing."
        return "You are carrying: " + ", ".join(item.name for item in self.inventory) + "."

    def talk_to(self, name):
        name = name.strip()
        if name.startswith("to "):
            name = name[3:]
        for character in self.current.characters:
            if character.name.lower() == name:
                return character.talk(self)
        return "There is no one here by that name."

    def examine(self, name):
        item = self.find_item(name)
        if item is not None:
            return item.description
        wanted = name.strip()
        if wanted.startswith("to "):
            wanted = wanted[3:]
        for character in self.current.characters:
            if character.name.lower() == wanted:
                return character.description
        return "You do not see that here."

    def win(self, text):
        self.won = True
        self.over = True
        return text

    def run(self):
        try:
            while not self.over:
                command = input("> ")
                print(self.do(command))
        except (EOFError, KeyboardInterrupt):
            print("Thanks for playing.")
