import argparse
import sys
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
import requests


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
	parser.add_argument('--render_device_type', required=True)
	parser.add_argument('--pass_limit', required=True)
	parser.add_argument('--startFrame', required=True)
	parser.add_argument('--endFrame', required=True)
	parser.add_argument('--sceneName', required=True)

	args = parser.parse_args()
	current_path = os.getcwd().replace("\\", "\\\\")

	render_device_type = args.render_device_type
	if render_device_type == 'gpu':
		render_device_type = '2'
	elif render_device_type == 'cpu':
		render_device_type = '1'
	elif render_device_type == 'dual':
		render_device_type = '3'

	if not os.path.exists('Output'):
		os.makedirs('Output')

	with open("max_render.ms") as f:
		max_script_template = f.read()

	sceneName = os.path.basename(args.sceneName).split(".")[0]
	# check zip/7z
	files = os.listdir(current_path)
	zip_file = False
	for file in files:
		if file.endswith(".zip") or file.endswith(".7z"):
			zip_file = True
			scene_path = "\\\\".join(args.scene.split("/")[1:-2])
			project = current_path + "\\" + scene_path

	if not zip_file:
		project = current_path

	maxScript = max_script_template.format(scene=args.scene, pass_limit=args.pass_limit, \
		render_device_type=render_device_type, scene_name = sceneName, res_path=current_path, project=project)

	with open('max_render.ms', 'w') as f:
		f.write(maxScript)

	cmdRun = '"C:\\Program Files\\Autodesk\\3ds Max {tool}\\3dsmax.exe" -U MAXScript "{job_script}" -silent' \
		.format(tool=args.tool, job_script="max_render.ms")

	with open(os.path.join(current_path, 'script.bat'), 'w') as f:
		f.write(cmdRun)

	p = psutil.Popen(os.path.join(current_path, 'script.bat'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	rc = -1

	while True:
		try:
			rc = p.communicate(timeout=60)
		except (subprocess.TimeoutExpired, psutil.TimeoutExpired) as err:
			fatal_errors_titles = ['Radeon ProRender', 'AMD Radeon ProRender debug assert', current_path + ' - MAXScript',\
			'3ds Max', 'Microsoft Visual C++ Runtime Library', \
			'3ds Max Error Report', '3ds Max application', 'Radeon ProRender Error', 'Image I/O Error', 'Warning', 'Error']
			if set(fatal_errors_titles).intersection(get_windows_titles()):
				rc = -1
				try:
					error_screen = pyscreenshot.grab()
					error_screen.save(os.path.join("Output", 'error_screenshot.jpg'))
				except:
					pass
				for child in reversed(p.children(recursive=True)):
					child.terminate()
				p.terminate()
				break
		else:
			rc = 0
			break

	# post request
	with open(os.path.join(current_path, "render_info.json")) as f:
		data = json.loads(f.read())

	post_data = {'tool': 'Max', 'render_time': data['render_time'], 'width': data['width'], 'height': data['height'],\
		 'iterations': data['iterations'], 'id': args.id, 'status':'render_info'}
	response = requests.post(args.django_ip, data=post_data)

	return rc


if __name__ == "__main__":
	rc = main()
	exit(rc)
