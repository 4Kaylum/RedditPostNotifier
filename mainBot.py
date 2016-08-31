import praw
import OAuth2Util
import time
import os

print('Opened.')
emList = os.path.dirname(os.path.realpath(__file__)) + '\\emailList.txt'
r = praw.Reddit(user_agent="A bot to email out when there's a new chapter to Magic Muggle")

print('Logging in...')
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)
print('Logged in.\n')

while True:
	print('Going through messages...')
	for msg in r.get_unread(limit=None):
		print('Message subject line :: {}'.format(msg.subject))

		if msg.subject.lower().startswith("[add]"):
			print('Identified - add to list.')
			with open(emList) as a:
				peopleOnThere = a.read()
				peopleOnThere = peopleOnThere.split('\n')
				print(peopleOnThere)
			
			if msg.author.name in peopleOnThere:
				print('Already on list.')
				msg.reply("You're already on the message list! You silly :3\n\nIf you want to be removed, [click here!](https://www.reddit.com/message/compose/?to=magicSquib&subject=[REMOVE]&message=User list user update.)")
				print('Replied to user.')
			else:
				with open(emList,'a') as a:
					a.write('{}\n'.format(msg.author.name))
				print('Added to list.')
				msg.reply("You've been added to the message list!\n\nIf you want to be removed, [click here!](https://www.reddit.com/message/compose/?to=magicSquib&subject=[REMOVE]&message=User list user update.)")
				print('Replied to user.')
		
		elif msg.subject.lower().startswith("[remove]"):
			print('Identified - remove from list.')
			with open(emList) as a:
				peopleOnThere = a.read()
				peopleOnThere = peopleOnThere.split('\n')
				print(peopleOnThere)

			try:
				peopleOnThere.remove(msg.author.name)
				print('Removed from list.')
				qwe = ''
				for i in peopleOnThere:
					qwe = qwe + i + '\n'
				with open(emList,'w') as a:
					a.write(qwe)
				msg.reply("You've been removed from the message list!\n\nIf you want to be removed, [click here!](https://www.reddit.com/message/compose/?to=magicSquib&subject=[ADD]&message=User list user update.)")
				print('Replied to user.')
			except ValueError:
				print('Not on list.')
				msg.reply("You're not on the message list! You silly :3\n\nIf you want to be added, [click here!](https://www.reddit.com/message/compose/?to=magicSquib&subject=[ADD]&message=User list user update.)")
				print('Replied to user.')

		elif msg.subject.lower().startswith("[send message]") and str(msg.author) in ['SatanistSnowflake','Doomchicken7']:
			with open(emList) as a:
				print('Outward message send detected. Initiating...')
				peopleOnThere = a.read()
				peopleOnThere = peopleOnThere.split('\n')
				print(peopleOnThere)

			for i in peopleOnThere:
				if i == '':
					pass
				else:
					print('    Messaging {}...'.format(i))
					r.send_message(i,"New Magic Muggle chapter!","Check it out! \n\n/r/MagicMuggle")
					print('    Sent!')

		print('Marking as read...')
		msg.mark_as_read()
		print('Marked.\n')

	print('Sleeping for 10 seconds...\n')
	time.sleep(10)

# r.send_message('user', 'Subject Line', 'You are awesome!')
