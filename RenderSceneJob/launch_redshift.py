import argparse
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
from shutil import copyfile
import PIL.ImageGrab as IG


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
		
	cmdRun = '''
	"C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\mayapy.exe" redshift_cmd_render.py
	'''.format(tool=args.tool)

	with open('launch_conversion.bat', 'w') as f:
		f.write(cmdRun)

	p = psutil.Popen('launch_render.bat', stdout=subprocess.PIPE)
	rc = -1

	try:
		rc = p.wait(timeout=100)
	except psutil.TimeoutExpired as err:
		rc = -1
		for child in reversed(p.children(recursive=True)):
			child.terminate()
		p.terminate()

	return rc


if __name__ == "__main__":
	rc = main()
	exit(rc)
