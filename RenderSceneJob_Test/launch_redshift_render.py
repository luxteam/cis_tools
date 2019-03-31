import argparse
import os
import subprocess
import psutil
import pyscreenshot
from subprocess import Popen
import requests
import json

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

	args = parser.parse_args()

	current_path = os.getcwd()
	redshift_scene = os.path.join(current_path, args.scene)

	if not os.path.exists('Output'):
		os.makedirs('Output')
	output_path = os.path.join(current_path, "Output")
	
	sceneName = os.path.basename(args.sceneName).split(".")[0]
	work_path = "C:/JN/WS/Render_Scene_Render/"
	# check zip/7z
	files = os.listdir(work_path)
	zip_file = False
	for file in files:
		if file.endswith(".zip") or file.endswith(".7z"):
			zip_file = True
			scene_path = "/".join(args.scene.split("/")[1:-1])
			project = work_path + scene_path

	if not zip_file:
		project = work_path

	# Redshift batch render
	cmd_render = '''"C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\Render.exe" -r redshift -proj "{project}" -log redshift_tool.log -im {scene_name} -of jpg -rd {output_path} {redshift_scene}'''\
					.format(tool=args.tool, scene_name = sceneName, output_path=output_path, redshift_scene=redshift_scene, project=project)

	with open(os.path.join(current_path, 'redshift_script.bat'), 'w') as f:
		f.write(cmd_render)				

	p = psutil.Popen(os.path.join(current_path, 'redshift_script.bat'))
	stdout, stderr = p.communicate()

	render_time = get_rs_render_time(os.path.join(current_path, "Output", "redshift_tool.log"))
	post_data = {'tool': 'RedshiftConvert', 'render_time': render_time, 'id': args.id, 'status':'render_info'}
	response = requests.post(args.django_ip, data=post_data)


if __name__ == "__main__":
	main()
