import argparse
import os
import subprocess
import psutil
import ctypes
import pyscreenshot
from subprocess import Popen
import requests
import json


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

	parser.add_argument('--django_ip', required=True)
	parser.add_argument('--id', required=True)

	parser.add_argument('--tool', required=True)
	parser.add_argument('--scene', required=True)
	parser.add_argument('--sceneName', required=True)

	args = parser.parse_args()

	current_path = os.getcwd()
	redshift_scene = os.path.join(current_path, args.scene)

	if not os.path.exists('Output'):
		os.makedirs('Output')
	output_path = os.path.join(current_path, "Output")
	
	sceneName = os.path.basename(args.sceneName).split(".")[0]
	work_path = "C:/JN/WS/RenderServiceConvertJob/"
	# check zip/7z
	files = os.listdir(work_path)
	zip_file = False
	for file in files:
		if file.endswith(".zip") or file.endswith(".7z"):
			zip_file = True
			scene_path = "/".join(args.scene.split("/")[1:-2])
			project = work_path + scene_path

	if not zip_file:
		project = work_path
	

	with open("maya_rpr_conversion.py") as f:
		py_template = f.read()
	
	pyScript = py_template.format(scene = args.scene, scene_name = sceneName, res_path=output_path, project=project)

	with open('maya_rpr_conversion.py', 'w') as f:
		f.write(pyScript)

	cmdRun = '''
	set MAYA_CMD_FILE_OUTPUT=%cd%/rpr_tool.log 
	set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
	set PYTHONPATH=%cd%;%PYTHONPATH%
	"C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\Maya.exe" -command "python(\\"import maya_rpr_conversion as converter\\"); python(\\"converter.main()\\");" ''' \
		.format(tool=args.tool)

	with open(os.path.join(current_path, 'script.bat'), 'w') as f:
		f.write(cmdRun)

	p = psutil.Popen(os.path.join(current_path, 'script.bat'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

	os.rename(args.scene + ".log", os.path.join("Output", sceneName + ".log"))	
	os.rename("rpr_tool.log", os.path.join("Output", "rpr_tool.log"))	

	# post request
	with open(os.path.join(current_path, "render_info.json")) as f:
		data = json.loads(f.read())

	post_data = {'tool': 'Redshift', 'rpr_render_time': data['render_time'], 'id': args.id, 'status':'rpr_render_info'}
	response = requests.post(args.django_ip, data=post_data)
	

if __name__ == "__main__":
	main()