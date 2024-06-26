#
# Copyright (c) 2024 'jaemybeloved' <jade.pillow@protonmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

import argparse
import discord
import json
import logging
import pathlib
import psutil
import requests
import time
import whisper

from discord import app_commands
from os import getpid
# from typing import override

# Constants ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

AUTHOR_NAME: str = "'jaemybeloved' <jade.pillow@protonmail.com>"

COPYRIGHT: str = f"Copyright (c) 2024 {AUTHOR_NAME}"

PROJECT_NAME: str = "jaemybeloved/macaron"
PROJECT_DESCRIPTION: str = "「🐍」︲A Speech-To-Text Discord bot, " \
    "powered by OpenAI Whisper."

# Global Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

args: argparse.Namespace = None
config: dict[any] = None
guild: discord.Object = None
intents: discord.Intents = discord.Intents.default()

void: any = None

# Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

class Formatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.levelname = record.levelname.lower()

        return logging.Formatter.format(self, record)


class Macaron(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> void:
        super().__init__(intents=intents)

        self.model: whisper.Whisper = whisper.load_model("small")
        self.start_time: float = time.time()

        self.setup_logger()
        self.setup_tree()


    # @override
    async def on_ready(self) -> void:
        for guild in self.guilds:
            self.tree.copy_global_to(guild=guild)

            await self.tree.sync(guild=guild)

        self.logger.info(f"logged in as '{self.user}'")


    def setup_logger(self) -> void:
        logger: logging.Logger = logging.getLogger("discord")

        logger.setLevel(logging.INFO)

        handler: logging.StreamHandler = logging.StreamHandler()

        formatter: Formatter = Formatter(
            "[%(asctime)s] %(module)s: %(levelname)s: %(message)s",
            "%H:%M:%S"
        )

        handler.setFormatter(formatter)

        logger.addHandler(handler)

        self.logger = logger
    

    def setup_tree(self) -> void:
        self.tree = app_commands.CommandTree(self)

        @self.tree.command(name="info",
                           description="Show information about this bot.")
        async def info(interaction: discord.Interaction) -> void:
            embed: discord.Embed = discord.Embed(
                title=PROJECT_NAME,
                description=f"{PROJECT_DESCRIPTION}"
            )

            embed.timestamp = interaction.created_at

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>
            
            uptime: str = time.strftime(
                "%H:%M:%S", time.gmtime(time.time() - self.start_time)
            )

            embed.add_field(name="UPT", value=f"{uptime}")
            
            process: psutil.Process = psutil.Process(getpid())

            embed.add_field(name="CPU", 
                            value=f"{process.cpu_percent():.1f}%")

            embed.add_field(name="RAM", 
                            value=f"{process.memory_percent():.1f}%")

            embed.set_author(
                name=self.user.name, 
                icon_url=self.user.display_avatar
            )

            embed.set_footer(text=COPYRIGHT)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

            view: discord.ui.View = discord.ui.View()

            view.add_item(
                discord.ui.Button(label="GitHub Repository", 
                                  style=discord.ButtonStyle.url, 
                                  url=f"https://github.com/{PROJECT_NAME}"))

            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=False
            )

        pathlib.Path("_cache").mkdir(parents=True, exist_ok=True)

        @self.tree.context_menu(name="Transcribe!")
        async def transcribe(interaction: discord.Interaction,
                             message: discord.Message) -> void:
            await interaction.response.defer(ephemeral=False, thinking=True)

            if not message or not message.attachments:
                embed: discord.Embed = discord.Embed(
                    description="Please refer to a valid voice message!"
                )

                embed.timestamp = interaction.created_at

                embed.set_author(
                    name=self.user.name, 
                    icon_url=self.user.display_avatar
                )

                await interaction.followup.send(embed=embed)
            else:
                response: requests.Response = requests.get(
                    message.attachments[0].url)
                
                file_path: str = f"_cache/audio-{message.id}.ogg"
                
                with open(file_path, "wb") as file:
                    file.write(response.content)

                pred: dict[any] = self.model.transcribe(file_path)

                embed: discord.Embed = discord.Embed(
                    title="Prediction",
                    description=f"{pred['text']}"
                )

                embed.timestamp = interaction.created_at

                embed.add_field(name="Language", 
                            value=f"`{pred['language']}`")
                
                embed.add_field(name="Temperature", 
                            value=f"`{pred['segments'][0]['temperature']}`")

                embed.set_author(
                    name=self.user.name, 
                    icon_url=self.user.display_avatar
                )

                await interaction.followup.send(embed=embed)

                pathlib.Path(file_path).unlink(missing_ok=True)


# Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>
        
def parse_arguments() -> void:
    global args, config

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="macaron", description=COPYRIGHT,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-c", "--config",
        type=argparse.FileType("r", encoding="utf-8"),
        help="the path to the configuration file"
    )

    args = parser.parse_args()

    config = json.loads(args.config.read())


# Entry Point ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

if __name__ == "__main__":
    parse_arguments()

    Macaron(intents=intents).run(
        config["discord"]["token"], log_handler=None
    )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>