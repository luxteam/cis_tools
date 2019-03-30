import argparse
import sys
import os
import subprocess
import psutil
import json
import ctypes
import pyscreenshot
import platform


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
	
	if not os.path.exists('Output'):
		os.makedirs('Output')

	with open ("blender_render.py") as f:
		blender_script_template = f.read()

	sceneName = os.path.basename(args.sceneName).split(".")[0]

	BlenderScript = blender_script_template.format(render_device_type=args.render_device_type, pass_limit=args.pass_limit, \
													res_path=current_path, scene_name=args.scene, startFrame=args.startFrame, endFrame=args.endFrame, \
													sceneName=sceneName)

	with open("blender_render.py", 'w') as f:
		f.write(BlenderScript)

	system_pl = platform.system()

	if (system_pl == 'Linux'):
		cmdRun = '"{tool}" -b -P "{template}"' \
			.format(tool="blender",\
			 scene=args.scene, template="blender_render.py")
		cmdScriptPath = './launch_render.sh'
		with open('launch_render.sh', 'w') as f:
			f.write(cmdRun)
		os.system('chmod +x launch_render.sh')
		scene = args.scene.split("/")[-1]

	elif (system_pl == "Windows"):
		cmdRun = '"{tool}" -b -P "{template}"' \
			.format(tool="C:\\Program Files\\Blender Foundation\\Blender\\blender.exe", \
				scene=args.scene, template="blender_render.py")
		cmdScriptPath = 'launch_render.bat'
		with open('launch_render.bat', 'w') as f:
			f.write(cmdRun)
		scene = args.scene.split("\\")[-1]

	elif system_pl == 'Darwin':
		cmdRun = '"{tool}" -b -P "{template}"\n' \
			.format(tool="blender",\
			 scene=args.scene, template="blender_render.py")
		cmdScriptPath = './launch_render.sh'
		with open('launch_render.sh', 'w') as f:
		   f.write(cmdRun)
		os.system('chmod +x launch_render.sh')
		scene = args.scene.split("/")[-1]
	
	if not os.path.exists("Output"):
		os.makedirs("Output")

	p = subprocess.Popen(cmdScriptPath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()

	if args.startFrame == args.endFrame:
		with open(os.path.join('Output', "blender_log.txt".format(scene=scene)), 'w', encoding='utf-8') as file:
			stdout = stdout.decode("utf-8")
			file.write(stdout)

		with open(os.path.join('Output', "blender_log.txt".format(scene=scene)), 'a', encoding='utf-8') as file:
			file.write("\n ----STEDERR---- \n")
			stderr = stderr.decode("utf-8")
			file.write(stderr)
	else:
		with open(os.path.join('Output', "frame_{startFrame}_{endFrame}_blender_log.txt".format(startFrame=args.startFrame, endFrame=args.endFrame)), 'w', encoding='utf-8') as file:
			stdout = stdout.decode("utf-8")
			file.write(stdout)

		with open(os.path.join('Output', "frame_{startFrame}_{endFrame}_blender_log.txt".format(startFrame=args.startFrame, endFrame=args.endFrame)), 'a', encoding='utf-8') as file:
			file.write("\n ----STEDERR---- \n")
			stderr = stderr.decode("utf-8")
			file.write(stderr)

	rc = -1

	try:
		rc = p.wait(timeout=100)
	except psutil.TimeoutExpired as err:
		rc = -1
		error_screen = pyscreenshot.grab()
		error_screen.save(os.path.join('Output', 'error_screenshot.jpg'))
		for child in reversed(p.children(recursive=True)):
			child.terminate()
		p.terminate()

	# post request
	with open(os.path.join(current_path, "render_info.json")) as f:
		data = json.loads(f.read())

	post_data = {'tool': 'Blender', 'render_time': data['render_time'], 'width': data['width'], 'height': data['height'],\
		 'iterations': data['iterations'], 'id': args.id, 'status':'render_info'}
	response = requests.post(args.django_ip, data=post_data)

	return rc

if __name__ == "__main__":
	rc = main()
	exit(rc)
