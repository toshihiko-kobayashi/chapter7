import os

test = 0

def run():
	
	print("[*] In dirlister module.")
	files = os.listdir(".")
	
	return str(files)
