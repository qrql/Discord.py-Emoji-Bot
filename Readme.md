# Emoji Bot v0.1
A bot to turn images into a metric fuck-ton of emojis, for Nitro users to dump as one massive emoji.

# How do I use it?
First, set an image with !setimage and upload the image as an attachment to that message. Afterwards, use !setemojiname to set the name for the emoji, and optionally, use !setblocksize to set the number of pixels each block is.
After you're done, use !finalize to finalize the process and create the servers. This can take some time.
If you've changed your mind, you can use !abort.

# How do I run it?
Install discord.py and Pillow. Clone the repo, and create a file called config.json in the top-level directory. It should have the following keys:
* discord_client_key : Your client key for your bot
* debug_mode : A true/false value as to whether to allow debug output
* command_token : The token that starts commands
* database : A path to the sqlite database, which will be created if it doesn't exist