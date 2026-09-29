import os
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
LISTENERS_ROOT = PACKAGE_ROOT / "listeners"
COMMANDS_ROOT = PACKAGE_ROOT / "commands"

def _extensions(directory: Path, *, exclude: frozenset[str] = frozenset()) -> list[str]:
    """Module names for loadable discord.py extensions in a directory."""
    return sorted(
        path.stem for path in directory.glob("*.py")
        if not path.stem.startswith("_") and path.stem not in exclude
    )


# These inventories are module names loaded by bot.setup_hook.
# on_guild_join is loaded by the on_ready extension, not as a top-level listener.
LISTENERS = _extensions(LISTENERS_ROOT, exclude=frozenset({"on_guild_join"}))
LISTENERS_LOGS = _extensions(LISTENERS_ROOT / "logs")
LISTENERS_REPORT = _extensions(LISTENERS_ROOT / "report")
LISTENERS_SUGGEST = _extensions(LISTENERS_ROOT / "suggestion")
LISTENERS_TICKET = _extensions(LISTENERS_ROOT / "ticket")

COMMANDS = _extensions(COMMANDS_ROOT)
COMMANDS_TICKET = _extensions(COMMANDS_ROOT / "ticket", exclude=frozenset({"tickets"}))
COMMANDS_STAFF = _extensions(COMMANDS_ROOT / "staff")
COMMANDS_MOD = _extensions(COMMANDS_ROOT / "staff" / "mod")
COMMANDS_ADMIN = _extensions(COMMANDS_ROOT / "staff" / "admin")
COMMANDS_SETUP = _extensions(COMMANDS_ROOT / "staff" / "setup")
SETUP_ROLES = _extensions(COMMANDS_ROOT / "staff" / "setup" / "roles")
SETUP_CHANNELS = _extensions(COMMANDS_ROOT / "staff" / "setup" / "channels")
SETUP_TICKETS = _extensions(COMMANDS_ROOT / "staff" / "setup" / "tickets")
PLUGINS = _extensions(COMMANDS_ROOT / "staff" / "plugins")
UPDATE_DB = _extensions(LISTENERS_ROOT / "update_db")

commands_list = [
    "ping", "pileface", "suggest", "mod clear", "mod timeout", "mod untimemout", "nuke",
    "blacklist", "unblacklist", "giveaway", "setup server", "setup roles", "setup channels",
    "setup tickets", "setup max_ticket", "locale", "update", "add", "remove", "rename", "close",
    "close_reason"
]

TOKEN = os.getenv("TOKEN_OFFICIAL")

DATA = {
    "main": {
        "suggestion": 1011704888679477369,
        "suggest_result": 1011705768002727987
    }
}
