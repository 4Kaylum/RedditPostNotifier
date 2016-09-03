def checkStartWith(msg, startString):
	msSubj = msg.subject.lower()
	if msSubj.startswith(startString.lower()):
		return True 
	return False 


def writeToFile(usrList, filename):
	toWrite = '\n'.join(usrList)
	with open(filename, 'w') as a:
		a.write(toWrite)


def getFileList(filename):
	with open(filename) as a:
		ret = a.read()
	ret = ret.split('\n')
	for z in range(3):
		for i, item in enumerate(ret):
			if item == '':
				del ret[i]
	return ret 


def thing():
	pass	