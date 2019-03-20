import argparse
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
from shutil import copyfile


def get_windows_titles():
	EnumWindows = ctypes.windll.user32.EnumWindows
	EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
	GetWindowText = ctypes.windll.user32.GetWindowTextW
	GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
	IsWindowVisible = ctypes.windll.user32.IsWindowVisible

	titles = []

	def foreach_window(hwnd, lParam):
		if IsWindowVisible(hwnd):
			length = GetWindowTextLength(hwnd)
			buff = ctypes.create_unicode_buffer(length + 1)
			GetWindowText(hwnd, buff, length + 1)
			titles.append(buff.value)
		return True

	EnumWindows(EnumWindowsProc(foreach_window), 0)

	return titles


def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--tool', required=True)
	parser.add_argument('--scene', required=True)
	parser.add_argument('--render_device_type', required=True)
	parser.add_argument('--pass_limit', required=True)
	parser.add_argument('--startFrame', required=True)
	parser.add_argument('--endFrame', required=True)
	parser.add_argument('--sceneName', required=True)

	args = parser.parse_args()

	current_path = os.getcwd()
	redshift_scene = os.path.join(current_path, args.scene)

	if not os.path.exists('Output'):
		os.makedirs('Output')
	output_path = os.path.join(current_path, "Output")
	
	args.sceneName = os.path.basename(args.sceneName)
	work_path = "C:/JN/WS/Render_Scene_Render/"
	# check zip/7z
	files = os.listdir(work_path)
	zip_file = False
	for file in files:
		if file.endswith(".zip") or file.endswith(".7z"):
			zip_file = True
			project = work_path + args.scene.split("/")[1]

	if not zip_file:
		project = work_path

	with open("maya_render.py") as f:
		py_template = f.read()
	
	pyScript = py_template.format(scene = args.scene, pass_limit = args.pass_limit, scene_name = args.sceneName, \
			res_path=output_path, render_device_type = args.render_device_type, startFrame=args.startFrame, endFrame=args.endFrame, project=project)

	with open('maya_render.py', 'w') as f:
		f.write(pyScript)

	cmdRun = '''
	set MAYA_CMD_FILE_OUTPUT=%cd%/Output/rpr_tool.txt
	set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
	set PYTHONPATH=%cd%;%PYTHONPATH%
	"C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\Maya.exe" -command "python(\\"import maya_render as render\\"); python(\\"render.main()\\");" ''' \
		.format(tool=args.tool)

	with open(os.path.join(current_path, 'script.bat'), 'w') as f:
		f.write(cmdRun)

	p = psutil.Popen(os.path.join(current_path, 'script.bat'), stdout=subprocess.PIPE)
	rc = -1

	while True:
		try:
			rc = p.wait(timeout=5)
		except psutil.TimeoutExpired as err:
			fatal_errors_titles = ['maya', 'Student Version File', 'Radeon ProRender Error', 'Script Editor']
			if set(fatal_errors_titles).intersection(get_windows_titles()):
				rc = -1
				try:
					error_screen = pyscreenshot.grab()
					error_screen.save(os.path.join(args.output, 'error_screenshot.jpg'))
				except:
					pass
				for child in reversed(p.children(recursive=True)):
					child.terminate()
				p.terminate()
				break
		else:
			break

	stdout, stderr = p.communicate()


if __name__ == "__main__":
	rc = main()
	exit(rc)
