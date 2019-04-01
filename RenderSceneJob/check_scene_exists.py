import os
import argparse
from shutil import copyfile

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--file_name')
	args = parser.parse_args()

	scene_folder = os.path.join("..", "..", "RenderServiceStorage", "scenes")
	match = False

	if not os.path.exists(scene_folder):
		os.makedirs(scene_folder)

	for rootdir, dirs, files in os.walk(scene_folder):
		for file in files:
			if args.file_name == file:
				scene_path = os.path.join(rootdir, file)
				match = True

	if match:
		print('file_exists')
	else:
		print("no_such_file")

if __name__ == "__main__":

	main()
