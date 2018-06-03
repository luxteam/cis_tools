import os
import argparse

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	parser.add_argument('--scene')
	args = parser.parse_args()
	
	folder = args.folder
	scene = args.scene

	with open(os.path.join(folder, "maya_render.mel")) as f:
            mel_template = f.read()
	melScript = mel_template.format(scene=scene)

	with open(os.path.join(folder, "maya_render.mel"), 'w') as f:
            f.write(melScript)
			
if __name__ == "__main__":

	main()
