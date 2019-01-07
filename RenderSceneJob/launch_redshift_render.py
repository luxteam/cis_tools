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
	parser.add_argument('--pass_limit', required=True)
	parser.add_argument('--sceneName', required=True)

	args = parser.parse_args()

	current_path = os.getcwd()
	redshift_scene = os.path.join(current_path, args.scene)

	if not os.path.exists('Output'):
		os.makedirs('Output')
	output_path = os.path.join(current_path, "Output")
	
	args.sceneName = os.path.basename(args.sceneName)

	# Redshift batch render
	cmd_render = '''"C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\Render.exe" -r redshift -log redshift_tool.log -im {scene_name} -of jpg -rd {output_path} {redshift_scene}'''\
					.format(tool=args.tool, scene_name = args.sceneName, output_path=output_path, redshift_scene=redshift_scene)

	with open(os.path.join(current_path, 'redshift_script.bat'), 'w') as f:
		f.write(cmd_render)				

	p = psutil.Popen(os.path.join(current_path, 'redshift_script.bat'))
	stdout, stderr = p.communicate()


if __name__ == "__main__":
	main()
