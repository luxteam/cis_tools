import argparse
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
from shutil import copyfile
import PIL.ImageGrab as IG
from subprocess import Popen


def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--tool', required=True)
	parser.add_argument('--scene', required=True)
	parser.add_argument('--pass_limit', required=True)
	parser.add_argument('--sceneName', required=True)

	args = parser.parse_args()
	
	with open("redshift_cmd_render.py") as f:
		py_template = f.read()

	args.sceneName = os.path.basename(args.sceneName)

	pyScript = py_template.format(scene = args.scene, pass_limit = args.pass_limit, scene_name = args.sceneName)

	with open('redshift_cmd_render.py', 'w') as f:
		f.write(pyScript)

	if not os.path.exists('Output'):
		os.makedirs('Output')
		
	mayapy = "C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\mayapy.exe".format(tool=args.tool)
	params = [mayapy]
	params += ["redshift_cmd_render.py"]

	p = Popen(params)
	stdout, stderr = p.communicate()


if __name__ == "__main__":
	main()
