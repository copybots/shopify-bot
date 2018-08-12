import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import time
import json
import os

#----------------------------------------------------------------------------------------------------
# These variables must be filled out in order for the bot to work.
#
# selfbot: If you want a selfbot, just leave it as True, but if you ever want to use it on a normal bot, set it to False.
# token : The account token on which the bot will be running.
# commands_server_id : The bot will only respond to commands in the server with this server ID.
#                      If you leave it blank, the bot will respond to commands in every server.
# commands_channel_id : The bot will only respond to commands in the channel with this channel ID.
#                       If you leave it blank, the bot will respond to commands in every channel (in the server
#                       with the server ID that you put).

selfbot = False
token = str(os.environ.get("BOT_TOKEN"))
commands_server_id = str(os.environ.get("COMMANDS_SERVER_ID"))
commands_channel_id = str(os.environ.get("COMMANDS_SERVER_ID"))

#----------------------------------------------------------------------------------------------------
# These variables can be edited in the code, but are designed to be changed through discord commands.
# To see more commands type !help in discord.
#
# copy_server_ids : The servers to copy from.
# copy_channel_ids : The channels inside those servers to copy from.
# post_server_ids : The servers to post those messages to.
# post_channel_ids : The channels inside those servers to post those messages to.

copy_server_ids = []
copy_channel_ids = []
post_server_ids = []
post_channel_ids = []

memberlist = []
wordlist = []
case_sensitive_wordlist = True

#----------------------------------------------------------------------------------------------------

Client = discord.Client()
bot = commands.Bot(command_prefix="!")

edit_msg_list = []
edit_msg_list_length = 10

filename = "botinfo.cfg"
filedata = {"setup_info": {"copy_server_ids": ["456445523960791042"], "copy_channel_ids": ["461494200979030016"], "post_server_ids": ["455275822807252993"], "post_channel_ids": ["457811512296341515"]}, "memberlist": ["454205578537861121"], "wordlist": [], "case_sensitive_wordlist": true}

# try:
# 	filehandle = open(filename)
# 	filedata = json.load(filehandle)
# except Exception:
# 	pass
# else:
# 	if filedata["setup_info"]["copy_server_ids"] != None:
# 		copy_server_ids = filedata["setup_info"]["copy_server_ids"]
# 	if filedata["setup_info"]["copy_channel_ids"] != None:
# 		copy_channel_ids = filedata["setup_info"]["copy_channel_ids"]
# 	if filedata["setup_info"]["post_server_ids"] != None:
# 		post_server_ids = filedata["setup_info"]["post_server_ids"]
# 	if filedata["setup_info"]["post_channel_ids"] != None:
# 		post_channel_ids = filedata["setup_info"]["post_channel_ids"]
# 	if filedata["memberlist"] != None:
# 		memberlist = filedata["memberlist"]
# 	if filedata["wordlist"] != None:
# 		wordlist = filedata["wordlist"]
# 	if filedata["case_sensitive_wordlist"] != None:
# 		case_sensitive_wordlist = filedata["case_sensitive_wordlist"]
# 	filehandle.close()

commands_server_id_exists = False
commands_channel_id_exists = False

adding_copy_server = False
adding_copy_channel = False
adding_post_server = False
adding_post_channel = False

removing_copy_server = False
removing_copy_channel = False
removing_post_server = False
removing_post_channel = False

async def edit_check():

	global edit_msg_list

	await bot.wait_until_ready()
	while not bot.is_closed:
		await asyncio.sleep(0.1)
		for edit_msg in edit_msg_list:
			if edit_msg["copy_message_object"].content != edit_msg["message_content"]:
				try:
					await bot.edit_message(edit_msg["post_message_object"], new_content=text_message_filter(edit_msg["copy_message_object"].content))
					edit_msg_list[edit_msg_list.index(edit_msg)]["message_content"] = edit_msg["copy_message_object"].content
				except Exception:
					pass



def text_message_filter(original_message):

	global case_sensitive_wordlist
	global wordlist

	local_new_message = original_message
	if case_sensitive_wordlist:
		for word in wordlist:
			local_new_message = local_new_message.replace(word, "")
	else:
		lowercase_message = local_new_message.lower()
		new_letters = list(local_new_message)
		letter_index = 0
		uppercase_letter_indexes = []
		for letter in new_letters:
			if letter.isupper():
				uppercase_letter_indexes.append(letter_index)
			letter_index += 1
		del letter_index
		for word in wordlist:
			replacement_word = len(word) * "�"
			lowercase_message = lowercase_message.replace(word.lower(), replacement_word)
		lowercase_letters = list(lowercase_message)
		for letter_index in uppercase_letter_indexes:
			lowercase_letters[letter_index] = lowercase_letters[letter_index].upper()
		local_new_message = "".join(lowercase_letters)
		local_new_message = local_new_message.replace("�", "")
	return local_new_message

@bot.event
async def on_ready():
	await bot.wait_until_ready()

	global commands_server_id
	global commands_channel_id
	global commands_server_id_exists
	global commands_channel_id_exists

	commands_server_id = commands_server_id.strip()
	commands_channel_id = commands_channel_id.strip()

	if (len(commands_server_id) != 0):
			try:
				commands_server_object = bot.get_server(commands_server_id)
				print("Commands Server: {0} ({1})".format(commands_server_object.name, commands_server_object.id))
			except Exception:
				print("Exiting: Invalid commands_server_id ({0})".format(commands_server_id))
				time.sleep(5)
				raise SystemExit
			commands_server_id_exists = True
			if (len(commands_channel_id) != 0):
				try:
					commands_channel_object = bot.get_server(commands_server_id).get_channel(commands_channel_id)
					print("Commands Channel: {0} ({1})".format(commands_channel_object.name, commands_channel_object.id))
				except Exception:
					print("Exiting: Invalid commands_channel_id ({0})".format(commands_channel_id))
					time.sleep(5)
					raise SystemExit
				commands_channel_id_exists = True

	print (bot.user.name + " is ready")
	print ("ID: " + bot.user.id)

@bot.event
async def on_message(message):

	t0 = time.time()

	message_channel = message.channel

	global embed
	global edit_msg_list
	global edit_msg_list_length

	global copy_server_ids
	global copy_channel_ids
	global post_server_ids
	global post_channel_ids

	global commands_server_id
	global commands_channel_id
	global commands_server_id_exists
	global commands_channel_id_exists

	global adding_copy_server
	global adding_copy_channel
	global adding_post_server
	global adding_post_channel

	global removing_copy_server
	global removing_copy_channel
	global removing_post_server
	global removing_post_channel

	global memberlist
	global wordlist
	global case_sensitive_wordlist

	if message.author.id != bot.user.id:
		if ((not commands_server_id_exists) or (message.server.id == commands_server_id)) and ((not commands_channel_id_exists) or (message.channel.id == commands_channel_id)):

			# If block for all the commands.

			if (not adding_copy_server) and (not adding_copy_channel) and (not adding_post_server) and (not adding_post_channel) and (not removing_copy_server) and (not removing_copy_channel) and (not removing_post_server) and (not removing_post_channel):



				####################################################################################################
				####################################################################################################



				if (message.content[:12] == "!memberlist ") or (message.content == "!memberlist"):
					if (copy_server_ids != []) and (copy_channel_ids != []):

						#!MEMBERLIST ADD

						if (message.content[:16] == "!memberlist add ") or (message.content == "!memberlist add"):
							if (message.content[:20] == "!memberlist add all ") or (message.content == "!memberlist add all"):
								count = 0
								for copy_server_id in copy_server_ids:
									for member in bot.get_server(copy_server_id).members:
										if not (member.id in memberlist):
											memberlist.append(member.id)
											count += 1
								filedata["memberlist"] = memberlist		#SAVE TO FILE
								filehandle = open(filename, "w")
								json.dump(filedata, filehandle)
								filehandle.close()
								if count == 1:
									await bot.send_message(message_channel, """**[1] member was added to the memberlist.**""")
								else:
									await bot.send_message(message_channel, """**[{0}] members were added to the memberlist.**""".format(str(count)))
								del count
							else:
								temp_bool = True
								for copy_server_id in copy_server_ids:
									for member in bot.get_server(copy_server_id).members:
										if (message.content[16:] == member.name) or (message.content[16:] == member.id):
											if member.id in memberlist:
												await bot.send_message(message_channel, """**The member *{0} ({1})* is already in the memberlist.**
**Use the command *!memberlist* to see all the members who have their messages currently being copied.**
""".format(member.name, member.id))
											else:
												memberlist.append(member.id)
												filedata["memberlist"] = memberlist		#SAVE TO FILE
												filehandle = open(filename, "w")
												json.dump(filedata, filehandle)
												filehandle.close()
												await bot.send_message(message_channel, """**The member *{0} ({1})* has been added to the memberlist.**
""".format(member.name, member.id))
											temp_bool = False
											break
									if (not temp_bool):
										break
								if temp_bool:
									if message.content.strip()[:16] == "!memberlist add ":
										await bot.send_message(message_channel, """**Invalid member - does not exist**""")
									await bot.send_message(message_channel, """**Here are all the members in the copy servers.**
**Use the command *!memberlist add member* to add a member to the memberlist.**""")
									for copy_server_id in copy_server_ids:
										copy_server_object = bot.get_server(copy_server_id)
										await bot.send_message(message_channel, """**{0} ({1})**""".format(copy_server_object.name, copy_server_object.id))
										for member in copy_server_object.members:
											await bot.send_message(message_channel, """• {0} ({1})""".format(member.name, member.id))
								del temp_bool

						#!MEMBERLIST REMOVE

						elif (message.content[:19] == "!memberlist remove ") or (message.content == "!memberlist remove"):
							if len(memberlist) > 0:
								if (message.content[:23] == "!memberlist remove all ") or (message.content == "!memberlist remove all"):
									count = len(memberlist)
									memberlist = []
									filedata["memberlist"] = memberlist		#SAVE TO FILE
									filehandle = open(filename, "w")
									json.dump(filedata, filehandle)
									filehandle.close()
									if count == 1:
										await bot.send_message(message_channel, """**[1] member was removed from the memberlist.**""")
									else:
										await bot.send_message(message_channel, """**[{0}] members were removed from the memberlist.**""".format(str(count)))
									del count
								else:
									temp_bool = True
									for member_id in memberlist:
										for copy_server_id in copy_server_ids:
											try:
												member_object = bot.get_server(copy_server_id).get_member(member_id)
											except Exception:
												pass
											else:
												if (message.content[19:] == member_object.name) or (message.content[19:] == member_object.id):
													memberlist.remove(member_object.id)
													filedata["memberlist"] = memberlist		#SAVE TO FILE
													filehandle = open(filename, "w")
													json.dump(filedata, filehandle)
													filehandle.close()
													await bot.send_message(message_channel, """**The member *{0} ({1})* has been removed from the memberlist.**
""".format(member_object.name, member_object.id))
													temp_bool = False
													break
									if temp_bool:
										if message.content.strip()[:19] == "!memberlist remove ":
											await bot.send_message(message_channel, """**Invalid member - not in memberlist**""")
										await bot.send_message(message_channel, """**Here are all the members in the memberlist (the members who have their messages currently being copied).**
**Use the command *!memberlist remove member* to remove a member from the memberlist**""")
										for member_id in memberlist:
											for copy_server_id in copy_server_ids:
												try:
													member_object = bot.get_server(copy_server_id).get_member(member_id)
													await bot.send_message(message_channel, """• {0} ({1})""".format(member_object.name, member_object.id))
												except Exception:
													pass
									del temp_bool
							else:
								await bot.send_message(message_channel, """**There are currently no members in the memberlist.**
**For more commands on the memberlist, use the command *!help*.**""")

						#!MEMBERLIST

						else:
							if len(memberlist) > 0:
								await bot.send_message(message_channel, """**[MEMBERLIST]**

**These members are currently having their messages copied when they send a message in the copy channels in the copy servers.**
**For more commands on the memberlist, use the command *!help*.**""")
								for member_id in memberlist:
									for copy_server_id in copy_server_ids:
										try:
											member_object = bot.get_server(copy_server_id).get_member(member_id)
											await bot.send_message(message_channel, """• {0} ({1})""".format(member_object.name, member_object.id))
										except Exception:
											pass
							else:
								await bot.send_message(message_channel, """**There are no members currently in the memberlist.**
**For more commands on the memberlist, use the command *!help*.**""")



					else:
						await bot.send_message(message_channel, """**The server to copy from and the channel to copy from must be set up before the *!memberlist* command can be used.**""")



				####################################################################################################
				####################################################################################################



				elif (message.content[:10] == "!wordlist ") or (message.content == "!wordlist"):
					if (copy_server_ids != []) and (copy_channel_ids != []):

						#!WORDLIST ADD

						if (message.content[:14] == "!wordlist add ") or (message.content == "!wordlist add"):
							if (message.content.strip()[:14] == "!wordlist add "):
								if (message.content[14:] in wordlist) or ((not case_sensitive_wordlist) and (message.content[14:].lower() in wordlist)):
									if case_sensitive_wordlist:
										await bot.send_message(message_channel, """**The word *{0}* is already in the wordlist.**
**Use the command *!wordlist* to see all the words that are currently being removed from the copied messages.**""".format(message.content[14:]))
									else:
										await bot.send_message(message_channel, """**The word *{0}* is already in the wordlist.**
**Use the command *!wordlist* to see all the words that are currently being removed from the copied messages.**""".format(message.content[14:].lower()))
								else:
									if case_sensitive_wordlist:
										wordlist.append(message.content[14:])
										filedata["wordlist"] = wordlist		#SAVE TO FILE
										filehandle = open(filename, "w")
										json.dump(filedata, filehandle)
										filehandle.close()
										await bot.send_message(message_channel, """**The word *{0}* has been added to the wordlist.**""".format(message.content[14:]))
									else:
										wordlist.append(message.content[14:].lower())
										filedata["wordlist"] = wordlist		#SAVE TO FILE
										filehandle = open(filename, "w")
										json.dump(filedata, filehandle)
										filehandle.close()
										await bot.send_message(message_channel, """**The word *{0}* has been added to the wordlist.**""".format(message.content[14:].lower()))
							else:
								await bot.send_message(message_channel, """**Use the command *!wordlist add word* to add a member to the wordlist.**""")

						#!WORDLIST REMOVE

						elif (message.content[:17] == "!wordlist remove ") or (message.content == "!wordlist remove"):
							if len(wordlist) > 0:
								if (message.content[:21] == "!wordlist remove all ") or (message.content == "!wordlist remove all"):
									count = len(wordlist)
									wordlist = []
									filedata["wordlist"] = wordlist		#SAVE TO FILE
									filehandle = open(filename, "w")
									json.dump(filedata, filehandle)
									filehandle.close()
									if count == 1:
										await bot.send_message(message_channel, """**[1] word was removed from the wordlist.**""")
									else:
										await bot.send_message(message_channel, """**[{0}] words were removed from the wordlist.**""".format(str(count)))
									del count
								else:
									if (message.content[17:] in wordlist) or ((not case_sensitive_wordlist) and (message.content[17:].lower() in wordlist)):
										if case_sensitive_wordlist:
											wordlist.remove(message.content[17:])
											filedata["wordlist"] = wordlist		#SAVE TO FILE
											filehandle = open(filename, "w")
											json.dump(filedata, filehandle)
											filehandle.close()
											await bot.send_message(message_channel, """**The word *{0}* has been removed from the wordlist.**""".format(message.content[17:]))
										else:
											wordlist.remove(message.content[17:].lower())
											filedata["wordlist"] = wordlist		#SAVE TO FILE
											filehandle = open(filename, "w")
											json.dump(filedata, filehandle)
											filehandle.close()
											await bot.send_message(message_channel, """**The word *{0}* has been removed from the wordlist.**""".format(message.content[17:].lower()))
									else:
										if (message.content.strip()[:17] == "!wordlist remove "):
											await bot.send_message(message_channel, """**Invalid word - not in wordlist**""")
										await bot.send_message(message_channel, """**Here are all the words in the wordlist (the words that are currently being removed from the copied messages).**
**Use the command *!wordlist remove word* to remove a word from the wordlist**""")
										for word in wordlist:
											await bot.send_message(message_channel, """• {0}""".format(word))
							else:
								await bot.send_message(message_channel, """**There are currently no words in the wordlist.**
**For more commands on the wordlist, use the command *!help*.**""")

						#!WORDLIST TOGGLE CASE

						elif (message.content[:22] == "!wordlist toggle case ") or (message.content == "!wordlist toggle case"):
							if case_sensitive_wordlist:
								if len(wordlist) > 0:
									wordlist = list(word.lower() for word in wordlist)
									for word in wordlist:
										if wordlist.count(word) > 1:
											for x in range(wordlist.count(word) - 1):
												wordlist.remove(word)
								case_sensitive_wordlist = False
								filedata["wordlist"] = wordlist		#SAVE TO FILE
								filedata["case_sensitive_wordlist"] = case_sensitive_wordlist
								filehandle = open(filename, "w")
								json.dump(filedata, filehandle)
								filehandle.close()
								await bot.send_message(message_channel, """The wordlist is now case **insensitive**.""")
							else:
								case_sensitive_wordlist = True
								filedata["case_sensitive_wordlist"] = case_sensitive_wordlist		#SAVE TO FILE
								filehandle = open(filename, "w")
								json.dump(filedata, filehandle)
								filehandle.close()
								await bot.send_message(message_channel, """The wordlist is now case **sensitive**.""")

						#!WORDLIST

						elif (message.content[:10] == "!wordlist ") or (message.content == "!wordlist"):
							if len(wordlist) > 0:
								await bot.send_message(message_channel, """**[WORDLIST]**

**These words are currently being removed from the copied messages.**
**For more commands on the wordlist, use the command *!help*.**""")
								for word in wordlist:
									await bot.send_message(message_channel, """• {0} """.format(word))
							else:
								await bot.send_message(message_channel, """**There are no words currently in the wordlist.**
**For more commands on the wordlist, use the command *!help*.**""")



					else:
						await bot.send_message(message_channel, """**The server to copy from and the channel to copy from must be set up before the *!wordlist* command can be used.**""")



				####################################################################################################
				####################################################################################################



				elif (message.content[:5] == "!add ") or (message.content == "!add"):
					if (message.content[:17] == "!add copy server ") or (message.content == "!add copy server"):
						temp_bool = False
						for server_object in bot.servers:
							if not (server_object.id in copy_server_ids):
								temp_bool = True
						if temp_bool:
							for server_object in bot.servers:
								if not (server_object.id in copy_server_ids):
									temp_bool
							await bot.send_message(message_channel, """**[ADDING COPY SERVER]**

**Type one of these servers to add them to the copy server list.**""")
							for server_object in bot.servers:
								if not (server_object.id in copy_server_ids):
									await bot.send_message(message_channel, """• {0} ({1})""".format(server_object.name, server_object.id))
							adding_copy_server = True
						else:
							await bot.send_message(message_channel, """**All the servers I'm in are already in the copy server list.**""")


					elif (message.content[:18] == "!add copy channel ") or (message.content == "!add copy channel"):
						temp_bool = False
						for copy_server_id in copy_server_ids:
							server_object = bot.get_server(copy_server_id)
							for channel_object in server_object.channels:
								if (not (channel_object.id in copy_channel_ids)) and (str(channel_object.type) == "text"):
									temp_bool = True
						if temp_bool:
							await bot.send_message(message_channel, """**[ADDING COPY CHANNEL]**

**Type one of these channels to add them to the copy channel list.**""")
							for server_object in bot.servers:
								if server_object.id in copy_server_ids:
									await bot.send_message(message_channel, """**{0} ({1})**""".format(server_object.name, server_object.id))
									for channel_object in server_object.channels:
										if (not (channel_object.id in copy_channel_ids)) and (str(channel_object.type) == "text"):
											await bot.send_message(message_channel, """• {0} ({1})""".format(channel_object.name, channel_object.id))
							adding_copy_channel = True
						else:
							await bot.send_message(message_channel, """**All the channels I'm in are already in the copy channel list.**""")


					elif (message.content[:17] == "!add post server ") or (message.content == "!add post server"):
						temp_bool = False
						for server_object in bot.servers:
							if not (server_object.id in post_server_ids):
								temp_bool = True
						if temp_bool:
							await bot.send_message(message_channel, """**[ADDING POST SERVER]**

**Type one of these servers to add them to the post server list.**""")
							for server_object in bot.servers:
								if not (server_object.id in post_server_ids):
									await bot.send_message(message_channel, """• {0} ({1})""".format(server_object.name, server_object.id))
							adding_post_server = True
						else:
							await bot.send_message(message_channel, """**All the servers I'm in are already in the post server list.**""")


					elif (message.content[:18] == "!add post channel ") or (message.content == "!add post channel"):
						temp_bool = False
						for post_server_id in post_server_ids:
							server_object = bot.get_server(post_server_id)
							for channel_object in server_object.channels:
								if (not (channel_object.id in post_channel_ids)) and (str(channel_object.type) == "text"):
									temp_bool = True
						if temp_bool:
							await bot.send_message(message_channel, """**[ADDING POST CHANNEL]**

**Type one of these channels to add them to the post channel list.**""")
							for server_object in bot.servers:
								if server_object.id in post_server_ids:
									await bot.send_message(message_channel, """**{0} ({1})**""".format(server_object.name, server_object.id))
									for channel_object in server_object.channels:
										if (not (channel_object.id in post_channel_ids)) and (str(channel_object.type) == "text"):
											await bot.send_message(message_channel, """• {0} ({1})""".format(channel_object.name, channel_object.id))
							adding_post_channel = True
						else:
							await bot.send_message(message_channel, """**All the channels I'm in are already in the post channel list.**""")


					else:
						await bot.send_message(message_channel, """**Use *!add* like this:**

• *!add copy server* : Adds a server to copy from.
• *!add copy channel* : Adds a channel (in the copy servers) to copy from.
• *!add post server* : Adds a server to post to.
• *!add post channel* : Adds a channel (in the post servers) to post to.
""")



				####################################################################################################
				####################################################################################################



				elif (message.content[:8] == "!remove ") or (message.content == "!remove"):
					if (message.content[:20] == "!remove copy server ") or (message.content == "!remove copy server"):
						if len(copy_server_ids) > 0:
							await bot.send_message(message_channel, """**[REMOVING COPY SERVER]**

**Type one of these servers to remove them from the copy server list.**""")
							for copy_server_id in copy_server_ids:
								server_object = bot.get_server(copy_server_id)
								await bot.send_message(message_channel, """• {0} ({1})""".format(server_object.name, server_object.id))
							removing_copy_server = True
						else:
							await bot.send_message(message_channel, """**There are currently no copy servers.**""")



					elif (message.content[:21] == "!remove copy channel ") or (message.content == "!remove copy channel"):
						if len(copy_channel_ids) > 0:
							await bot.send_message(message_channel, """**[REMOVING COPY CHANNEL]**

**Type one of these channels to remove them from the copy channel list.**""")
							for copy_server_id in copy_server_ids:
								server_object = bot.get_server(copy_server_id)
								temp_bool = False
								for channel_object in server_object.channels:
									if channel_object.id in copy_channel_ids:
										temp_bool = True
								if temp_bool:
									await bot.send_message(message_channel, """**{0} ({1})**""".format(server_object.name, server_object.id))
								for channel_object in server_object.channels:
									if channel_object.id in copy_channel_ids:
										await bot.send_message(message_channel, """• {0} ({1})""".format(channel_object.name, channel_object.id))
							removing_copy_channel = True
						else:
							await bot.send_message(message_channel, """**There are currently no copy channels.**""")



					elif (message.content[:20] == "!remove post server ") or (message.content == "!remove post server"):
						if len(post_server_ids) > 0:
							await bot.send_message(message_channel, """**[REMOVING POST SERVER]**

**Type one of these servers to remove them from the post server list.**""")
							for post_server_id in post_server_ids:
								server_object = bot.get_server(post_server_id)
								await bot.send_message(message_channel, """• {0} ({1})""".format(server_object.name, server_object.id))
							removing_post_server = True
						else:
							await bot.send_message(message_channel, """**There are currently no post servers.**""")



					elif (message.content[:21] == "!remove post channel ") or (message.content == "!remove post channel"):
							if len(post_channel_ids) > 0:
								await bot.send_message(message_channel, """**[REMOVING POST CHANNEL]**

**Type one of these channels to remove them from the post channel list.**""")
								for post_server_id in post_server_ids:
									server_object = bot.get_server(post_server_id)
									temp_bool = False
									for channel_object in server_object.channels:
										if channel_object.id in post_channel_ids:
											temp_bool = True
									if temp_bool:
										await bot.send_message(message_channel, """**{0} ({1})**""".format(server_object.name, server_object.id))
									for channel_object in server_object.channels:
										if channel_object.id in post_channel_ids:
											await bot.send_message(message_channel, """• {0} ({1})""".format(channel_object.name, channel_object.id))
								removing_post_channel = True
							else:
								await bot.send_message(message_channel, """**There are currently no post channels.**""")



					else:
						await bot.send_message(message_channel, """**Use *!remove* like this:**

• *!remove copy server* : Removes a copy server.
• *!remove copy channel* : Removes a copy channel.
• *!remove post server* : Removes a post server.
• *!remove post channel* : Removes a post channel.
""")


				####################################################################################################
				####################################################################################################

				elif (message.content[:6] == "!help ") or (message.content == "!help"):
					await bot.send_message(message_channel, """**[COMMANDS]**

• *!memberlist* : Shows you all the members currently in the memberlist.
• *!memberlist add member* : Adds a member from the copy server to the memberlist.
• *!memberlist add all* : Adds all the members from the copy server to the memberlist.
• *!memberlist remove member* : Removes a member from the memberlist.
• *!memberlist remove all* : Removes all the members from the memberlist.

• *!wordlist* : Shows all the words currently in the wordlist.
• *!wordlist add word* : Adds a word to the wordlist.
• *!wordlist remove word* : Removes a word from the wordlist .
• *!wordlist remove all* : Removes all the words from the wordlist.
• *!wordlist toggle case* : Toggles between case insensitive and case sensitive.

• *!add* : Shows the commands for adding copy/post servers/channels.
• *!remove* : Shows the commands for removing copy/post servers/channels.
""")


				####################################################################################################
				####################################################################################################



			elif adding_copy_server:
				temp_bool = True
				for server_object in bot.servers:
					if (message.content == server_object.name) or (message.content == server_object.id):
						if server_object.id in copy_server_ids:
							await bot.send_message(message_channel, """**Invalid server - already a copy server.**""")
						else:
							copy_server_ids.append(server_object.id)
							filedata["setup_info"]["copy_server_ids"] = copy_server_ids		#SAVE TO FILE
							filehandle = open(filename, "w")
							json.dump(filedata, filehandle)
							filehandle.close()
							await bot.send_message(message_channel, """**The copy server *{0} ({1})* has been added.**""".format(server_object.name, server_object.id))
							adding_copy_server = False
						temp_bool = False
						break
				if adding_copy_server and temp_bool:
					await bot.send_message(message_channel, """**Invalid server - does not exist.**""")



			elif adding_copy_channel:
				temp_bool = True
				for server_id in copy_server_ids:
					for channel_object in bot.get_server(server_id).channels:
						if (message.content == channel_object.name) or (message.content == channel_object.id):
							if channel_object.id in copy_channel_ids:
								await bot.send_message(message_channel, """**Invalid channel - already a copy channel.**""")
							else:
								copy_channel_ids.append(channel_object.id)
								filedata["setup_info"]["copy_channel_ids"] = copy_channel_ids		#SAVE TO FILE
								filehandle = open(filename, "w")
								json.dump(filedata, filehandle)
								filehandle.close()
								await bot.send_message(message_channel, """**The copy channel *{0} ({1})* has been added.**""".format(channel_object.name, channel_object.id))
								adding_copy_channel = False
							temp_bool = False
							break
				if adding_copy_channel and temp_bool:
					await bot.send_message(message_channel, """**Invalid channel - does not exist.**""")



			elif adding_post_server:
				temp_bool = True
				for server_object in bot.servers:
					if (message.content == server_object.name) or (message.content == server_object.id):
						if server_object.id in post_server_ids:
							await bot.send_message(message_channel, """**Invalid server - already a post server.**""")
						else:
							post_server_ids.append(server_object.id)
							filedata["setup_info"]["post_server_ids"] = post_server_ids		#SAVE TO FILE
							filehandle = open(filename, "w")
							json.dump(filedata, filehandle)
							filehandle.close()
							await bot.send_message(message_channel, """**The post server *{0} ({1})* has been added.**""".format(server_object.name, server_object.id))
							adding_post_server = False
						temp_bool = False
						break
				if adding_post_server and temp_bool:
					await bot.send_message(message_channel, """**Invalid server - does not exist.**""")



			elif adding_post_channel:
				temp_bool = True
				for server_id in post_server_ids:
					for channel_object in bot.get_server(server_id).channels:
						if (message.content == channel_object.name) or (message.content == channel_object.id):
							if channel_object.id in post_channel_ids:
								await bot.send_message(message_channel, """**Invalid channel - already a post channel.**""")
							else:
								post_channel_ids.append(channel_object.id)
								filedata["setup_info"]["post_channel_ids"] = post_channel_ids		#SAVE TO FILE
								filehandle = open(filename, "w")
								json.dump(filedata, filehandle)
								filehandle.close()
								await bot.send_message(message_channel, """**The post channel *{0} ({1})* has been added.**""".format(channel_object.name, channel_object.id))
								adding_post_channel = False
							temp_bool = False
							break
				if adding_post_channel and temp_bool:
					await bot.send_message(message_channel, """**Invalid channel - does not exist.**""")






			elif removing_copy_server:
				for server_object in bot.servers:
					if (message.content == server_object.name) or (message.content == server_object.id):
						if server_object.id in copy_server_ids:
							copy_server_ids.remove(server_object.id)
							filedata["setup_info"]["copy_server_ids"] = copy_server_ids		#SAVE TO FILE
							filehandle = open(filename, "w")
							json.dump(filedata, filehandle)
							filehandle.close()
							await bot.send_message(message_channel, """**The copy server *{0} ({1})* has been removed.**""".format(server_object.name, server_object.id))
							removing_copy_server = False
				if removing_copy_server:
					await bot.send_message(message_channel, """**Invalid server - not a copy server.**""")



			elif removing_copy_channel:
				for server_object in bot.servers:
					for channel_object in server_object.channels:
						if (message.content == channel_object.name) or (message.content == channel_object.id):
							if channel_object.id in copy_channel_ids:
								copy_channel_ids.remove(channel_object.id)
								filedata["setup_info"]["copy_channel_ids"] = copy_channel_ids		#SAVE TO FILE
								filehandle = open(filename, "w")
								json.dump(filedata, filehandle)
								filehandle.close()
								await bot.send_message(message_channel, """**The copy channel *{0} ({1})* has been removed.**""".format(channel_object.name, channel_object.id))
								removing_copy_channel = False
				if removing_copy_channel:
					await bot.send_message(message_channel, """**Invalid channel - not a copy channel.**""")



			elif removing_post_server:
				for server_object in bot.servers:
					if (message.content == server_object.name) or (message.content == server_object.id):
						if server_object.id in post_server_ids:
							post_server_ids.remove(server_object.id)
							filedata["setup_info"]["post_server_ids"] = post_server_ids		#SAVE TO FILE
							filehandle = open(filename, "w")
							json.dump(filedata, filehandle)
							filehandle.close()
							await bot.send_message(message_channel, """**The post server *{0} ({1})* has been removed.**""".format(server_object.name, server_object.id))
							removing_post_server = False
				if removing_post_server:
					await bot.send_message(message_channel, """**Invalid server - not a post server.**""")



			elif removing_post_channel:
				for server_object in bot.servers:
					for channel_object in server_object.channels:
						if (message.content == channel_object.name) or (message.content == channel_object.id):
							if channel_object.id in post_channel_ids:
								post_channel_ids.remove(channel_object.id)
								filedata["setup_info"]["post_channel_ids"] = post_channel_ids		#SAVE TO FILE
								filehandle = open(filename, "w")
								json.dump(filedata, filehandle)
								filehandle.close()
								await bot.send_message(message_channel, """**The post channel *{0} ({1})* has been removed.**""".format(channel_object.name, channel_object.id))
								removing_post_channel = False
				if removing_post_channel:
					await bot.send_message(message_channel, """**Invalid channel - not a post channel.**""")

		# Checks if the message being sent is in the copy server and in the copy channel,
		# and if it is, then it posts that same message to the post server.

		if message.server.id in copy_server_ids:
			if message.channel.id in copy_channel_ids:
				if (message.author.id in memberlist) or (not(message.author in message.server.members)):
					if (message.content).strip() != "":
						for post_server_id in post_server_ids:
							for post_channel_id in post_channel_ids:
								server_object = bot.get_server(post_server_id)
								channel_object = server_object.get_channel(post_channel_id)
								if channel_object in server_object.channels:
									if len(edit_msg_list) > 0:
										for x in range(len(edit_msg_list)):
											if (x == 0) and (len(edit_msg_list) != edit_msg_list_length):
												edit_msg_list.append(edit_msg_list[len(edit_msg_list) - 1])
											else:
												edit_msg_list[len(edit_msg_list) - 1 - x] = edit_msg_list[len(edit_msg_list) - 2 - x]
										edit_msg_list[0] = {"copy_message_object" : message,
															"post_message_object" : None,
															"message_content" : message.content,
															"message_type" : "text"}
									else:
										edit_msg_list.append({"copy_message_object" : message,
															"post_message_object" : None,
															"message_content" : message.content,
															"message_type" : "text"})

									new_message = text_message_filter(message.content)
									edit_msg_list[0]["post_message_object"] = await bot.send_message(channel_object, new_message)

					if message.attachments != []:
						for attachment in message.attachments:
							for post_server_id in post_server_ids:
								for post_channel_id in post_channel_ids:
									server_object = bot.get_server(post_server_id)
									channel_object = server_object.get_channel(post_channel_id)
									if channel_object in server_object.channels:
										await bot.send_message(channel_object, attachment["url"])
					if message.embeds != []:

						for embed_info in message.embeds:
							if ("title" in embed_info) and ("url" in embed_info) and ("description" in embed_info) and ("color" in embed_info):
								embed=discord.Embed(title=embed_info["title"], url=embed_info["url"], description=embed_info["description"], color=embed_info["color"])
							elif ("title" in embed_info) and ("url" in embed_info) and ("description" in embed_info):
								embed=discord.Embed(title=embed_info["title"], url=embed_info["url"], description=embed_info["description"])
							elif ("title" in embed_info) and ("url" in embed_info) and ("color" in embed_info):
								embed=discord.Embed(title=embed_info["title"], url=embed_info["url"], color=embed_info["color"])
							elif ("title" in embed_info) and ("description" in embed_info) and ("color" in embed_info):
								embed=discord.Embed(title=embed_info["title"], description=embed_info["description"], color=embed_info["color"])
							elif ("url" in embed_info) and ("description" in embed_info) and ("color" in embed_info):
								embed=discord.Embed(url=embed_info["url"], description=embed_info["description"], color=embed_info["color"])
							elif ("title" in embed_info) and ("url" in embed_info):
								embed=discord.Embed(title=embed_info["title"], url=embed_info["url"])
							elif ("title" in embed_info) and ("description" in embed_info):
								embed=discord.Embed(title=embed_info["title"], description=embed_info["description"])
							elif ("title" in embed_info) and ("color" in embed_info):
								embed=discord.Embed(title=embed_info["title"], color=embed_info["color"])
							elif ("url" in embed_info) and ("description" in embed_info):
								embed=discord.Embed(url=embed_info["url"], description=embed_info["description"])
							elif ("url" in embed_info) and ("color" in embed_info):
								embed=discord.Embed(url=embed_info["url"], color=embed_info["color"])
							elif ("description" in embed_info) and ("color" in embed_info):
								embed=discord.Embed(description=embed_info["description"], color=embed_info["color"])
							elif ("title" in embed_info):
								embed=discord.Embed(title=embed_info["title"])
							elif ("url" in embed_info):
								embed=discord.Embed(url=embed_info["url"])
							elif ("description" in embed_info):
								embed=discord.Embed(description=embed_info["description"])
							elif ("color" in embed_info):
								embed=discord.Embed(color=embed_info["color"])
							else:
								embed=discord.Embed()


							if "thumbnail" in embed_info:
								embed.set_thumbnail(url=embed_info["thumbnail"]["url"])


							if "fields" in embed_info:
								for embed_field in embed_info["fields"]:
									embed.add_field(name=embed_field["name"], value=embed_field["value"], inline=embed_field["inline"])


							if "footer" in embed_info:
								embed.set_footer(text=embed_info["footer"]["text"])

							for post_server_id in post_server_ids:
								for post_channel_id in post_channel_ids:
									server_object = bot.get_server(post_server_id)
									channel_object = server_object.get_channel(post_channel_id)
									if channel_object in server_object.channels:
										await bot.send_message(channel_object, embed=embed)


					print("Time taken: " + str(time.time() - t0))

bot.loop.create_task(edit_check())
bot.run(token, bot=(not selfbot))
