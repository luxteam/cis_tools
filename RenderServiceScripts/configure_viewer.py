import os
import json
import argparse
import subprocess
import psutil
import logging
import traceback

# logging
logging.basicConfig(filename="python_log.txt", level=logging.INFO)
logger = logging.getLogger(__name__)


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--scene_name')
	parser.add_argument('--scene_version')
	parser.add_argument('--version')
	parser.add_argument('--width')
	parser.add_argument('--height')
	parser.add_argument('--engine')
	parser.add_argument('--iterations')
	args = parser.parse_args()

	# find GLTF scene and UIConfig
	gltf_file = ""
	ui_config = ""
	
	for rootdir, dirs, files in os.walk("scene"):
		for file in files:
			if file.endswith('.gltf'):
				gltf_file = os.path.join("scene", file)
			if file.endswith('.json'):
				ui_config = os.path.join("scene", file)

	if gltf_file:
		logger.info("Found scene: " + gltf_file)
	else:
		logger.error("No scene in the package!")
		exit(1)

	# set default
	if ui_config:
		logger.info("Found UI config: " + ui_config)
	else:
		logger.error("No UI config in the package!")

	# read config json file
	if os.path.isfile("config.json"):
		logger.info("Found config file.")
		try:
			with open("config.json") as f:
				config = json.loads(f.read())
			logger.info("Config file was read successfuly.")
		except Exception as ex:
			logger.error("Config file in corructed.")
			logger.error(str(ex))
			logger.error(traceback.format_exc())	
	else:
		logger.error("Config file in corructed.")
		exit(1)

	config['scene']['path'] = gltf_file
	config['screen']['width'] = int(args.width)
	config['screen']['height'] = int(args.height)

	config['engine'] = args.engine
	if args.engine == "hyb":
		config['draw_engine'] = "vw_vulkan"
	elif args.engine in ("rpr", "ogl"):
		config['draw_engine'] = "ogl"
		
	config['uiConfig'] = ui_config

	with open('config.json', 'w') as f:
		json.dump(config, f, indent=' ', sort_keys=True)
		
	# parse scene name
	split_name = args.scene_name.split('.')
	filename = '.'.join(split_name[0:-1])

	# pack zip
	repeat_launch = False
	for file in os.listdir():
		if file.endswith(".zip"):
			repeat_launch = True

	if not repeat_launch:
		try:
			zip_name = "RPRViewerPack_{}_{}.zip".format(args.version, filename)	
			st = psutil.Popen('7z a "{}" ./"{}"/*'.format(zip_name, "."), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			st.communicate()
			logger.info("Zip package was built successfuly.")
		except Exception as ex:
			logger.error("Zip package build failed.")
			logger.error(str(ex))
			logger.error(traceback.format_exc())	
			exit(1)

	config['save_frames'] = "yes"
	config['iterations_per_frame'] = int(args.iterations)
	config['frame_exit_after'] = 1
	with open('config.json', 'w') as f:
		json.dump(config, f, indent=' ')
	
	# Fix empty stdout 113 line.
	stdout, stderr = (b'', b'')

	if os.path.isfile("RadeonProViewer.exe"):
		p = psutil.Popen("RadeonProViewer.exe", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		try:
			stdout, stderr = p.communicate(timeout=300)
		except (subprocess.TimeoutExpired, psutil.TimeoutExpired) as err:
			try:
				for child in reversed(p.children(recursive=True)):
					child.terminate()
				p.terminate()
			except Exception as ex:
				logger.error(str(ex))
				logger.error(traceback.format_exc())	

		with open("viewer_log.txt", 'w', encoding='utf-8') as file:
			stdout = stdout.decode("utf-8")
			file.write(stdout)

		with open("viewer_log.txt", 'a', encoding='utf-8') as file:
			file.write("\n ----STDERR---- \n")
			stderr = stderr.decode("utf-8")
			file.write(stderr)
		
		if not os.path.isfile("img0001.png") and args.engine != "ogl":
			logger.error("Failed to render image! Retry ...")
			raise Exception("No image")
		else:
			logger.info("Testing was finished successfuly.")

	else:
		logger.error("Failed! No exe file in package.")
		exit(1)
	
if __name__ == "__main__":
	try_count = 0
	while try_count < 3:
		try:
			main()
			exit(0)
		except Exception as ex:
			logger.error(str(ex))
			logger.error(traceback.format_exc())
			try_count += 1
			if try_count == 3:
				exit(1)