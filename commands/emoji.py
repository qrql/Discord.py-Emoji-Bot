from command import Command, InvalidSyntaxException, InvalidArgumentException
import discord
import PIL
from PIL import Image
import database
import io
from config import config
import math

class SetImage(Command):
	async def callback(self):
		if len(self.message.attachments) != 1:
			return await self.channel.send("Error: Must attach exactly one image")
		attachment = self.message.attachments[0]
		img = None
		try:
			img = io.BytesIO(await attachment.read())
			Image.open(io.BytesIO(img.getvalue())) # check that it can be parsed as an image
		except PIL.UnidentifiedImageError:
			return await self.message.channel.send("Error: Attachment is not an image")
		if database.getImageForUser(self.author):
			return await self.message.channel.send("Error: Image is already set. Use `{token}abort` to restart the emoji block creation.".format(token = config["command_token"]))
		database.setImageForUser(self.author, img.getvalue())

class SetEmojiName(Command):
	async def validateArguments(self):
		if len(self.args) != 1 or len(self.args[0]) < 2:
			raise InvalidArgumentException("Only argument must be a string of at least 2 characters")

	async def callback(self):
		database.setEmojiNameForUser(self.author, self.args[0])

class SetBlockSize(Command):
	def getArguments(self):
		try:
			return [int(self.argString)]
		except:
			raise InvalidSyntaxException()

	async def validateArguments(self):
		if self.args[0] < 16:
			raise InvalidArgumentException()
		return self.args

	async def callback(self):
		if database.getImageForUser(self.author) is None:
			return await self.message.channel.send("Error: No image set. Use `{token}setimage` first.")
		database.setBlockSizeForUser(self.author, self.args[0])

class GetImage(Command):
	async def callback(self):
		img = database.getImageForUser(self.author)
		if img is None:
			return await self.message.channel.send("Error: No image set. User `{token}setimage` and attach the image to set one.".format(token = config["command_token"]))
		else:
			fileobj = discord.File(img, filename = "img.png")
			return await self.message.channel.send("Your image", file = fileobj)

class CleanServers(Command):
	async def callback(self):
		i = 0
		for guild in [guild for guild in self.client.guilds if guild.owner.id is self.client.user.id]:
			i += 1
			await guild.delete()
		msg = "Error: No guilds to delete"
		if i == 1:
			msg = "Successfully deleted 1 guild"
		elif i > 1:
			msg = ("Successfully deleted {} guilds".format(i))
		return await self.channel.send(msg)

class Abort(Command):
	async def callback(self):
		database.setImageForUser(self.author, None)
		database.setEmojiNameForUser(self.author, None)
		database.setCropModeForUser(self.author, 0)
		database.setBlockSizeForUser(self.author, 128)

class Finalize(Command):
	async def callback(self):
		# TODO:
		# implement crop mode
		if len(self.client.guilds) >= 10:
			return await self.channel.send("Error: Cannot create guilds at the moment. Please try again later.")
		rawImage = database.getImageForUser(self.author)
		if rawImage is None:
			return await self.channel.send("Error: No image set. Use `{token}setimage` and attach the image to set one.".format(token = config["command_token"]))
		emojiName = database.getEmojiNameForUser(self.author)
		if emojiName is None:
			return await self.channel.send("Error: Emoji name not set. Use `{token}setemojiname name` to set a name.")

		baseImage = Image.open(rawImage)
		blockSize = database.getBlockSizeForUser(self.author)
		(width, height) = baseImage.size

		diffX, diffY = width % blockSize, height % blockSize
		newWidth, newHeight = width - diffX, height - diffY
		offsetX, offsetY = diffX / 2, diffY / 2
		chunkAlignmentTuple = (math.ceil(offsetX), math.ceil(offsetY), width - math.floor(offsetX), height - math.floor(offsetY))

		centeredChunkAlignedImage = baseImage.crop(chunkAlignmentTuple)

		if newWidth // blockSize == 0 or newHeight // blockSize == 0:
			return await self.channel.send("Image is not big enough. Try a smaller size or abort emoji block creation.")

		files = []
		emojiString = ""
		i = 0
		for y in range(0, newHeight // blockSize):
			for x in range(0, newWidth // blockSize):
				newFile = io.BytesIO()
				section = centeredChunkAlignedImage.crop((x * blockSize, y * blockSize, (x+1) * blockSize, (y+1) * blockSize))
				section.save(newFile, "png")
				files.append(newFile)
				emojiString += "\\:{}{}\\:".format(emojiName, i)
				i += 1
			emojiString += "\n"
		
		await self.channel.send("Creating guilds. This may take a minute.")

		guilds = []
		invite_urls = []
		for guildNumber in range(0, len(files) // 50 + 1):
			# TODO:
			# This can fail if either len(files) // 50 + 1 < 10 - len(self.client.guilds) or someone else runs finalize while this is being executed
			# Implement a queue
			newGuild = await self.client.create_guild("Emoji Bot Server {} {}".format(emojiName, guildNumber))
			for emojiNumber in range(50 * guildNumber, 50 * (guildNumber + 1)):
				if emojiNumber < len(files):
					file = files[emojiNumber]
					await newGuild.create_custom_emoji(name = "{}{}".format(emojiName, emojiNumber), image = file.getvalue())
			channel = await newGuild.create_text_channel("general")
			invite = await channel.create_invite()
			guilds.append(newGuild)
			invite_urls.append(invite.url)


		await self.channel.send("\n".join(invite_urls))
		targetChannel = guilds[len(guilds) - 1].channels[0]
		for section in range(0, len(emojiString) // 2000 + 1):
			substr = emojiString[section*2000:(section+1)*2000]
			await targetChannel.send(substr)
		if len(emojiString.split("\n")) > 0:
			for line in emojiString.split("\n"):
				if len(line) > 0:
					await targetChannel.send(line)

		database.setImageForUser(self.author, None)
		database.setEmojiNameForUser(self.author, None)
		database.setCropModeForUser(self.author, 0)
		database.setBlockSizeForUser(self.author, 128)