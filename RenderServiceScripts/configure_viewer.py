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
		ui_config = "UIConfig.json"

	config = {}
	config['scene'] = {}
	config['scene']['path'] = gltf_file
	config['screen'] = {}
	config['screen']['width'] = int(args.width)
	config['screen']['height'] = int(args.height)
	config['screen']['full_screen'] = "no"
	config['engine'] = args.engine
	config['primary_device'] = 0
	config['use_mgpu'] = "yes"
	config['use_denoiser'] = "yes"
	config['loader'] = "fx-gltf"
	config['render_interop'] = "yes"
	config['iterations_per_frame'] = 1
	config['camera'] = 0
	config['save_frames'] = "no"
	config['frame_exit_after'] = 0
	config['output_image_format'] = "png"
	config['camera_step'] = 0.3
	config['camera_roll_step'] = 2.0
	config['camera_fov_step'] = 0.1
	config['time_mode'] = "real"
	config['animation'] = "on"
	config['camera_fov_step'] = 0.1
	config['camera_fov_step'] = 0.1
	config['camera_fov_step'] = 0.1
	config['uiConfig'] = ui_config
	config['environment_light'] = {}
	config['environment_light']['add'] = "no"
	config['environment_light']['source'] = "sky.hdr"
	config['environment_light']['intensity'] = 1.5
	config['default_light'] = {}
	config['default_light']['add'] = "no"
	config['default_light']['position'] = [0.0, 20.0, 20.0, 1.0]
	config['default_light']['intensity'] = 5000.0
	config['textures'] = {}
	config['textures']['flip_y'] = "no"

	with open('config.json', 'w') as f:
		json.dump(config, f, indent=' ')
		
	# pack zip
	zip_name = "RPRViewerPack_{}_{}_{}.zip".format(args.version, args.scene_name, args.scene_version)	
	st = psutil.Popen('7z a "{}" ./"{}"/*'.format(zip_name, "."), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	st.communicate()

	config['save_frames'] = "yes"
	config['iterations_per_frame'] = int(args.iterations)
	config['frame_exit_after'] = 1
	with open('config.json', 'w') as f:
		json.dump(config, f, indent=' ')
	
	p = psutil.Popen("RadeonProViewer.exe", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	try:
		rc = p.communicate(timeout=600)
	except (subprocess.TimeoutExpired, psutil.TimeoutExpired) as err:
		try:
			for child in reversed(p.children(recursive=True)):
				child.terminate()
			p.terminate()
		except Exception as ex:
			print(ex)
	
	print(zip_name)
	
if __name__ == "__main__":
	try:
		main()
	except:
		exit(1)