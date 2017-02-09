# Message to go at the bottom of all automated responses
BOTDISCLAIMERMESSAGE = '''\n\n---\n\n^^I ^^am ^^a ^^bot, ^^*bleep*, ^^*bloop.* ^^This ^^action ^^was ^^performed ^^automatically.  \n^^[Author](/u/SatanistSnowflake) ^^:: ^^[Git](https://github.com/4Kaylum/RedditPostNotifier)'''

# Message to be sent when the bot is sent a message that isn't nicely formatted or made
INVALIDMESSAGETOBOT = '''Sorry, but it looks like the message you sent is invalid.

This bot has several actions, many of which ~~are pretty neat~~ can be seen below:

Command|Example Subject|Example Body|Description
:------|:--------------|:-----------|:----------
ADD|ADD::AskReddit||If you run this command, you will be added to the messaging list for a given subreddit, and will thus recieve a message when this subreddit sends out an update message.
REMOVE|REMOVE::AskReddit||Running this command will remove you from a given subreddit's mailing list.
SEND|SEND::AskReddit New Rules!|There has been a rules update. Check it out.|This will send a message to everyone on the mailing list for the mentioned subreddit, with the anything past the command in the subject being parsed as the subject for the output message. This will only work if you are a moderator of the subreddit you are mentioning.
DISCORD|DISCORD::AskReddit|https://discordapp.com/api/webhooks/...|A Discord webhook link so that different updates will post into your Discord channel.

This bot will not be able to parse a response to this message, so thus you will have to make a completely new message should you wish you correct any mistakes you made in sending this initially.

Have a nice day! c:''' + BOTDISCLAIMERMESSAGE

# Message to be sent with you're added to a mailing list
# Formats :: subreddit name
ADDEDTOMAILINGLIST = '''You have successfully been added to the mailing list for the server **{}**!

It should be noted that just because you've been added, it doesn't mean that you've set up the message properly, or that you'll  ever recieve any messages.

Regardless, I hope that everything was a pleasant experience for you!''' + BOTDISCLAIMERMESSAGE

# Message to be sent when you're removed from a mailing list
# Formats :: subreddit name
REMOVEDFROMMAILINGLIST  = '''You have successfully been removed from the mailing list for the subreddit **{}**.

I hope that everything was a pleasant experience for you!''' + BOTDISCLAIMERMESSAGE

# Message to be sent when you aren't permitted to send out a message
# Formats :: subreddit name
NOTALLOWEDTOSEND = '''You just tried to send a message out to all signed up users for the subreddit **{}**. Unfortunately, you are not a moderator with this permission.

If this is an action you would like to perform, you need to be a moderator of the subreddit you are trying to send out to.

I apologise for any inconvenience.''' + BOTDISCLAIMERMESSAGE

# Message to be sent when the user is permitted to send the message
# Formats :: subreddit name
ABOUTTOBESENT = '''You are a moderator of the **{}** subreddit, and thus you are allowed to send a message to all of the signed up users for the subreddit. 

This may take a while, so don't panic if you don't recieve a message immediately.

Thank you for using PostNotifier.''' + BOTDISCLAIMERMESSAGE

# The ping back to the user when they set a new webhook for Discord
# Formats :: subreddit name
DISCORDWEBHOOKMESSAGE = '''You are a moderator of the **{}** subreddit, and thus you are allowed to run this command.

Doing this will set and save a webhook that will be pinged with information when certain actions happen with the bot, such as when a message is sent or when a user signs up.

A test ping has been sent out to the given webhook now. If you did not recieve anything, then please check and reset your webhook in the bot.

Thank you for using PostNotifier.''' + BOTDISCLAIMERMESSAGE
