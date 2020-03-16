from command import Command, InvalidSyntaxException, InvalidArgumentException
import discord
import PIL
from PIL import Image
import database
import io
from config import config

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

class GetImage(Command):
	async def callback(self):
		img = database.getImageForUser(self.author)
		if img is None:
			return await self.message.channel.send("Error: No image set. User `{token}setimage` and attach the image to set one.".format(token = config["command_token"]))
		else:
			fileobj = discord.File(img, filename = "img.png")
			return await self.message.channel.send("Your image", file = fileobj)

class Abort(Command):
	async def callback(self):
		database.setImageForUser(self.author, None)