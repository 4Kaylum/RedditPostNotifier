import praw
import OAuth2Util
import time
import os
from postNotifierTools import *

## Set some constants
print('Opened.')
emList = os.path.dirname(os.path.realpath(__file__)) + '\\emailList.txt'
r = praw.Reddit(user_agent="A user to message out to a list of [registered] when there's a new chapter to Magic Muggle - /u/SatanistSnowflake")

## Auth the bot to /u/magicSquib
print('Logging in...')
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)
print('Logged in.')

justJoined    = "You've been added to the message list!\n\nIf you want to be removed, [click here!](https://www.reddit.com/message/compose/?to=magicSquib&subject=[REMOVE]&message=User list user update.)"
justLeft      = "You've been removed from the message list!\n\nIf you want to be added, [click here!](https://www.reddit.com/message/compose/?to=magicSquib&subject=[ADD]&message=User list user update.)"
alreadyJoined = "You're already on the message list! You silly :3\n\nIf you want to be removed, [click here!](https://www.reddit.com/message/compose/?to=magicSquib&subject=[REMOVE]&message=User list user update.)"
alreadyLeft   = "You're not on the message list! You silly :3\n\nIf you want to be added, [click here!](https://www.reddit.com/message/compose/?to=magicSquib&subject=[ADD]&message=User list user update.)"
disclaimer    = "\n\n---\n\n^^I ^^am ^^a ^^bot, ^^*bleep, ^^bloop.* ^^All ^^body ^^text ^^apart ^^from ^^this ^^disclaimer ^^was ^^written ^^by ^^{}.  \n^^[Author](/u/SatanistSnowflake) ^^:: ^^[Git](https://github.com/4Kaylum/RedditPostNotifier)"

## Main event loop
while True:

	changeFlag = False

	## Go through unread messages.
	print('\nGoing through messages...')
	for msg in r.get_unread(limit=None):

		## Print the subject to console.
		print('\nMessage subject line :: {}'.format(msg.subject))

		## Get the users who are already on the message list
		currentUsers = getFileList(emList)

		## Checks to add to the list
		if checkStartWith(msg, '[add]'):
			print("    Identified :: ADD :: {}".format(msg.author.name))
			if msg.author.name in currentUsers:
				print("    Already on list. Aborting.")
				print("    Sending message.")
				msg.reply(alreadyJoined)
			else:
				print("    Not on list. Adding.")
				changeFlag = True
				currentUsers.append(msg.author.name)
				print("    Sending message.")
				msg.reply(justJoined)

		## Checks to rem from the list
		if checkStartWith(msg, '[remove]'):
			print("    Identified :: REMOVE :: {}".format(msg.author.name))
			if msg.author.name in currentUsers:
				print("    Already on list. Removing.")
				changeFlag = True
				currentUsers.remove(msg.author.name)
				print("    Sending message.")
				msg.reply(justLeft)
			else:
				print("    Not on list. Aborting.")
				print("    Sending message.")
				msg.reply(alreadyLeft)

		## Checks to send out message
		if checkStartWith(msg, '[send message]'):
			print("    Identified :: SEND MESSAGE :: {}".format(msg.author.name))
			if str(msg.author.name) in ['SatanistSnowflake', 'Doomchicken7']:
				print("    Author allowed. Sending messages out.")
				for i in currentUsers:
					print("        Sending message :: {}".format(i))
					r.send_message(i, "New Magic Muggle chapter!", msg.body + '\n\n' + disclaimer.format(str(msg.author.name)))
			else:
				print("    Author not allowed. Aborting.")

		## Checks to post a comment
		if checkStartWith(msg, '[comment]'):
			print("    Identified :: COMMENT :: {}".format(msg.author.name))
			if str(msg.author.name) in ['SatanistSnowflake']:
				print("    Author allowed. Proceeding to make comment.")

				## Split the ID of the comment to respond to and the text
				commentMake = msg.body.split('\n\n',1)
				toCommentOn = r.get_submission(url=commentMake[0])
				try:
					toCommentOn = toCommentOn.comments[0]
				except:
					pass
				toCommentWith = commentMake[1]

				if type(toCommentOn) == praw.objects.Comment:
					print("    Identified ID. Comment.\nPosting.")
					toCommentOn.reply(toCommentWith)
				elif type(toCommentOn) == praw.objects.Submission:
					print("    Identified ID. Submission.\nPosting.")
					toCommentOn.add_comment(toCommentWith)
				else:
					print("    ID was invalid. Aborting.")
			else:
				print("    Author not allowed. Aborting.")

		print("Marking message as read.")
		msg.mark_as_read()

	if changeFlag:
		print("\nWriting changes to file.")
		writeToFile(currentUsers, emList)

	print("\nSleeping for 30 seconds.")
	time.sleep(30)

