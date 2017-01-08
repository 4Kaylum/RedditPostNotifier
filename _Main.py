from praw import Reddit
import responses
from postnotifier import PostNotifier
from os.path import realpath, dirname
workingDirectory = dirname(realpath(__file__))


if __name__ == '__main__':
	r = Reddit('magicSquib')
	p = PostNotifier(r, workingDirectory)
	p.run()
