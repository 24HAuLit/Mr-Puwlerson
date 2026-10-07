"""Offline tests for the setup commands that persist guild configuration."""

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, Mock, create_autospec, patch

import discord

from mr_puwlerson.commands.staff.setup._shared import (
    handle_role_selection,
    require_owner,
)
from mr_puwlerson.commands.staff.setup.setup import Setup
from mr_puwlerson.commands.staff.setup.tickets.ticket_category import TicketCategory
from mr_puwlerson.database import initialize_database


class SetupWorkflowTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.guild_id = 123456789
        self.path = initialize_database(self.guild_id, Path(self.temp.name) / "Database")
        self.guild = SimpleNamespace(id=self.guild_id, owner_id=42)
        self.interaction = SimpleNamespace(
            guild=self.guild, user=SimpleNamespace(id=42, roles=[]),
            type=discord.InteractionType.component,
            response=SimpleNamespace(send_message=AsyncMock()),
            followup=SimpleNamespace(send=AsyncMock()),
        )
        path = lambda guild_id: self.path
        owner_patch = patch.dict(require_owner.__globals__, {"database_path": path})
        owner_patch.start()
        self.addCleanup(owner_patch.stop)

    def config(self, column):
        with closing(sqlite3.connect(self.path)) as conn:
            return conn.execute(f"SELECT {column} FROM config").fetchone()[0]

    async def test_max_ticket_updates_config_without_changing_ticket_counts(self):
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("INSERT INTO ticket_count (user_id, count) VALUES (7, 2)")
        callback = cast(Any, Setup.max_ticket.callback)
        with patch.dict(callback.__globals__, {"database_path": lambda guild_id: self.path}):
            cog = Setup(Mock())
            await callback(cog, self.interaction, 5)
            self.assertEqual(self.config("ticket_limit"), 5)
            with closing(sqlite3.connect(self.path)) as conn:
                self.assertEqual(conn.execute("SELECT count FROM ticket_count WHERE user_id = 7").fetchone(), (2,))
            await callback(cog, self.interaction, 0)
            self.assertEqual(self.config("ticket_limit"), 5)
        self.assertEqual(self.interaction.response.send_message.await_count, 2)

    async def test_hidden_channels_lists_only_existing_hidden_channels(self):
        self.guild.get_channel = lambda channel_id: SimpleNamespace(id=channel_id) if channel_id in (10, 20) else None
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.executemany(
                "INSERT INTO channels (name, id, hidden) VALUES (?, ?, ?)",
                [("visible", 10, 0), ("hidden", 20, 1), ("deleted", 30, 1)],
            )
        callback = cast(Any, Setup.hidden_channels.callback)
        with patch.dict(callback.__globals__, {"database_path": lambda guild_id: self.path}):
            await callback(Setup(Mock()), self.interaction)
        self.interaction.response.send_message.assert_awaited_once_with(
            "Salons exclus des logs :\n• <#20>", ephemeral=True,
        )
        self.interaction.followup.send.assert_not_awaited()

    async def test_hidden_channels_empty_and_owner_only(self):
        self.guild.get_channel = lambda channel_id: None
        callback = cast(Any, Setup.hidden_channels.callback)
        with patch.dict(callback.__globals__, {"database_path": lambda guild_id: self.path}):
            await callback(Setup(Mock()), self.interaction)
            self.interaction.response.send_message.assert_awaited_once_with(
                "Aucun salon n'est exclu des logs.", ephemeral=True,
            )
            self.interaction.response.send_message.reset_mock()
            self.interaction.user.id = 99
            await callback(Setup(Mock()), self.interaction)
        self.interaction.response.send_message.assert_awaited_once_with(
            ":x: You don't have the permission to do this.", ephemeral=True,
        )

    async def test_hidden_channels_long_list_uses_followups(self):
        self.guild.get_channel = lambda channel_id: SimpleNamespace(id=channel_id)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.executemany(
                "INSERT INTO channels (name, id, hidden) VALUES (?, ?, 1)",
                [(str(channel_id), channel_id) for channel_id in range(100, 400)],
            )
        callback = cast(Any, Setup.hidden_channels.callback)
        with patch.dict(callback.__globals__, {"database_path": lambda guild_id: self.path}):
            await callback(Setup(Mock()), self.interaction)
        messages = [self.interaction.response.send_message.await_args.args[0]]
        messages += [call.args[0] for call in self.interaction.followup.send.await_args_list]
        self.assertGreater(len(messages), 1)
        self.assertTrue(all(len(message) <= 2000 for message in messages))
        self.assertEqual(sum(message.count("<#") for message in messages), 300)

    async def test_role_selection_updates_config_and_replaces_previous_role(self):
        old_role = SimpleNamespace(id=10, name="Old")
        role = SimpleNamespace(id=11, name="Staff")
        self.guild.get_role = lambda role_id: {10: old_role, 11: role}.get(role_id)
        self.interaction.data = {"custom_id": "staff_menu", "values": [str(role.id)]}
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("INSERT INTO roles (name, id, type) VALUES ('Old', 10, 'Staff')")
        with patch.dict(handle_role_selection.__globals__, {"database_path": lambda guild_id: self.path}):
            await handle_role_selection(cast(discord.Interaction, self.interaction), "staff_menu", "Staff", "Staff")
        self.assertEqual(self.config("staff_role"), 11)
        with closing(sqlite3.connect(self.path)) as conn:
            self.assertEqual(conn.execute("SELECT id, type FROM roles ORDER BY id").fetchall(),
                             [(10, None), (11, "Staff")])
        self.interaction.response.send_message.assert_awaited_once()

    async def test_ticket_category_updates_config(self):
        category = create_autospec(discord.CategoryChannel, instance=True)
        category.id = 20
        category.name = "Tickets"
        self.guild.get_channel = lambda channel_id: category if channel_id == 20 else None
        self.interaction.data = {"custom_id": "ticket_category", "values": ["20"]}
        callback = TicketCategory.ticket_category
        with patch.dict(callback.__globals__, {"database_path": lambda guild_id: self.path}):
            cog = TicketCategory()
            await cog.ticket_category(cast(discord.Interaction, self.interaction))
        self.assertEqual(self.config("ticket_parent"), 20)
        with closing(sqlite3.connect(self.path)) as conn:
            self.assertEqual(conn.execute("SELECT id FROM channels WHERE type = 'ticket_parent'").fetchall(),
                             [(20,)])
        self.interaction.response.send_message.assert_awaited_once()

    async def test_non_owner_cannot_change_ticket_limit(self):
        self.interaction.user.id = 99
        callback = cast(Any, Setup.max_ticket.callback)
        with patch.dict(callback.__globals__, {"database_path": lambda guild_id: self.path}):
            cog = Setup(Mock())
            await callback(cog, self.interaction, 5)
        self.assertEqual(self.config("ticket_limit"), 3)
        self.interaction.response.send_message.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
