import argparse
import os
import subprocess
import psutil
import pyscreenshot
from subprocess import Popen
import requests
import json
import datetime

def get_rs_render_time(log_name):
	with open(log_name, 'r') as file:
		for line in file.readlines():
			if "[Redshift] Rendering done - total time for 1 frames:" in line:
				time_s = line.split(": ")[-1]

				try:
					x = datetime.datetime.strptime(time_s.replace('\n', '').replace('\r', ''), '%S.%fs')
				except ValueError:
					x = datetime.datetime.strptime(time_s.replace('\n', '').replace('\r', ''), '%Mm:%Ss')
				# 	TODO: proceed H:M:S

				return float(x.second + x.minute * 60 + float(x.microsecond / 1000000))

def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--django_ip', required=True)
	parser.add_argument('--id', required=True)

	parser.add_argument('--tool', required=True)
	parser.add_argument('--scene', required=True)
	parser.add_argument('--sceneName', required=True)
	parser.add_argument('--min_samples')
	parser.add_argument('--max_samples')
	parser.add_argument('--noise_threshold')

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

	# Redshift batch render
	cmd_render = '''"set MAYA_SCRIPT_PATH=%CD%;MAYA_SCRIPT_PATH \n"C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\Render.exe" -r redshift -preRender "source maya_mel.mel" -proj "{project}" -log redshift_tool.txt -of jpg -rd {output_path} {redshift_scene}'''\
					.format(tool=args.tool, scene_name = sceneName, output_path=output_path, redshift_scene=redshift_scene, project=project)

	with open(os.path.join(current_path, 'redshift_script.bat'), 'w') as f:
		f.write(cmd_render)				

	p = psutil.Popen(os.path.join(current_path, 'redshift_script.bat'))
	stdout, stderr = p.communicate()

	try:
		os.rename("redshift_tool.txt", os.path.join("Output", "redshift_tool.txt"))	
		render_time = round(get_rs_render_time(os.path.join(current_path, "Output", "redshift_tool.txt")), 2)
		post_data = {'tool': 'Maya (Redshift)', 'render_time': render_time, 'id': args.id, 'status':'render_info'}
		response = requests.post(args.django_ip, data=post_data)
	except Exception as ex:
		print(ex)
		print("Error during parsing render time")


if __name__ == "__main__":
	main()