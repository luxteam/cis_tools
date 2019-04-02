import argparse
import sys
import os
import subprocess
import psutil
import json
import requests

def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--django_ip', required=True)
	parser.add_argument('--id', required=True)

	parser.add_argument('--tool', required=True)
	parser.add_argument('--scene', required=True)
	parser.add_argument('--pass_limit', required=True)
	parser.add_argument('--width', required=True)
	parser.add_argument('--height', required=True)
	parser.add_argument('--sceneName', required=True)
	parser.add_argument('--startFrame', required=True)
	parser.add_argument('--endFrame', required=True)

	args = parser.parse_args()

	startFrame = int(args.startFrame)
	endFrame = int(args.endFrame)

	current_path = os.getcwd()
	if not os.path.exists('Output'):
		os.makedirs('Output')
	output_path = os.path.join(current_path, "Output")

	timeout = 3600 / (endFrame - startFrame + 1)
	render_time = 0

	# parse file
	sceneName = os.path.basename(args.sceneName)
	file_name = '_'.join(sceneName.split("_")[0:-1])
	file_format = sceneName.split(".")[1]

	for frame in range(startFrame, endFrame + 1):

		if endFrame - startFrame != 0:
			post_data = {'tool': 'Core', 'current_frame': frame, 'id': args.id, 'status':'frame'}
			response = requests.post(args.django_ip, data=post_data)

		config_json = {}
		config_json["width"] = int(args.width)
		config_json["height"] = int(args.height)
		config_json["iterations"] = int(args.pass_limit)
		config_json["threads"] = 4
		config_json["output"] = os.path.join(output_path, file_name + "_" + str(frame).zfill(3) + ".png")
		config_json["output.json"] = os.path.join(output_path, file_name + "_" + str(frame).zfill(3) + "_original.json")
		config_json["context"] = {
			"gpu0": 1,
			"gpu1": 0,
			"threads": 16,
			"debug": 0
		}

		# change render scene
		if endFrame - startFrame != 0:
			scene_name = args.scene.split("\\")[-1].split(".")[0]
			scene = args.scene.replace(scene_name, file_name + "_" + str(frame))
		else:
			scene = args.scene

		ScriptPath = os.path.join(current_path, "cfg_{}.json".format(file_name + "_" + str(frame)))
		cmdRun = '"{tool}" "{scene}" "{template}"\n'.format(tool="C:\\rprSdkWin64\\RprsRender64.exe", scene=scene, template=ScriptPath)
		cmdScriptPath = os.path.join(current_path, '{}.bat'.format(file_name + "_" + str(frame)))
		
		try:
			with open(ScriptPath, 'w') as f:
				json.dump(config_json, f, indent=4)
			with open(cmdScriptPath, 'w') as f:
				f.write(cmdRun)
		except OSError as err:
			pass

		p = psutil.Popen(cmdScriptPath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = p.communicate()
		rc = 0

		try:
			rc = p.wait(timeout=timeout)
		except psutil.TimeoutExpired as err:
			rc = -1
			for child in reversed(p.children(recursive=True)):
				child.terminate()
			p.terminate()


		# post request
		with open(os.path.join(output_path, file_name + "_" + str(frame).zfill(3) + "_original.json")) as f:
			data = json.loads(f.read().replace("\\", "\\\\"))
		render_time += round(data['render.time.ms'] / 1000, 2)


	post_data = {'tool': 'Core', 'render_time': render_time, 'id': args.id, 'status':'time'}
	response = requests.post(args.django_ip, data=post_data)

if __name__ == "__main__":
	rc = main()
	exit(rc)