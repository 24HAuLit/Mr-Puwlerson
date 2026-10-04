# Mr. Puwlerson

[![Discord community](https://img.shields.io/discord/419529681885331456?label=Discord&logo=discord)](https://discord.gg/VDPUKScFPf)

Mr. Puwlerson is a general-purpose Discord bot built with [discord.py](https://discordpy.readthedocs.io/). It provides slash commands and event listeners for server administration and community workflows.

## Features

- Ticket creation, claiming, and management
- Moderation tools, including message clearing, timeouts, and blacklisting
- Suggestions, reports, giveaways, and self-assignable roles
- Server event logs and per-server settings backed by SQLite
- English and French command localizations

## Requirements

- Python 3.14 or newer and [`uv`](https://docs.astral.sh/uv/), **or** Nix with flakes enabled
- A Discord application and bot token
- The gateway intents required by the bot: it currently requests `discord.Intents.all()`, including privileged intents that must be enabled in the Discord Developer Portal

## Getting started

From the repository root, install the dependencies recorded in `uv.lock`:

```sh
uv sync --locked
```

Create a `.env` file in the repository root and set your bot token:

```dotenv
TOKEN_OFFICIAL=your-bot-token
```

Keep this file private; `.env` is ignored by Git. Start the bot from the repository root so it can find its `Database/` directory:

```sh
uv run mr-puwlerson
```

The bot registers its slash commands with Discord on startup. Invite it with the `bot` and `applications.commands` scopes and grant the permissions needed for the features you intend to use.

### Nix development shell

The included `flake.nix` provides Python 3.14 and `uv` on Linux and macOS. It does not install the Python dependencies for you:

```sh
nix develop
uv sync --locked
uv run mr-puwlerson
```

The first `nix develop` needs network access to resolve the `nixpkgs` input. The shell sets `SSL_CERT_FILE` to Nix's CA bundle.

### TLS certificates

Discord login requires a trusted CA bundle. If Python has no default CA file, the bot uses `/etc/ssl/certs/ca-certificates.crt` when available; it does not turn off certificate verification. To use a different trust store (for example, a corporate CA), set `SSL_CERT_FILE` to the path of your trusted PEM bundle before starting the bot.

## Server configuration

Guild data is stored in `Database/<guild-id>.db`. On startup and when joining a new guild, the bot creates any missing tables, a default English `config` row, disabled plugin rows, and the shared `Database/temp_join.db` used for verification. Existing rows and settings are preserved. You can also initialize a guild database before starting the bot, from the repository root:

```sh
uv run python -m mr_puwlerson.database GUILD_ID
```

Replace `GUILD_ID` with the server ID. This restores **empty storage**, not lost ticket, blacklist, or report records. The old `Database/ddl/main/` SQL files are not the current authoritative schema; use the initializer instead.

To set server-specific IDs, rerun the same command with options (replace every uppercase value with an actual Discord ID):

```sh
uv run python -m mr_puwlerson.database GUILD_ID \
  --owner-role OWNER_ROLE_ID --staff-role STAFF_ROLE_ID \
  --ticket-parent TICKET_CATEGORY_ID \
  --log-channel create=LOG_CHANNEL_ID --log-channel close=LOG_CHANNEL_ID
```

Use `--help` for all settings, including `--admin-role`, `--default-role`, `--suggest-channel`, `--logs-server`, `--locale`, `--ticket-limit`, `--suggestion-cooldown`, and repeated `--log-channel NAME=ID`. Configure actual log channels for each feature you use (for example, `report`, `blacklist`, `clear`, `timeout`, and `nuke`); **no channel or role IDs are guessed**. Plugins start disabled and can be enabled with `/plugins` after their required channels are configured. The `/setup` command displays settings but does not fill missing IDs. Ticket transcripts are unavailable at present.

These database files are ignored by Git. Set up automatic off-device SQLite backups before relying on the bot; the initializer cannot recover records deleted during a PC reset.

## Development

Run the offline tests with:

```sh
uv run python -m unittest discover -s tests -v
```

The tests cover extension loading, slash-command registration, selected French localizations, and SQLite initialization without connecting to Discord.
