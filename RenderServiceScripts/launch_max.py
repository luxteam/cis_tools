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
	parser.add_argument('--min_samples', required=True)
	parser.add_argument('--max_samples', required=True)
	parser.add_argument('--noise_threshold', required=True)
	parser.add_argument('--startFrame', required=True)
	parser.add_argument('--endFrame', required=True)
	parser.add_argument('--sceneName', required=True)

	args = parser.parse_args()
	current_path = os.getcwd().replace("\\", "\\\\")

	if not os.path.exists('Output'):
		os.makedirs('Output')

	with open("max_render.ms") as f:
		max_script_template = f.read()

	sceneName = os.path.basename(args.sceneName).split(".")[0]
	
	maxScript = max_script_template.format(scene=args.scene, min_samples = args.min_samples, max_samples = args.max_samples, \
		 noise_threshold = args.noise_threshold, scene_name = sceneName, res_path=current_path)

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

	try:
		# post request
		with open(os.path.join(current_path, "render_info.json")) as f:
			data = json.loads(f.read())

		post_data = {'tool': 'Max', 'render_time': data['render_time'], 'width': data['width'], 'height': data['height'],\
			 'min_samples': data['min_samples'], 'max_samples': data['max_samples'], 'noise_threshold': data['noise_threshold'], 'id': args.id, 'status':'render_info'}
		response = requests.post(args.django_ip, data=post_data)
	except Exception as ex:
		print(ex)

	return rc


if __name__ == "__main__":
	rc = main()
	exit(rc)
