import os

test = 0

def run(**args):
	print("[*] In environment module.")
	return str(os.environ)