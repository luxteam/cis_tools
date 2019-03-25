import argparse
import os
import subprocess
import psutil
import pyscreenshot
from subprocess import Popen

def main():

	parser = argparse.ArgumentParser()

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
			project = work_path + args.scene.split("/")[1]

	if not zip_file:
		project = work_path

	# Redshift batch render
	cmd_render = '''"C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\Render.exe" -r redshift -proj "{project}" -log redshift_tool.log -im {scene_name} -of jpg -rd {output_path} {redshift_scene}'''\
					.format(tool=args.tool, scene_name = sceneName, output_path=output_path, redshift_scene=redshift_scene, project=project)

	with open(os.path.join(current_path, 'redshift_script.bat'), 'w') as f:
		f.write(cmd_render)				

	p = psutil.Popen(os.path.join(current_path, 'redshift_script.bat'))
	stdout, stderr = p.communicate()


if __name__ == "__main__":
	main()
