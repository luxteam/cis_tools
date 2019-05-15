import argparse
import sys
import os
import re
import subprocess
import psutil
import json
import requests

def parse_scenename(name):
	split_name = name.split('.')
	filename = '.'.join(split_name[0:-1])
	ext = split_name[-1]
	return filename, ext


def str_to_raw(s):
    raw_map = {8:r'\b', 7:r'\a', 12:r'\f', 10:r'\n', 13:r'\r', 9:r'\t', 11:r'\v'}
    return r''.join(i if ord(i) > 32 else raw_map.get(ord(i), i) for i in s)


def getScenes(folder):
	scenes = []
	for rootdir, dirs, files in os.walk(folder):
		for file in files:
			if file.endswith('.rpr'):
				scenes.append(os.path.join(rootdir, file))

	return scenes

def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--django_ip', required=True)
	parser.add_argument('--id', required=True)

	parser.add_argument('--tool', required=True)
	parser.add_argument('--pass_limit', required=True)
	parser.add_argument('--width', required=True)
	parser.add_argument('--height', required=True)
	parser.add_argument('--sceneName', required=True)
	parser.add_argument('--startFrame', required=True)
	parser.add_argument('--endFrame', required=True)
	parser.add_argument('--gpu', required=True)

	args = parser.parse_args()

	startFrame = int(args.startFrame)
	endFrame = int(args.endFrame)

	current_path = os.getcwd()
	if not os.path.exists('Output'):
		os.makedirs('Output')
	output_path = os.path.join(current_path, "Output")

	scenes = getScenes(current_path)

	timeout = 3600 / len(scenes)
	render_time = 0

	if startFrame == 1 and endFrame == 1:
		animation = False
	else:
		animation = True

	# single rpr file
	if len(scenes) == 1:
		sceneName = os.path.basename(str_to_raw(args.sceneName))
		file_name, file_format = parse_scenename(sceneName)

		config_json = {}
		config_json["width"] = int(args.width)
		config_json["height"] = int(args.height)
		config_json["iterations"] = int(args.pass_limit)
		config_json["threads"] = 4
		config_json["output"] = os.path.join(output_path, file_name + ".png")
		config_json["output.json"] = os.path.join(output_path, file_name + ".json")
		config_json["context"] = {
			"gpu0": 1 if 'gpu0' in args.gpu else 0,
			"gpu1": 1 if 'gpu1' in args.gpu else 0,
			"gpu2": 1 if 'gpu2' in args.gpu else 0,
			"gpu3": 1 if 'gpu3' in args.gpu else 0,
			"gpu4": 1 if 'gpu4' in args.gpu else 0,
			"gpu5": 1 if 'gpu5' in args.gpu else 0,
			"threads": 16,
			"debug": 0
		}

		ScriptPath = os.path.join(current_path, "cfg_{}.json".format(file_name))
		cmdRun = '"{tool}" "{scene}" "{template}"\n'.format(tool="C:\\rprSdkWin64\\RprsRender64.exe", scene=scenes[0], template=ScriptPath)
		cmdScriptPath = os.path.join(current_path, '{}.bat'.format(file_name))
		
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

		with open(os.path.join('Output', "core_log.txt"), 'a', encoding='utf-8') as file:
			stdout = stdout.decode("utf-8")
			file.write(stdout)

		with open(os.path.join('Output', "core_log.txt"), 'a', encoding='utf-8') as file:
			file.write("\n ----STEDERR---- \n")
			stderr = stderr.decode("utf-8")
			file.write(stderr)

		try:
			rc = p.wait(timeout=timeout)
		except psutil.TimeoutExpired as err:
			rc = -1
			for child in reversed(p.children(recursive=True)):
				child.terminate()
			p.terminate()

		

		# post request
		try:
			with open(os.path.join(output_path, file_name + ".json")) as f:
				data = json.loads(f.read().replace("\\", "\\\\"))
			render_time = data['render.time.ms'] / 1000
		except:
			print("Error render")

	elif len(scenes) > 1 and animation:
		sceneName = os.path.basename(str_to_raw(args.sceneName))
		file_name, file_format = parse_scenename(sceneName)

		for frame in range(startFrame, endFrame + 1):

			post_data = {'tool': 'Core', 'current_frame': frame, 'id': args.id, 'status':'frame'}
			response = requests.post(args.django_ip, data=post_data)

			config_json = {}
			config_json["width"] = int(args.width)
			config_json["height"] = int(args.height)
			config_json["iterations"] = int(args.pass_limit)
			config_json["threads"] = 4
			config_json["output"] = os.path.join(output_path, file_name + "_" + str(frame).zfill(3) + ".png")
			config_json["output.json"] = os.path.join(output_path, file_name + "_" + str(frame).zfill(3) + ".json")
			config_json["context"] = {
				"gpu0": 1 if 'gpu0' in args.gpu else 0,
				"gpu1": 1 if 'gpu1' in args.gpu else 0,
				"gpu2": 1 if 'gpu2' in args.gpu else 0,
				"gpu3": 1 if 'gpu3' in args.gpu else 0,
				"gpu4": 1 if 'gpu4' in args.gpu else 0,
				"gpu5": 1 if 'gpu5' in args.gpu else 0,
				"threads": 16,
				"debug": 0
			}

			scene_name = scenes[0].split("\\")[-1].split(".")[0]
			scene = scenes[0].replace(scene_name, file_name + "_" + str(frame))	

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

			with open(os.path.join('Output', "core_log.txt"), 'a', encoding='utf-8') as file:
				stdout = stdout.decode("utf-8")
				file.write(stdout)

			with open(os.path.join('Output', "core_log.txt"), 'a', encoding='utf-8') as file:
				file.write("\n ----STEDERR---- \n")
				stderr = stderr.decode("utf-8")
				file.write(stderr)

			try:
				rc = p.wait(timeout=timeout)
			except psutil.TimeoutExpired as err:
				rc = -1
				for child in reversed(p.children(recursive=True)):
					child.terminate()
				p.terminate()

			try:
				with open(os.path.join(output_path, file_name + "_" + str(frame).zfill(3) + ".json")) as f:
					data = json.loads(f.read().replace("\\", "\\\\"))
				render_time += data['render.time.ms'] / 1000
			except:
				print("Error render")

	else:

		for scene in scenes:
			sceneName = os.path.basename(str_to_raw(scene))
			file_name, file_format = parse_scenename(scene)

			frame = re.findall(r'_\d+', file_name)
			if frame:
				frame = int(frame[-1][1:])
				file_name = '_'.join(sceneName.split("_")[0:-1]) + '_' + str(frame).zfill(3)

			config_json = {}
			config_json["width"] = int(args.width)
			config_json["height"] = int(args.height)
			config_json["iterations"] = int(args.pass_limit)
			config_json["threads"] = 4
			config_json["output"] = os.path.join(output_path, file_name + ".png")
			config_json["output.json"] = os.path.join(output_path, file_name + ".json")
			config_json["context"] = {
				"gpu0": 1 if 'gpu0' in args.gpu else 0,
				"gpu1": 1 if 'gpu1' in args.gpu else 0,
				"gpu2": 1 if 'gpu2' in args.gpu else 0,
				"gpu3": 1 if 'gpu3' in args.gpu else 0,
				"gpu4": 1 if 'gpu4' in args.gpu else 0,
				"gpu5": 1 if 'gpu5' in args.gpu else 0,
				"threads": 16,
				"debug": 0
			}

			ScriptPath = os.path.join(current_path, "cfg_{}.json".format(file_name))
			cmdRun = '"{tool}" "{scene}" "{template}"\n'.format(tool="C:\\rprSdkWin64\\RprsRender64.exe", scene=scene, template=ScriptPath)
			cmdScriptPath = os.path.join(current_path, '{}.bat'.format(file_name))
			
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

			with open(os.path.join('Output', "core_log.txt"), 'a', encoding='utf-8') as file:
				stdout = stdout.decode("utf-8")
				file.write(stdout)

			with open(os.path.join('Output', "core_log.txt"), 'a', encoding='utf-8') as file:
				file.write("\n ----STEDERR---- \n")
				stderr = stderr.decode("utf-8")
				file.write(stderr)

			try:
				rc = p.wait(timeout=timeout)
			except psutil.TimeoutExpired as err:
				rc = -1
				for child in reversed(p.children(recursive=True)):
					child.terminate()
				p.terminate()

			# post request
			try:
				with open(os.path.join(output_path, file_name + ".json")) as f:
					data = json.loads(f.read().replace("\\", "\\\\"))
				render_time += data['render.time.ms'] / 1000
			except:
				print("Error render")


	render_time = round(render_time, 2)
	post_data = {'tool': 'Core', 'render_time': render_time, 'id': args.id, 'status':'time'}
	#response = requests.post(args.django_ip, data=post_data)

if __name__ == "__main__":
	rc = main()
	exit(rc)
