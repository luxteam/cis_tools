import argparse
import os
import subprocess
import psutil
import requests
import json
import datetime
import glob
import os
import logging

# logging
logging.basicConfig(filename="launch_render_log.txt", level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')
logger = logging.getLogger(__name__)


def update_license(file):
	with open(file) as f:
		scene_file = f.read()

	license = "fileInfo \"license\" \"student\";"
	scene_file = scene_file.replace(license, '')

	with open(file, "w") as f:
		f.write(scene_file)


def find_maya_scene():
	scene = []
	for rootdir, dirs, files in os.walk(os.getcwd()):
		for file in files:
			if file.endswith('.ma') or file.endswith('mb'):
				try:
					update_license(os.path.join(rootdir, file))
				except Exception:
					pass
				scene.append(os.path.join(rootdir, file))

	scene[0] = scene[0].replace("\\", "/")
	return scene[0]


def send_status(post_data, django_ip):	
	try_count = 0
	while try_count < 3:
		try:
			response = requests.post(django_ip, data=post_data)
			if response.status_code  == 200:
				logger.info("POST request successfuly sent.")
				break
			else:
				logger.info("POST reques failed, status code: " + str(response.status_code))
				break
		except Exception as e:
			if try_count == 2:
				logger.info("POST request try 3 failed. Finishing work.")
				break
			try_count += 1
			logger.info("POST request failed. Retry ...")


def send_results(post_data, files, django_ip):
	try_count = 0
	while try_count < 3:
		try:
			response = requests.post(django_ip, data=post_data, files=files)
			if response.status_code  == 200:
				logger.info("POST request successfuly sent.")
				break
			else:
				logger.info("POST reques failed, status code: " + str(response.status_code))
				break
		except Exception as e:
			if try_count == 2:
				logger.info("POST request try 3 failed. Finishing work.")
				break
			try_count += 1
			logger.info("POST request failed. Retry ...")


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
	parser.add_argument('--build_number', required=True)
	parser.add_argument('--tool', required=True)
	parser.add_argument('--min_samples', required=True)
	parser.add_argument('--max_samples', required=True)
	parser.add_argument('--noise_threshold', required=True)
	parser.add_argument('--startFrame', required=True)
	parser.add_argument('--endFrame', required=True)
	parser.add_argument('--width', required=True)
	parser.add_argument('--height', required=True)
	args = parser.parse_args()

	# create output folder for images and logs
	if not os.path.exists('Output'):
		os.makedirs('Output')
	
	# find all blender scenes
	maya_scene = find_maya_scene()
	logger.info("Found scene: {}".format(maya_scene))

	current_path_for_maya = os.getcwd().replace("\\", "/") + "/"

	# detect project path
	files = os.listdir(os.getcwd())
	zip_file = False
	for file in files:
		if file.endswith(".zip") or file.endswith(".7z"):
			zip_file = True
			project = "/".join(maya_scene.split("/")[:-2])

	if not zip_file:
		project = current_path_for_maya

	# read maya template
	with open("redshift_render.py") as f:
		maya_script_template = f.read()

	maya_script = maya_script_template.format(min_samples=args.min_samples, max_samples=args.max_samples, noise_threshold=args.noise_threshold, \
		width = args.width, height = args.height, res_path=current_path_for_maya, startFrame=args.startFrame, endFrame=args.endFrame, scene_path=maya_scene, project=project)

	# scene name
	filename = os.path.basename(maya_scene).split(".")[0]

	# save render py file
	render_file = "render_{}.py".format(filename) 
	with open(render_file, 'w') as f:
		f.write(maya_script)

	# Redshift batch render
	cmd_command = '''
		set MAYA_CMD_FILE_OUTPUT=%cd%/Output/maya_render_log.txt
		set MAYA_SCRIPT_PATH=%cd%;%MAYA_SCRIPT_PATH%
		set PYTHONPATH=%cd%;%PYTHONPATH%
		"C:\\Program Files\\Autodesk\\Maya{tool}\\bin\\Render.exe" -r redshift -preRender "python(\\"import {render_file} as render\\"); python(\\"render.main()\\");" -log "Output\\batch_render_log.txt" -of jpg {maya_scene}
		'''.format(tool=args.tool, maya_scene=maya_scene, render_file=render_file.split('.')[0])
	render_bat_file = "launch_render_{}.bat".format(filename)
	with open(render_bat_file, 'w') as f:
		f.write(cmd_command)		

	# starting rendering
	logger.info("Starting rendering scene: {}".format(maya_scene))
	post_data = {'status': 'Rendering', 'id': args.id}
	send_status(post_data, args.django_ip)	

	# start render
	p = psutil.Popen(render_bat_file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	# catch timeout ~30 minutes
	rc = 0
	try:
		stdout, stderr = p.communicate(timeout=2000)
	except (subprocess.TimeoutExpired, psutil.TimeoutExpired) as err:
		rc = -1
		for child in reversed(p.children(recursive=True)):
			child.terminate()
		p.terminate()

	# update render status
	logger.info("Finished rendering scene: {}".format(maya_scene))
	post_data = {'status': 'Completed', 'id': args.id}
	send_status(post_data, args.django_ip)

	# send render info
	logger.info("Sending render info")
	if os.path.exists("render_info.json"):
		render_time = 0
		try:
			render_time = round(get_rs_render_time(os.path.join("Output", "maya_render_log.txt")), 2)
		except:
			logger.info("Error. No render time!")
			
		with open("render_info.json") as f:
			data = json.loads(f.read())
		
		post_data = {'render_time': render_time, 'width': data['width'], 'height': data['height'], 'min_samples': data['min_samples'], \
			'max_samples': data['max_samples'], 'noise_threshold': data['noise_threshold'], 'id': args.id, 'status':'render_info'}
		send_status(post_data, args.django_ip)
	else:
		logger.info("Error. No render info!")

	# preparing dict with output files for post
	files = {}
	output_files = os.listdir('Output')
	for output_file in output_files:
		files.update({output_file: open(os.path.join('Output', output_file), 'rb')})
	logger.info("Output files: {}".format(files))

	# detect render status
	status = "Unknown"
	fail_reason = "Unknown"

	images = glob.glob(os.path.join('Output' ,'*.jpg'))
	if rc == 0 and images:
		logger.info("Render status: success")
		status = "Success"
	else:
		logger.info("Render status: failure")
		status = "Failure"
		if rc == -1:
			logger.info("Fail reason: timeout expired")
			fail_reason = "Timeout expired"
		elif not images:
			rc = -1
			logger.info("Fail reason: rendering failed, no output image")
			fail_reason = "No output image"
		else:
			rc = -1
			logger.info("Fail reason: unknown")
			fail_reason = "Unknown"

	logger.info("Sending results")
	post_data = {'status': status, 'fail_reason': fail_reason, 'id': args.id, 'build_number': args.build_number}
	send_results(post_data, files, args.django_ip)

	return rc

if __name__ == "__main__":
	rc = main()
	exit(rc)