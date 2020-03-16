import logging

commands = {}
commandAliases = {}

_commandLogger = logging.getLogger("EmojiBot.Commands")

def getCommand(commandName):
	if commandName.lower() in commands:
		return commands[commandName.lower()]
	elif commandName.lower() in commandAliases:
		return commands[commandAliases[commandName.lower()]]
	return None

class CommandNameConflictException(Exception):
	pass

class CommandMetaclass(type):
	def __init__(cls, name, bases, attrs):
		if bases:
			commandName = (name if "name" not in attrs else attrs["name"]).lower()
			if commandName in commands or commandName in commandAliases:
				raise CommandNameConflictException(commandName)
			_commandLogger.info("Create command '{}'".format(commandName))
			commands[commandName] = cls
			if "aliases" in attrs:
				for alias in attrs["aliases"]:
					if alias in commands or alias in commandAliases:
						raise CommandNameConflictException(alias)
					_commandLogger.info("Create alias '{}' for '{}'".format(alias, commandName))
					commandAliases[alias] = commandName

class InvalidSyntaxException(Exception):
	pass

class InvalidArgumentException(Exception):
	pass

class Command(metaclass = CommandMetaclass):
	def __init__(self, message, argString):
		self.message = message
		self.author = message.author
		self.channel = message.channel
		self.guild = message.guild
		self.argString = argString
		self.args = self.getArguments()

	async def authorHasPermission(self):
		return True

	def getArguments(self):
		return self.argString.split()

	async def validateArguments(self):
		pass

	async def callback(self):
		raise NotImplementedError()