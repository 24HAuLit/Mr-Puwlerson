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

Guild data is stored in `Database/<guild-id>.db`. **New-guild database setup is not yet complete:** the join listener creates some tables but does not create and populate the `config` table required by several commands. Those commands require an already provisioned guild database; `/setup` does not currently initialize one. Ticket transcripts are also unavailable at present.

## Development

Run the offline command-registration test with:

```sh
uv run python -m unittest discover -s tests -v
```

This test checks extension loading, slash-command registration, and selected French localizations without connecting to Discord.
