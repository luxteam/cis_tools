import os
import json


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--version')
	parser.add_argument('--width')
	parser.add_argument('--height')
	parser.add_argument('--engine')
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
		ui_config = "UIConfig.json"
		
	# Preparing config files
	with open('config.json') as f:
		config = json.load(f)
	config['scene']['path'] = gltf_file
	config['uiConfig'] = ui_config
	config['engine'] = args.engine
	config['screen']['width'] = int(args.width)
	config['screen']['height'] = int(args.height)
	with open('config.json', 'w') as f:
		json.dump(config, f, indent=' ')
		
	# pack zip
	zip_name = "RPRViewerPack_{}.zip".format(args.version)
	subprocess.check_call('7z a "{}" ./"{}"/*'.format(zip_name, "."), shell=True)
	
	return zip_name
	
if __name__ == "__main__":

	main()