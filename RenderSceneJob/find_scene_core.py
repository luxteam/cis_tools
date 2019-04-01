import os
import argparse


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	args = parser.parse_args()

	folder = args.folder

	scene = []
	for rootdir, dirs, files in os.walk(folder):
		for file in files:
			if file.endswith('.rpr') or file.endswith('.gltf'):
				scene.append(os.path.join(rootdir, file))

	print (scene[0])

	
if __name__ == "__main__":

	main()
