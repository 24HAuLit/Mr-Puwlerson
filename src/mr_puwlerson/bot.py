import os
import ssl
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

from mr_puwlerson.utils.const import (
    COMMANDS,
    COMMANDS_ADMIN,
    COMMANDS_MOD,
    COMMANDS_SETUP,
    COMMANDS_STAFF,
    COMMANDS_TICKET,
    LISTENERS,
    LISTENERS_LOGS,
    LISTENERS_REPORT,
    LISTENERS_SUGGEST,
    LISTENERS_TICKET,
    PLUGINS,
    SETUP_CHANNELS,
    SETUP_ROLES,
    SETUP_TICKETS,
    TOKEN,
    UPDATE_DB,
)


class Main(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=discord.Intents.all(),
            status=discord.Status.dnd,
            activity=discord.Game("sa réparation"),
        )
        self.owner_ids = {700685199662514186}

    async def setup_hook(self) -> None:
        sections = (
            ("commands", COMMANDS),
            ("commands.ticket", ["tickets", *COMMANDS_TICKET]),
            ("commands.staff", COMMANDS_STAFF),
            ("commands.staff.mod", COMMANDS_MOD),
            ("commands.staff.admin", COMMANDS_ADMIN),
            ("commands.staff.plugins", PLUGINS),
            ("commands.staff.setup", COMMANDS_SETUP),
            ("commands.staff.setup.roles", SETUP_ROLES),
            ("commands.staff.setup.channels", SETUP_CHANNELS),
            ("commands.staff.setup.tickets", SETUP_TICKETS),
            ("listeners", LISTENERS),
            ("listeners.logs", LISTENERS_LOGS),
            ("listeners.report", LISTENERS_REPORT),
            # The suggestion cog owns these button callbacks; loading the old
            # listener handlers as well would acknowledge the same interaction twice.
            ("listeners.suggestion", [name for name in LISTENERS_SUGGEST
                                       if name not in {"accepted_suggest", "denied_suggest"}]),
            ("listeners.ticket", LISTENERS_TICKET),
            ("listeners.update_db", UPDATE_DB),
            ("listeners.bda", ["besoin_aide"]),
        )
        for section, names in sections:
            for name in names:
                await self.load_extension(f"mr_puwlerson.{section}.{name}")
        await self.tree.sync()


def configure_ca_bundle() -> None:
    """Use the system CA bundle when Python's default OpenSSL path is empty."""
    if os.environ.get("SSL_CERT_FILE") or os.environ.get("SSL_CERT_DIR"):
        return
    if ssl.get_default_verify_paths().cafile is not None:
        return
    bundle = Path("/etc/ssl/certs/ca-certificates.crt")
    if bundle.is_file():
        os.environ["SSL_CERT_FILE"] = str(bundle)


def main() -> None:
    if TOKEN is None:
        raise RuntimeError("TOKEN_OFFICIAL is not set")
    configure_ca_bundle()
    Main().run(TOKEN)
