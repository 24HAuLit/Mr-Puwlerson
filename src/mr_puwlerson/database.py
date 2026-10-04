"""Initialize the SQLite files used by the bot (run from the repository root)."""

import argparse
import sqlite3
from contextlib import closing
from pathlib import Path


# Keep column order for tables used with positional INSERT statements.
TABLES = {
    "config": """CREATE TABLE config (
        server_id INTEGER NOT NULL, logs_server INTEGER, locale TEXT NOT NULL DEFAULT 'en',
        suggestion_cooldown INTEGER DEFAULT 0, auto_role INTEGER DEFAULT 0,
        ticket_parent INTEGER, ticket_limit INTEGER DEFAULT 3, staff_role INTEGER,
        default_role INTEGER, owner_role INTEGER, admin_role INTEGER, suggest_channel INTEGER
    )""",
    "antiraid": "CREATE TABLE antiraid (member INTEGER NOT NULL, code TEXT)",
    "blacklist": "CREATE TABLE blacklist (blacklist_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, reason TEXT)",
    "channels": "CREATE TABLE channels (name TEXT, id INTEGER, type TEXT DEFAULT NULL, hidden INTEGER DEFAULT 0)",
    "cooldown": "CREATE TABLE cooldown (user INTEGER NOT NULL, timestamp INTEGER)",
    "locale": "CREATE TABLE locale (locale TEXT DEFAULT 'en' NOT NULL)",
    "logs_channels": "CREATE TABLE logs_channels (name TEXT NOT NULL, id INTEGER NOT NULL)",
    "plugins": "CREATE TABLE plugins (name TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'false')",
    "reports": "CREATE TABLE reports (author_id INTEGER NOT NULL, user_id INTEGER, channel_id INTEGER, problem TEXT)",
    "roles": "CREATE TABLE roles (name TEXT, id INTEGER, type TEXT DEFAULT NULL)",
    "self_role": "CREATE TABLE self_role (message_id INTEGER NOT NULL, emoji ANY, role_id INTEGER)",
    "ticket": "CREATE TABLE ticket (ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER NOT NULL, staff_id INTEGER, channel_id INTEGER)",
    "ticket_count": "CREATE TABLE ticket_count (user_id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)",
}

# Only these missing columns can be appended without changing existing records.
ADDITIONS = {
    "config": {"logs_server": "INTEGER", "locale": "TEXT DEFAULT 'en'", "suggestion_cooldown": "INTEGER DEFAULT 0",
               "auto_role": "INTEGER DEFAULT 0", "ticket_parent": "INTEGER",
               "ticket_limit": "INTEGER DEFAULT 3", "staff_role": "INTEGER", "default_role": "INTEGER",
               "owner_role": "INTEGER", "admin_role": "INTEGER", "suggest_channel": "INTEGER"},
    "channels": {"hidden": "INTEGER DEFAULT 0"},
    "plugins": {"status": "TEXT DEFAULT 'false'"},
}
POSITIONAL = {"antiraid", "channels", "cooldown", "reports", "roles", "self_role", "ticket"}


def _columns(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return conn.execute(f'PRAGMA table_info("{table}")').fetchall()


def _ensure_table(conn: sqlite3.Connection, table: str, ddl: str) -> None:
    kind = conn.execute("SELECT type FROM sqlite_master WHERE name = ?", (table,)).fetchone()
    if kind is None:
        conn.execute(ddl)
    elif kind[0] != "table":
        raise ValueError(f"{table}: expected a table, found {kind[0]}")


def _guild_schema(conn: sqlite3.Connection, guild_id: int) -> None:
    for table, ddl in TABLES.items():
        _ensure_table(conn, table, ddl)
        columns = _columns(conn, table)
        names = [column[1] for column in columns]
        if table == "cooldown" and names == ["user", "suggestion"]:
            conn.execute('ALTER TABLE cooldown RENAME COLUMN suggestion TO timestamp')
            names = ["user", "timestamp"]
        if table == "ticket" and len(columns) > 2 and columns[2][3]:
            raise ValueError("ticket.staff_id is NOT NULL; cannot open unclaimed tickets with this schema")
        if table == "config" and "logs_server" in names:
            logs = next(column for column in columns if column[1] == "logs_server")
            if logs[3]:
                # The old DDL required a real logs-server ID. Never invent one.
                # An empty, uncustomized table can be recreated without losing data.
                objects = conn.execute("SELECT name FROM sqlite_master WHERE tbl_name = 'config' "
                                       "AND type IN ('index', 'trigger')").fetchall()
                if conn.execute("SELECT 1 FROM config LIMIT 1").fetchone() or objects:
                    raise ValueError("config.logs_server is NOT NULL; cannot safely seed NULL or rebuild a populated/customized config")
                conn.execute("DROP TABLE config")
                conn.execute(ddl)
                columns = _columns(conn, table)
                names = [column[1] for column in columns]
        required = _columns_for_ddl(table)
        if table == "config" and "server_id" not in names:
            raise ValueError("config: missing server_id; cannot identify existing settings")
        if table == "plugins" and "name" not in names:
            raise ValueError("plugins: missing name; cannot identify existing settings")
        if table == "ticket_count" and not {"user_id", "count"}.issubset(names):
            raise ValueError("ticket_count: missing user_id or count")
        for name in required:
            if name not in names:
                definition = ADDITIONS.get(table, {}).get(name)
                if definition is None:
                    raise ValueError(f"{table}: missing required column {name}; cannot migrate safely")
                conn.execute(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {definition}')
        if table in POSITIONAL:
            actual = [column[1] for column in _columns(conn, table)]
            if actual != required:
                raise ValueError(f"{table}: incompatible column order/layout {actual}; positional INSERT requires {required}")
        if table == "config" and "ticket_count" in names and "ticket_limit" not in names:
            conn.execute("UPDATE config SET ticket_limit = ticket_count WHERE ticket_count IS NOT NULL")

    rows = conn.execute("SELECT server_id FROM config").fetchall()
    if len(rows) > 1 or (rows and rows[0][0] != guild_id):
        raise ValueError("config: expected at most one row for the requested guild; no settings changed")
    if not rows:
        conn.execute("INSERT INTO config (server_id, locale, suggestion_cooldown, auto_role, ticket_limit) "
                     "VALUES (?, 'en', 0, 0, 3)", (guild_id,))
    for plugin in ("suggestion", "report", "giveaway"):
        if conn.execute("SELECT 1 FROM plugins WHERE name = ? LIMIT 1", (plugin,)).fetchone() is None:
            conn.execute("INSERT INTO plugins (name, status) VALUES (?, 'false')", (plugin,))


def _columns_for_ddl(table: str) -> list[str]:
    # Inspect canonical DDL with SQLite rather than maintaining a second column list.
    with closing(sqlite3.connect(":memory:")) as memory:
        memory.execute(TABLES[table])
        return [column[1] for column in _columns(memory, table)]


def initialize_database(guild_id: int, database_dir: Path = Path("Database")) -> Path:
    """Create/repair guild and temp-join schemas without resetting existing settings."""
    if type(guild_id) is not int or guild_id <= 0 or guild_id > 2**63 - 1:
        raise ValueError("guild_id must be a positive SQLite-compatible integer")
    database_dir = Path(database_dir)
    database_dir.mkdir(parents=True, exist_ok=True)
    guild_path = database_dir / f"{guild_id}.db"
    with closing(sqlite3.connect(guild_path)) as conn:
        # SQLite commits attached on-disk databases together in rollback-journal mode.
        conn.execute("ATTACH DATABASE ? AS temp_join", (str(database_dir / "temp_join.db"),))
        conn.execute("BEGIN IMMEDIATE")
        try:
            _guild_schema(conn, guild_id)
            kind = conn.execute("SELECT type FROM temp_join.sqlite_master WHERE name = 'join'").fetchone()
            if kind is None:
                conn.execute('CREATE TABLE temp_join."join" (user_id INTEGER, guild_id INTEGER)')
            elif kind[0] != "table":
                raise ValueError(f"temp_join.join: expected a table, found {kind[0]}")
            columns = conn.execute('PRAGMA temp_join.table_info("join")').fetchall()
            if [column[1] for column in columns] != ["user_id", "guild_id"]:
                raise ValueError("temp_join.join: incompatible column order/layout")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return guild_path


CONFIG_IDS = (
    "logs_server", "owner_role", "admin_role", "staff_role", "default_role",
    "ticket_parent", "suggest_channel",
)
LOG_NAMES = frozenset({
    "ban", "blacklist", "clear", "close", "create", "create-channel", "create-role",
    "delete", "delete-channel", "edit", "giveaway", "join-quit", "new", "nuke",
    "report", "timeout",
})


def _positive_id(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("expected a positive integer") from error
    if not 0 < number < 2**63:
        raise argparse.ArgumentTypeError("expected a positive SQLite-compatible integer")
    return number


def _log_channel(value: str) -> tuple[str, int]:
    name, separator, channel_id = value.partition("=")
    if not separator or name not in LOG_NAMES:
        raise argparse.ArgumentTypeError(f"expected NAME=ID where NAME is one of: {', '.join(sorted(LOG_NAMES))}")
    return name, _positive_id(channel_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize or configure Database/<guild_id>.db")
    parser.add_argument("guild_id", type=_positive_id, help="Discord server ID")
    for field in CONFIG_IDS:
        parser.add_argument(f"--{field.replace('_', '-')}", type=_positive_id, metavar="ID")
    parser.add_argument("--locale", choices=("en", "fr"))
    parser.add_argument("--ticket-limit", type=_positive_id)
    parser.add_argument("--suggestion-cooldown", type=int, metavar="SECONDS")
    parser.add_argument("--log-channel", action="append", type=_log_channel, default=[], metavar="NAME=ID")
    args = parser.parse_args()
    if args.suggestion_cooldown is not None and args.suggestion_cooldown < 0:
        parser.error("--suggestion-cooldown cannot be negative")
    settings = {field: getattr(args, field) for field in (*CONFIG_IDS, "locale", "ticket_limit", "suggestion_cooldown")
                if getattr(args, field) is not None}
    try:
        path = initialize_database(args.guild_id)
        with closing(sqlite3.connect(path)) as conn, conn:
            for field, value in settings.items():
                conn.execute(f'UPDATE config SET "{field}" = ?', (value,))
            for name, channel_id in args.log_channel:
                if conn.execute("SELECT 1 FROM logs_channels WHERE name = ?", (name,)).fetchone():
                    conn.execute("UPDATE logs_channels SET id = ? WHERE name = ?", (channel_id, name))
                else:
                    conn.execute("INSERT INTO logs_channels (name, id) VALUES (?, ?)", (name, channel_id))
    except (ValueError, sqlite3.Error) as error:
        parser.exit(1, f"Database initialization failed: {error}\n")
    print(f"Initialized {path} and {path.parent / 'temp_join.db'}")


if __name__ == "__main__":
    main()
