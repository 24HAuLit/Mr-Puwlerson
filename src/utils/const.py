import os
import pathlib

src_path = pathlib.Path(__file__).parent.absolute().as_posix()

# Partie Listeners
LISTENERS = [
    file.replace(".py", "")
    for file in os.listdir("./src/listeners")
    if file.endswith(".py") and file != "on_guild_join.py"
]
LISTENERS_LOGS = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/listeners/logs")
    if file.endswith(".py")
]
LISTENERS_REPORT = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/listeners/report")
    if file.endswith(".py")
]
LISTENERS_SUGGEST = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/listeners/suggestion")
    if file.endswith(".py")
]
LISTENERS_TICKET = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/listeners/ticket")
    if file.endswith(".py")
]

# Partie commandes
COMMANDS = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands")
    if file.endswith(".py")
]
COMMANDS_TICKET = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands/ticket")
    if file.endswith(".py") and file != "tickets.py"
]
COMMANDS_STAFF = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands/staff")
    if file.endswith(".py")
]
COMMANDS_MOD = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands/staff/mod")
    if file.endswith(".py")
]

COMMANDS_ADMIN = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands/staff/admin")
    if file.endswith(".py")
]
COMMANDS_SETUP = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands/staff/setup")
    if file.endswith(".py")
]
SETUP_ROLES = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands/staff/setup/roles")
    if file.endswith(".py")
]
SETUP_CHANNELS = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands/staff/setup/channels")
    if file.endswith(".py")
]
SETUP_TICKETS = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands/staff/setup/tickets")
    if file.endswith(".py")
]
PLUGINS = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/commands/staff/plugins")
    if file.endswith(".py")
]
UPDATE_DB = [
    file.replace(".py", "")
    for file in os.listdir(f"./src/listeners/update_db")
    if file.endswith(".py")
]

plugins_list = ['auto_role', 'suggestion', 'report', 'verif', 'giveaway']
commands_list = [
    "ping", "pileface", "suggest", "mod clear", "mod timeout", "mod untimemout", "nuke",
    "blacklist", "unblacklist", "giveaway", "setup server", "setup roles", "setup channels",
    "setup tickets", "setup max_ticket", "locale", "update", "add", "remove", "rename", "close",
    "close_reason"
]

TOKEN = os.getenv("TOKEN_OFFICIAL")
SENTRY_TOKEN = os.getenv("SENTRY_TOKEN")

TICKET_MAXIMUM = 3
DATA = {
    "main": {
        "suggestion": 1011704888679477369,
        "suggest_result": 1011705768002727987,
        "giveaway": 1071516154109120602,
        "bda_waiting": 1046381499143950356,
        "ticket": 1027647411495129109
    }
}
