import os
import json
import argparse
import subprocess
import psutil
import platform
import logging


# logging
logging.basicConfig(filename="output.log", level=logging.INFO)
logger = logging.getLogger()


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--filename')
	args = parser.parse_args()

	# read manifest
	with open('manifest.json') as f:
		manifest = json.load(f)
		
	# parse scene name
	system_pl = platform.system()
	timeout = manifest[system_pl]["timeout"]
	output = manifest[system_pl]["output"]
	run = manifest[system_pl]["run"]

	before_files = os.listdir()
	# execute
	for r in run:
		p = psutil.Popen(r, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		try:
			stdout, stderr = p.communicate(timeout=timeout)
		except (subprocess.TimeoutExpired, psutil.TimeoutExpired) as err:
			try:
				for child in reversed(p.children(recursive=True)):
					child.terminate()
				p.terminate()
			except Exception as ex:
				print(ex)

		with open("output.log", 'w', encoding='utf-8') as file:
			stdout = stdout.decode("utf-8")
			file.write(stdout)

		with open("output.log", 'a', encoding='utf-8') as file:
			file.write("\n ----STDERR---- \n")
			stderr = stderr.decode("utf-8")
			file.write(stderr)


	after_files = os.listdir()
	diff_files = list(set(before_files) - set(after_files))

	if not os.path.exists('Output'):
		os.makedirs('Output')

	for f in diff_files:
		os.rename(diff_files, os.path.join("Output", diff_files))

	# pack zip
	zip_name = "ResultsPack_{}.zip".format(filename)	
	st = psutil.Popen('7z a "{}" ./"{}"/*'.format(zip_name, "Output"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	st.communicate()
	
	print(zip_name)
	
if __name__ == "__main__":
	try:
		main()
	except:
		exit(1)