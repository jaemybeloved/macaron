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

# Constants ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

DESCRIPTION: str = "Copyright (c) 2024 'jaemybeloved' "\
    "<jade.pillow@protonmail.com>"

# Global Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

args: argparse.Namespace = None
config: dict[any] = None
intents: discord.Intents = discord.Intents.default()

void: any = None

# Classes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

class Macaron(discord.Client):
    def __init__(self, *, intents: discord.Intents) -> void:
        super().__init__(intents=intents)


# Functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>
        
def parse_arguments() -> void:
    global args, config

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="macaron", description=DESCRIPTION,
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

    Macaron(intents=intents).run(config["discord"]["token"])


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>