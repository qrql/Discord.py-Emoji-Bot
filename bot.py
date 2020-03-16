import discord
import logging
from config import config

class EmojiBotClient(discord.Client):
	pass

if __name__ == "__main__":
	clientInstance = EmojiBotClient()
	if config["debug_mode"]:
		logging.basicConfig(level = logging.INFO)
	else:
		logging.basicConfig(level = logging.WARNING)
	clientInstance.run(config["discord_client_key"])