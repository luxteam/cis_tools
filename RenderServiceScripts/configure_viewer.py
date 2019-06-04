import os
import json
import argparse
import subprocess
import psutil


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
	gltf_file = None
	ui_config = None
	
	for rootdir, dirs, files in os.walk("scene"):
		for file in files:
			if file.endswith('.gltf'):
				gltf_file = os.path.join("scene", file)
			if file.endswith('.json'):
				ui_config = os.path.join("scene", file)
	# set default
	if ui_config == None:
		ui_config = ""

	with open("config.json") as f:
		config = json.loads(f.read())

	config['scene']['path'] = gltf_file
	config['screen']['width'] = int(args.width)
	config['screen']['height'] = int(args.height)
	config['engine'] = args.engine
	config['uiConfig'] = ui_config

	with open('config.json', 'w') as f:
		json.dump(config, f, indent=' ', sort_keys=True)
		
	# parse scene name
	split_name = args.scene_name.split('.')
	filename = '.'.join(split_name[0:-1])

	# pack zip
	zip_name = "RPRViewerPack_{}_{}_{}.zip".format(args.version, filename, args.scene_version)	
	st = psutil.Popen('7z a "{}" ./"{}"/*'.format(zip_name, "."), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	st.communicate()

	config['save_frames'] = "yes"
	config['iterations_per_frame'] = int(args.iterations)
	config['frame_exit_after'] = 1
	with open('config.json', 'w') as f:
		json.dump(config, f, indent=' ')
	
	p = psutil.Popen("RadeonProViewer.exe", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	try:
		stdout, stderr = p.communicate(timeout=600)
	except (subprocess.TimeoutExpired, psutil.TimeoutExpired) as err:
		try:
			for child in reversed(p.children(recursive=True)):
				child.terminate()
			p.terminate()
		except Exception as ex:
			print(ex)

	with open("output.txt", 'w', encoding='utf-8') as file:
			stdout = stdout.decode("utf-8")
			file.write(stdout)

	with open("output.txt", 'a', encoding='utf-8') as file:
		file.write("\n ----STDERR---- \n")
		stderr = stderr.decode("utf-8")
		file.write(stderr)
	
	print(zip_name)
	
if __name__ == "__main__":
	try_count = 0
	while try_count < 3:
		try:
			main()
			exit(0)
		except Exception as ex:
			with open("exception.txt", 'a') as f:
				f.write(str(ex) + "\r\n")
			try_count += 1
			if try_count == 3:
				exit(1)