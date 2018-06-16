import os
import argparse

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	parser.add_argument('--scene')
	parser.add_argument('--pass_limit')
	parser.add_argument('--render_device')
	args = parser.parse_args()
	
	folder = args.folder

	with open(os.path.join(folder, "maya_render.mel")) as f:
            mel_template = f.read()
	melScript = mel_template.format(scene=args.scene, pass_limit=args.pass_limit, render_device=args.render_device)

	with open(os.path.join(folder, "maya_render.mel"), 'w') as f:
            f.write(melScript)
			
if __name__ == "__main__":

	main()
