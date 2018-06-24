import os
import argparse

def update_license(file):
	with open(file) as f:
		scene_file = f.read()

	license = "fileInfo \"license\" \"student\";"
	scene_file = scene_file.replace(license, '')

	with open(file, "w") as f:
		f.write(scene_file)
		

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	args = parser.parse_args()

	folder = args.folder

	scene = []
	for rootdir, dirs, files in os.walk(folder):
		for file in files:
			if file.endswith('.ma') or file.endswith('mb'):
				try:
					update_license(os.path.join(rootdir, file))
				except Exception:
					pass
				scene.append(os.path.join(rootdir, file))
	if " " in scene[0]:
		os.rename(scene[0], scene[0].replace(" ", "_"))
		scene[0] = scene[0].replace(" ", "_")

	scene[0] = scene[0].replace("\\", "/")
	print (scene[0])


	

if __name__ == "__main__":

	main()
