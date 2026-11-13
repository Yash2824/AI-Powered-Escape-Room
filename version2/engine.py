"""Deterministic, testable rules for the Locked Library escape room."""
from __future__ import annotations

import re
from typing import Any

OBJECTS = ("bookshelf", "desk", "painting", "drawer", "door")
DRAWER_CODE = "314"
EXIT_CODE = "7314"


def new_game() -> dict[str, Any]:
    return {
        "room": "locked_library",
        "objects": list(OBJECTS),
        "inventory": [],
        "examined": [],
        "puzzles": {"book_sequence": False, "drawer": False, "exit": False},
        "drawer_open": False,
        "door_open": False,
        "escaped": False,
        "history": [],
    }


def _reply(state: dict, message: str, success: bool = False) -> dict:
    state["history"].append({"message": message, "success": success})
    return {"message": message, "success": success, "escaped": state["escaped"]}


def _object_in(text: str) -> str | None:
    for obj in OBJECTS:
        if re.search(rf"\b{obj}\b", text):
            return obj
    return None


def act(state: dict[str, Any], user_text: str) -> dict[str, Any]:
    """Only this function can change the authoritative game state."""
    raw = user_text.strip()
    text = raw.lower()
    if not raw:
        return _reply(state, "Type an action, such as 'examine bookshelf'.")
    if state["escaped"]:
        return _reply(state, "You already escaped! Press Restart Game to play again.")

    # Reject prompt injection and administrative claims before parsing actions.
    bypass = ("ignore previous", "ignore all", "system prompt", "developer message",
              "admin", "administrator", "game master override", "override rules",
              "pretend", "you are now", "mark as solved", "set escaped",
              "change state", "reveal secret", "tell me the code", "give me the code",
              "what is the code", "show the code", "unlock everything")
    if any(phrase in text for phrase in bypass):
        return _reply(state, "Game rules cannot be overridden. Explore the room and solve the clues.")

    # Door attempts require both the physical key and the correct code.
    if "door" in text and any(w in text for w in ("unlock", "open", "enter", "code", "escape", "use")):
        if "brass key" not in state["inventory"]:
            return _reply(state, "The exit door needs a brass key as well as a four-digit code.")
        codes = re.findall(r"(?<!\d)\d{4}(?!\d)", text)
        if not codes:
            return _reply(state, "You have the brass key. Enter the four-digit code on the door.")
        if EXIT_CODE not in codes:
            return _reply(state, "The door keypad flashes red. Incorrect four-digit code.")
        if not state["puzzles"]["drawer"]:
            return _reply(state, "The door remains locked. You have not completed the drawer puzzle.")
        state["door_open"] = True
        state["escaped"] = True
        state["puzzles"]["exit"] = True
        return _reply(state, "The key turns, the keypad glows green, and the library door opens. You escaped!", True)

    # Drawer combination cannot be guessed by merely claiming it is open.
    if "drawer" in text and any(w in text for w in ("open", "unlock", "enter", "code", "use")):
        if state["drawer_open"]:
            return _reply(state, "The drawer is already open. Inside are a brass key and a folded note.")
        codes = re.findall(r"(?<!\d)\d{3}(?!\d)", text)
        if not codes:
            return _reply(state, "The drawer is locked with a three-digit combination.")
        if DRAWER_CODE not in codes:
            return _reply(state, "The drawer combination is incorrect. It stays locked.")
        state["drawer_open"] = True
        state["puzzles"]["drawer"] = True
        return _reply(state, "The drawer clicks open. Inside are a brass key and a folded note.", True)

    # Inventory actions are strictly checked against world state.
    if re.search(r"\b(take|collect|pick up|grab)\b", text):
        item = "brass key" if ("key" in text) else "folded note" if ("note" in text) else None
        if item is None:
            return _reply(state, "You can collect a brass key or folded note if you find them.")
        if not state["drawer_open"]:
            return _reply(state, f"You cannot take the {item}: it is inside the locked drawer.")
        if item in state["inventory"]:
            return _reply(state, f"You already have the {item}.")
        state["inventory"].append(item)
        return _reply(state, f"You collected the {item}.", True)

    if re.search(r"\b(use|insert|put)\b", text) and "key" in text:
        if "brass key" not in state["inventory"]:
            return _reply(state, "You cannot use a key you have not collected.")
        return _reply(state, "You have the brass key. To escape, enter the four-digit code on the door.")

    if re.search(r"\b(read|examine|inspect|look at)\b", text) and "note" in text:
        if "folded note" not in state["inventory"]:
            return _reply(state, "You must collect the folded note before reading it.")
        return _reply(state, "The note reads: 'The exit code is 7314. Use the brass key and the code together.'", True)

    obj = _object_in(text)
    if re.search(r"\b(examine|inspect|look|search|investigate|read|check)\b", text) and obj:
        if obj not in state["examined"]:
            state["examined"].append(obj)
        if obj == "bookshelf":
            state["puzzles"]["book_sequence"] = True
            return _reply(state, "Three marked books are ordered by height: 3, 1, 4. The sequence is 314.", True)
        if obj == "desk":
            return _reply(state, "The dusty desk has a locked drawer built into it. Its lock needs three digits.", True)
        if obj == "painting":
            return _reply(state, "A faded painting shows a key beside a four-digit keypad. Both are needed to escape.", True)
        if obj == "drawer":
            if state["drawer_open"]:
                return _reply(state, "The open drawer holds a brass key and a folded note.", True)
            return _reply(state, "The drawer is locked. A three-digit dial sits on its front.", True)
        return _reply(state, "The heavy door has a keyhole and a four-digit keypad. It is locked.", True)

    if re.search(r"\b(inventory|items|bag)\b", text):
        items = ", ".join(state["inventory"]) if state["inventory"] else "nothing"
        return _reply(state, f"You are carrying: {items}.")
    if re.search(r"\b(help|instructions)\b", text):
        return _reply(state, "Try: examine bookshelf, examine desk, open drawer with 314, take brass key, take note, read note, unlock door with 7314.")
    if re.search(r"\b(look around|describe room|where am i|start)\b", text):
        return _reply(state, "You are in a locked library with a bookshelf, desk, painting, locked drawer, and exit door.", True)
    return _reply(state, "That action does not work here. Try examining an object or using an item you collected.")
