import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing, contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock, patch

import discord

from mr_puwlerson.database import initialize_database
from mr_puwlerson.listeners.on_guild_join import OnNewGuild


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "Database"
        self.guild_id = 123456789

    @contextmanager
    def connect(self, filename=None):
        with closing(sqlite3.connect(self.directory / (filename or f"{self.guild_id}.db"))) as conn, conn:
            yield conn

    def columns(self, conn, table):
        return [row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')]

    def test_clean_schema_and_positional_inserts(self):
        path = initialize_database(self.guild_id, self.directory)
        self.assertEqual(path, self.directory / f"{self.guild_id}.db")
        with self.connect() as conn:
            names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            self.assertTrue({"config", "cooldown", "antiraid", "blacklist", "channels", "locale",
                             "logs_channels", "plugins", "reports", "roles", "self_role", "ticket",
                             "ticket_count"}.issubset(names))
            self.assertEqual(self.columns(conn, "cooldown"), ["user", "timestamp"])
            self.assertEqual(self.columns(conn, "reports"), ["author_id", "user_id", "channel_id", "problem"])
            config = dict(zip(self.columns(conn, "config"), conn.execute("SELECT * FROM config").fetchone()))
            self.assertEqual(config, {"server_id": self.guild_id, "logs_server": None, "locale": "en",
                                      "suggestion_cooldown": 0, "auto_role": 0, "ticket_parent": None,
                                      "ticket_limit": 3, "staff_role": None, "default_role": None,
                                      "owner_role": None, "admin_role": None, "suggest_channel": None})
            self.assertEqual(dict(conn.execute("SELECT name, status FROM plugins")),
                             {"suggestion": "false", "report": "false", "giveaway": "false"})
            conn.execute("INSERT INTO cooldown VALUES (?, ?)", (5, 0))
            conn.execute("INSERT INTO reports VALUES (?, ?, ?, ?)", (5, None, None, "hello"))
            conn.execute("INSERT INTO ticket VALUES (NULL, ?, NULL, ?)", (5, 8))
            conn.execute("INSERT INTO ticket_count (user_id) VALUES (?)", (5,))
            self.assertEqual(conn.execute("SELECT count FROM ticket_count WHERE user_id = 5").fetchone(), (0,))
        with self.connect("temp_join.db") as conn:
            self.assertEqual(self.columns(conn, "join"), ["user_id", "guild_id"])
            conn.execute("INSERT INTO 'join' VALUES (?, ?)", (5, self.guild_id))
            self.assertEqual(conn.execute("SELECT guild_id FROM 'join' WHERE user_id = 5").fetchone(),
                             (self.guild_id,))

    def test_idempotent_preserves_records_and_settings(self):
        initialize_database(self.guild_id, self.directory)
        with self.connect() as conn:
            conn.execute("UPDATE config SET locale = 'fr', ticket_limit = 8, logs_server = 42")
            conn.execute("UPDATE plugins SET status = 'true' WHERE name = 'suggestion'")
            conn.execute("INSERT INTO blacklist (user_id, reason) VALUES (1, 'test')")
        with self.connect("temp_join.db") as conn:
            conn.execute("INSERT INTO 'join' VALUES (1, ?)", (self.guild_id,))
        initialize_database(self.guild_id, self.directory)
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT count(*), locale, ticket_limit, logs_server FROM config").fetchone(),
                             (1, "fr", 8, 42))
            self.assertEqual(dict(conn.execute("SELECT name, status FROM plugins"))["suggestion"], "true")
            self.assertEqual(conn.execute("SELECT user_id, reason FROM blacklist").fetchall(), [(1, "test")])
            self.assertEqual(conn.execute("SELECT count(*) FROM plugins").fetchone()[0], 3)
        with self.connect("temp_join.db") as conn:
            self.assertEqual(conn.execute("SELECT * FROM 'join'").fetchall(), [(1, self.guild_id)])

    def test_partial_old_schema_migrates_without_clobbering(self):
        self.directory.mkdir()
        with self.connect() as conn:
            conn.execute("CREATE TABLE config (server_id INTEGER, logs_server INTEGER, locale TEXT, "
                         "suggestion_cooldown INTEGER, auto_role INTEGER, ticket_parent INTEGER, "
                         "ticket_count INTEGER, staff_role INTEGER, default_role INTEGER, "
                         "owner_role INTEGER, admin_role INTEGER)")
            conn.execute("INSERT INTO config VALUES (?, 77, 'fr', 40, 1, 55, 9, 33, 22, 11, 44)",
                         (self.guild_id,))
            conn.execute("CREATE TABLE cooldown (user INTEGER, suggestion INTEGER)")
            conn.execute("INSERT INTO cooldown VALUES (5, 123)")
            conn.execute("CREATE TABLE plugins (name TEXT, status TEXT)")
            conn.execute("INSERT INTO plugins VALUES ('report', 'true')")
            conn.execute("CREATE TABLE channels (name TEXT, id INTEGER, type TEXT)")
            conn.execute("INSERT INTO channels VALUES ('general', 100, NULL)")
        initialize_database(self.guild_id, self.directory)
        initialize_database(self.guild_id, self.directory)
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT locale, logs_server, ticket_count, ticket_limit, suggest_channel "
                                          "FROM config").fetchall(), [("fr", 77, 9, 9, None)])
            self.assertEqual(self.columns(conn, "cooldown"), ["user", "timestamp"])
            self.assertEqual(conn.execute("SELECT * FROM cooldown").fetchall(), [(5, 123)])
            self.assertEqual(conn.execute("SELECT name, id, hidden FROM channels").fetchall(),
                             [("general", 100, 0)])
            self.assertEqual(dict(conn.execute("SELECT name, status FROM plugins"))["report"], "true")

    def test_empty_ddl_config_with_nonnull_logs_server_can_be_rebuilt(self):
        self.directory.mkdir()
        with self.connect() as conn:
            conn.execute("CREATE TABLE config (server_id INTEGER NOT NULL, logs_server INTEGER NOT NULL, "
                         "locale TEXT DEFAULT EN_US NOT NULL, ticket_count INTEGER)")
        initialize_database(self.guild_id, self.directory)
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT logs_server, locale, ticket_limit FROM config").fetchone(),
                             (None, "en", 3))

    def test_unsafe_config_rolls_back_without_join_table(self):
        self.directory.mkdir()
        with self.connect() as conn:
            conn.execute("CREATE TABLE config (server_id INTEGER, logs_server INTEGER NOT NULL)")
            conn.execute("INSERT INTO config VALUES (?, 99)", (self.guild_id,))
        with self.assertRaisesRegex(ValueError, "logs_server"):
            initialize_database(self.guild_id, self.directory)
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT * FROM config").fetchall(), [(self.guild_id, 99)])
            self.assertIsNone(conn.execute("SELECT name FROM sqlite_master WHERE name = 'antiraid'").fetchone())
        with self.connect("temp_join.db") as conn:
            self.assertIsNone(conn.execute("SELECT name FROM sqlite_master WHERE name = 'join'").fetchone())

    def test_incompatible_join_rolls_back_guild_schema(self):
        self.directory.mkdir()
        with self.connect("temp_join.db") as conn:
            conn.execute('CREATE TABLE "join" (guild_id INTEGER, user_id INTEGER)')
            conn.execute('INSERT INTO "join" VALUES (?, 5)', (self.guild_id,))
        with self.assertRaisesRegex(ValueError, "temp_join.join"):
            initialize_database(self.guild_id, self.directory)
        with self.connect() as conn:
            self.assertIsNone(conn.execute("SELECT name FROM sqlite_master WHERE name = 'config'").fetchone())
        with self.connect("temp_join.db") as conn:
            self.assertEqual(conn.execute('SELECT * FROM "join"').fetchall(), [(self.guild_id, 5)])

    def test_invalid_ids_and_incompatible_cooldown(self):
        for value in (0, -1, True, "12", 2**63):
            with self.subTest(value=value), self.assertRaises(ValueError):
                initialize_database(cast(int, value), self.directory)
        self.assertFalse(self.directory.exists())
        self.directory.mkdir()
        with self.connect() as conn:
            conn.execute("CREATE TABLE cooldown (suggestion INTEGER, user INTEGER)")
            conn.execute("INSERT INTO cooldown VALUES (123, 5)")
        with self.assertRaisesRegex(ValueError, "cooldown"):
            initialize_database(self.guild_id, self.directory)
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT * FROM cooldown").fetchall(), [(123, 5)])
            self.assertIsNone(conn.execute("SELECT name FROM sqlite_master WHERE name = 'config'").fetchone())

    def test_cli_uses_working_directory_without_discord(self):
        project = Path(__file__).resolve().parents[1]
        base = [sys.executable, "-m", "mr_puwlerson.database", str(self.guild_id)]
        environment = {"PYTHONPATH": str(project / "src")}
        result = subprocess.run(base + ["--locale", "fr", "--owner-role", "123", "--ticket-parent", "456",
                                        "--log-channel", "create=789", "--log-channel", "close=789"],
                                cwd=self.temp.name, env=environment, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.directory / f"{self.guild_id}.db").exists())
        self.assertTrue((self.directory / "temp_join.db").exists())
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT locale, owner_role, ticket_parent FROM config").fetchone(),
                             ("fr", 123, 456))
            self.assertEqual(dict(conn.execute("SELECT name, id FROM logs_channels")),
                             {"create": 789, "close": 789})
        second = subprocess.run(base + ["--log-channel", "create=987"], cwd=self.temp.name,
                                env=environment, capture_output=True, text=True, check=False)
        self.assertEqual(second.returncode, 0, second.stderr)
        with self.connect() as conn:
            self.assertEqual(conn.execute("SELECT locale, owner_role FROM config").fetchone(), ("fr", 123))
            self.assertEqual(dict(conn.execute("SELECT name, id FROM logs_channels")),
                             {"create": 987, "close": 789})
        invalid = subprocess.run(base + ["--log-channel", "invalid=1"], cwd=self.temp.name,
                                 env=environment, capture_output=True, text=True, check=False)
        self.assertNotEqual(invalid.returncode, 0)


class GuildInitializationTests(unittest.IsolatedAsyncioTestCase):
    async def test_existing_and_new_guilds_are_initialized(self):
        bot = SimpleNamespace(guilds=[SimpleNamespace(id=123), SimpleNamespace(id=456)])
        initialize = Mock()
        with patch.dict(OnNewGuild.on_ready.__globals__, {"initialize_database": initialize}):
            cog = OnNewGuild(bot)
            await cog.on_ready()
            await cog.on_guild_join(cast(discord.Guild, SimpleNamespace(id=789)))
        self.assertEqual([call.args[0] for call in initialize.call_args_list], [123, 456, 789])


if __name__ == "__main__":
    unittest.main()
