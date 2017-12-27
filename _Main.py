from praw import Reddit
from postnotifier import PostNotifier
from os.path import realpath, dirname


if __name__ == '__main__':
	r = Reddit('magicSquib')
	p = PostNotifier(r, './database.json')
	p.run()
	# p.database.close()
