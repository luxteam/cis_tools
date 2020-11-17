import re
import os
import sys
import time
import hashlib
import getpass
import argparse
import platform
import traceback
import subprocess


def Windows():
	return platform.system() == "Windows"


def MacOS():
	return platform.system() == "Darwin"


def get_parent_dir(path):
	return os.path.abspath(os.path.join(path, os.pardir))


def launchCommand(cmd):
	print("Execute command: {}".format(cmd))

	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()

	try:
		rc = p.wait(timeout=600)
	except psutil.TimeoutExpired as err:
		rc = -1
		for child in reversed(p.children(recursive=True)):
			child.terminate()
		p.terminate()
	except Exception as ex:
		print("launch command exception:".format(ex))

	print(stdout)
	print(stder)

	print("Executing finished.")


def installMaya(maya_installer):

	if Windows():
		pass

	elif MacOS():
		launchCommand("hdiutil attach {} -mountpoint /Volumes/RadeonProRenderMaya".format(maya_installer))
		launchCommand("{}/installMayaPlugin".format(os.getenv("CIS_TOOLS")))
		launchCommand("hdiutil detach /Volumes/RadeonProRenderMaya")


if __name__ == "__main__":

	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-m', '--maya_installer', required=True)
	args = parser.parse_args()

	try:
		print("Try #1")
		installMaya(args.maya_installer)
	except Exception as ex:
		traceback.print_exc()
	
	print("FINISHED")
