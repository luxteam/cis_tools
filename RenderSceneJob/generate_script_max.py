import os
import argparse

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	parser.add_argument('--scene')
	args = parser.parse_args()
	
	folder = args.folder
	scene = args.scene
	scene = folder + "\\\\" + scene

	with open("max_render.ms") as f:
            max_template = f.read()
	maxScript = max_template.format(scene=scene)

	with open("max_render.ms", 'w') as f:
            f.write(maxScript)
			
if __name__ == "__main__":

	main()
