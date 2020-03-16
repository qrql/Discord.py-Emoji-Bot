import sqlite3
from config import config
_conn = sqlite3.connect(config["database"])
_conn.row_factory = sqlite3.Row
import io

_conn.execute("""
	CREATE TABLE IF NOT EXISTS guilds
	(
		guild_id INTEGER PRIMARY KEY,
		command_token STRING NOT NULL DEFAULT "!"
	);
""")
_conn.execute("""
	CREATE TABLE IF NOT EXISTS users
	(
		user_id INTEGER PRIMARY KEY,
		image BLOB,
		crop_mode INTEGER DEFAULT 0,
		block_size INTEGER DEFAULT 128,
		emoji_name STRING
	);
""")

def _createUserIfNull(user_id):
	try:
		_conn.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
	except sqlite3.IntegrityError:
		pass

def getImageForUserId(user_id):
	blob = _conn.execute("SELECT image FROM users WHERE user_id LIKE (?) AND image IS NOT NULL", (user_id,)).fetchone()
	if blob:
		return io.BytesIO(blob["image"])
	return None

def getImageForUser(user):
	return getImageForUserId(user.id )

def setImageForUserId(user_id, imageBytes):
	_createUserIfNull(user_id)
	with _conn:
		if imageBytes is None:
			_conn.execute("UPDATE users SET image = NULL WHERE user_id LIKE (?)", (user_id,))
		else:
			_conn.execute("UPDATE users SET image = (?) WHERE user_id LIKE (?)", (imageBytes, user_id))

def setImageForUser(user, image):
	return setImageForUserId(user.id, image)

def getCropModeForUserId(user_id):
	value = _conn.execute("SELECT crop_mode FROM users WHERE user_id LIKE (?)", (user_id,)).fetchone()
	if value:
		return value["crop_mode"]
	return 0

def getCropModeForUser(user):
	return getCropModeForUserId(user.id)

def setCropModeForUserId(user_id, value):
	if value < 0 or value > 1:
		raise ValueError("Out of constraints")
	_createUserIfNull(user_id)
	with _conn:
		_conn.execute("UPDATE users SET crop_mode = (?) WHERE user_id LIKE (?)", (value, user_id))

def setCropModeForUser(user, value):
	return setCropModeForUserId(user.id, value)

def getBlockSizeForUserId(user_id):
	value = _conn.execute("SELECT block_size FROM users WHERE user_id LIKE (?)", (user_id,)).fetchone()
	if value:
		return value["block_size"]
	return 128

def getBlockSizeForUser(user):
	return getBlockSizeForUserId(user.id)

def setBlockSizeForUserId(user_id, value):
	if value < 0 or value > 128:
		raise ValueError("Out of constraints")
	_createUserIfNull(user_id)
	with _conn:
		_conn.execute("UPDATE users SET block_size = (?) WHERE user_id LIKE (?)", (value, user_id))

def setBlockSizeForUser(user, value):
	return setBlockSizeForUser(user.id, value)

def getEmojiNameForUserId(user_id):
	value = _conn.execute("SELECT emoji_name FROM users WHERE user_id LIKE (?)", (user_id,)).fetchone()
	if value:
		return value["emoji_name"]
	return None

def getEmojiNameForUser(user):
	return getEmojiNameForUserId(user.id)

def setEmojiNameForUserId(user_id, value):
	_createUserIfNull(user_id)
	with _conn:
		if value is None:
			_conn.execute("UPDATE users SET emoji_name = NULL WHERE user_id LIKE (?)", (user_id,))
		else:
			_conn.execute("UPDATE users SET emoji_name = (?) WHERE user_id LIKE (?)", (value, user_id))

def setEmojiNameForUser(user, value):
	return setEmojiNameForUserId(user.id, value)