import discord
import logging
from config import config
import commands

_emojiBotMasterLogger = logging.getLogger("EmojiBot")

class EmojiBotClient(discord.Client):
	async def on_message(self, message):
		if message.author == self.user:
			return
		if message.content.startswith(config["command_token"]):
			splitContent = message.content[len(config["command_token"]):].split(maxsplit = 2)
			if len(splitContent) > 0:
				commandString = splitContent[0]
				args = splitContent[1] if len(splitContent) == 2 else ""
				command = commands.getCommand(commandString)
				if command is None:
					if config["debug_mode"]:
						await message.channel.send("No such command '{}'".format(commandString))
					_emojiBotMasterLogger.info("Miss on command {} by user {}".format(commandString, message.author))
				else:
					_emojiBotMasterLogger.info("Hit on command {} by user {}".format(commandString, message.author))
					success, errMsg = False, "Something went wrong"
					try:
						commandInstance = command(message, args)
						if await commandInstance.authorHasPermission():
							await commandInstance.validateArguments()
							await commandInstance.callback()
							success = True
					except commands.InvalidSyntaxException:
						errMsg = "Invalid command syntax"
					except commands.InvalidArgumentException:
						errMsg = "Invalid arguments"
					except Exception as e:
						if config["debug_mode"]:
							errMsg = str(e)
						_emojiBotMasterLogger.error("Exception in command {} triggered by message {} by author {} : {}".format(commandString, message, message.author, e))
					if not success:
						_emojiBotMasterLogger.info("Command {} failed triggered by message {} by author {}".format(commandString, message, message.author))
						await message.channel.send(errMsg)

if __name__ == "__main__":
	clientInstance = EmojiBotClient()
	if config["debug_mode"]:
		logging.basicConfig(level = logging.INFO)
	else:
		logging.basicConfig(level = logging.WARNING)
	clientInstance.run(config["discord_client_key"])
