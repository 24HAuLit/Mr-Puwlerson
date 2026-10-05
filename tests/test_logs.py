"""Offline regression tests for message logs and the clear command."""

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, Mock, create_autospec, patch

import discord

from mr_puwlerson.commands.staff.mod.mod import Mod
from mr_puwlerson.database import initialize_database
from mr_puwlerson.listeners.logs.message import Message


class MessageLogChannelTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.guild_id = 123456789
        self.path = initialize_database(self.guild_id, Path(temp.name) / "Database")
        path_patch = patch.dict(Message.log_channel.__globals__,
                                {"database_path": lambda guild_id: self.path})
        path_patch.start()
        self.addCleanup(path_patch.stop)
        self.bot = Mock()
        self.cog = Message(self.bot)
        self.channel = SimpleNamespace(id=10, category_id=None)
        self.message = SimpleNamespace(guild=SimpleNamespace(id=self.guild_id), channel=self.channel)

    def test_null_ticket_parent_and_untracked_channel_are_allowed(self):
        with closing(sqlite3.connect(self.path)) as conn:
            self.assertIsNone(conn.execute("SELECT ticket_parent FROM config").fetchone()[0])
            self.assertIsNone(conn.execute("SELECT 1 FROM channels WHERE id = 10").fetchone())
            conn.execute("INSERT INTO logs_channels (name, id) VALUES ('new', 20)")
            conn.commit()
        destination = object()
        self.bot.get_channel.return_value = destination

        self.assertIs(self.cog.log_channel(self.message, "new"), destination)
        self.bot.get_channel.assert_called_once_with(20)

    def test_hidden_channel_is_skipped(self):
        self.channel.category_id = 99
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("INSERT INTO channels (name, id, hidden) VALUES ('private', 10, 1)")
            conn.execute("INSERT INTO logs_channels (name, id) VALUES ('new', 20)")

        self.assertIsNone(self.cog.log_channel(self.message, "new"))
        self.bot.get_channel.assert_not_called()

    def test_ticket_category_is_skipped(self):
        self.channel.category_id = 42
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("UPDATE config SET ticket_parent = 42")
            conn.execute("INSERT INTO logs_channels (name, id) VALUES ('new', 20)")

        self.assertIsNone(self.cog.log_channel(self.message, "new"))
        self.bot.get_channel.assert_not_called()

    def test_configured_new_log_channel_uses_bot_cache(self):
        self.channel.category_id = 99
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("INSERT INTO channels (name, id, hidden) VALUES ('general', 10, 0)")
            conn.execute("INSERT INTO logs_channels (name, id) VALUES ('new', 20)")
        destination = object()
        self.bot.get_channel.return_value = destination

        self.assertIs(self.cog.log_channel(self.message, "new"), destination)
        self.bot.get_channel.assert_called_once_with(20)


class ClearLogConfigurationTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_clear_mapping_sends_ephemeral_error_without_purging(self):
        with tempfile.TemporaryDirectory() as temp:
            guild_id = 123456789
            path = initialize_database(guild_id, Path(temp) / "Database")
            with closing(sqlite3.connect(path)) as conn:
                self.assertIsNone(conn.execute(
                    "SELECT id FROM logs_channels WHERE name = 'clear'").fetchone())

            channel = create_autospec(discord.TextChannel, instance=True)
            channel.id = 10
            channel.name = "general"
            channel.purge.side_effect = AssertionError("clear must not purge without a log mapping")
            interaction = SimpleNamespace(
                guild=SimpleNamespace(id=guild_id, name="Test guild"),
                channel=channel,
                response=SimpleNamespace(send_message=AsyncMock(), defer=AsyncMock()),
                followup=SimpleNamespace(send=AsyncMock()),
            )
            bot = Mock()
            bot.fetch_channel = AsyncMock()
            # App-command callbacks may be cloned when the Cog is constructed.
            # Patch the callback's own globals before constructing the Cog.
            callback = cast(Any, Mod.clear.callback)
            with patch.dict(callback.__globals__, {
                "database_path": lambda guild_id: path,
                "database_ready": AsyncMock(return_value=True),
                "has_permission": AsyncMock(return_value=True),
            }):
                cog = Mod(bot)
                await callback(cog, interaction, number=5)

            interaction.response.send_message.assert_awaited_once()
            args, kwargs = interaction.response.send_message.await_args
            self.assertTrue(kwargs.get("ephemeral"))
            self.assertRegex(str(args[0]).lower(), r"config")
            channel.purge.assert_not_awaited()
            bot.get_channel.assert_not_called()
            bot.fetch_channel.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
