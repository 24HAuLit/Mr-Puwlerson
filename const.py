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
    if file.endswith(".py")
]
COMMANDS_SETUP = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/commands/staff/setup")
    if file.endswith(".py")
]
SETUP_ROLES = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/commands/staff/setup/roles")
    if file.endswith(".py")
]
SETUP_CHANNELS = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/commands/staff/setup/channels")
    if file.endswith(".py")
]
SETUP_TICKETS = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/commands/staff/setup/tickets")
    if file.endswith(".py")
]
PLUGINS = [
    file.replace(".py", "")
    for file in os.listdir(f"{src_path}/src/commands/staff/plugins")
    if file.endswith(".py")
]


plugins_list = ['auto_role', 'suggestion', 'report']

TOKEN = os.getenv("TOKEN_OFFICIAL")

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
