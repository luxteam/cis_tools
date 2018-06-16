import os
import argparse

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	parser.add_argument('--pass_limit')
	parser.add_argument('--render_device')
	args = parser.parse_args()
	
	folder = args.folder
	render_device = args.render_device
	
	with open("blender_render.py") as f:
            blender_template = f.read()
	BlenderScript = blender_template.format(pass_limit=int(args.pass_limit), render_device=render_device)

	with open("blender_render.py", 'w') as f:
            f.write(BlenderScript)
			
if __name__ == "__main__":

	main()
