import unittest
from unittest.mock import AsyncMock, patch

from discord import app_commands

from mr_puwlerson.bot import Main


class CommandRegistrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_existing_slash_commands_load_and_sync(self):
        bot = Main()
        with patch.object(bot.tree, "sync", new_callable=AsyncMock) as sync:
            await bot.setup_hook()

        sync.assert_awaited_once_with()
        self.assertEqual(
            {command.name for command in bot.tree.get_commands()},
            {"coinflip", "help", "ping", "reload_ext", "report", "suggest",
             "ticket", "remove", "rename", "self_role",
             "mod", "blacklist", "giveaway", "nuke", "unblacklist",
             "plugins", "locale", "setup", "update"},
        )
        ticket = bot.tree.get_command("ticket")
        assert isinstance(ticket, app_commands.Group)
        self.assertEqual(
            {command.name for command in ticket.commands},
            {"add", "claim", "unclaim", "close"},
        )
        mod = bot.tree.get_command("mod")
        assert isinstance(mod, app_commands.Group)
        self.assertEqual(
            {command.name for command in mod.commands},
            {"clear", "timeout", "untimeout"},
        )
        setup = bot.tree.get_command("setup")
        assert isinstance(setup, app_commands.Group)
        self.assertEqual(
            {command.name for command in setup.commands},
            {"server", "roles", "channels", "hidden_channels", "tickets", "max_ticket"},
        )
        translator = bot.tree.translator
        assert isinstance(translator, app_commands.Translator)
        payloads = {
            command.name: await command.get_translated_payload(bot.tree, translator)
            for command in bot.tree.get_commands()
        }
        self.assertEqual(payloads["coinflip"]["name_localizations"]["fr"], "pileface")
        self.assertEqual(payloads["setup"]["description_localizations"]["fr"], "Pour configurer le bot")
        self.assertEqual(
            {option["name"] for option in payloads["setup"]["options"]},
            {"server", "roles", "channels", "hidden_channels", "tickets", "max_ticket"},
        )
        limit_option = next(option for option in payloads["setup"]["options"] if option["name"] == "max_ticket")
        self.assertEqual([option["name"] for option in limit_option["options"]], ["limit"])
        self.assertEqual(payloads["giveaway"]["description_localizations"]["fr"], "Lance un giveaway")
        report_options = payloads["report"]["options"]
        self.assertEqual([option["name"] for option in report_options], ["channel", "problem", "user"])
        self.assertEqual(report_options[0]["name_localizations"]["fr"], "salon")


if __name__ == "__main__":
    unittest.main()
