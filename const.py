import os
import pathlib

src_path = pathlib.Path(__file__).parent.absolute().as_posix()

# Partie Listeners
LISTENERS = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/listeners")
    if file.endswith(".py")
]
LISTENERS_LOGS = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/listeners/logs")
    if file.endswith(".py")
]
LISTENERS_REPORT = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/listeners/report")
    if file.endswith(".py")
]
LISTENERS_SUGGEST = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/listeners/suggestion")
    if file.endswith(".py")
]
LISTENERS_TICKET = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/listeners/ticket")
    if file.endswith(".py")
]

# Partie commandes
COMMANDS = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/commands")
    if file.endswith(".py")
]
COMMANDS_TICKET = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/commands/ticket")
    if file.endswith(".py")
]
COMMANDS_STAFF = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/commands/staff")
    if file.endswith(".py") and not file.endswith("setup.py")
]


TOKEN = os.getenv("TOKEN_OFFICIAL")

DATA = {
    "main": {
        "guild": 419529681885331456,
        "suggestion": 1011704888679477369,
        "suggest_result": 1011705768002727987,
        "bda_waiting": 1046381499143950356,
        "ticket": 1027647411495129109
    },
    "logs": {
        "guild": 1025129313546285056,
        "messages": {
            "new": 1025130771456983080,
            "edit": 1025703859689103392,
            "delete": 1025703875061219358
        },
        "moderation": {
            "clear": 1025703890513035284,
            "timeout": 1025705989745422377,
            "blacklist": 1065714693500579950,
            "ban": 1025706023333408878,
            "nuke": 1025705944266588160
        },
        "ticket": {
            "create": 1030764531720392734,
            "close": 1030764601295519845
        },
        "global": {
            "join": 1039280742993240125,
            "leave": 1039280760403787829,
            "report": 1065713793667174470,
        }
    },
    "roles": {
        "Default": 419556483861053448,
        "Staff": 1018602650566139984,
        "Moderator": 419532481319010314,
        "Admin": 419532345134284810,
        "Owner": 419532166888816640
    }
}
