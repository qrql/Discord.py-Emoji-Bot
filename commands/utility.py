from command import Command, InvalidSyntaxException, InvalidArgumentException
from config import config
import textwrap

class Help(Command):
	async def callback(self):
		await self.channel.send(textwrap.dedent("""
			`{token}create emojiname` : start creating an emoji block
			`{token}setimage image_url` : set the image
			`{token}setemojiname NAME` : set the image name
			`{token}cropmode (crop|pad) (WIP)` changes the mode, defaulting to crop.
				crop : crop pixels from the image to reaching a multiple of block size
				pad  : pad pixels to the image to reach a multiple of the block size
			`{token}blocksize N` changes the block size to X by X pixels, defaulting to 128.
			`{token}abort` will abort the process.
			`{token}finalize` : finalize the process.
				Once finalized, the bot will DM one or several invite links to you. You have a limited time to join them!
				To finalize, the block size must be set such that there are less than 250 blocks.
		""").format(token = config["command_token"]))