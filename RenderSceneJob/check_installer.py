import os
import argparse
from shutil import copyfile


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	args = parser.parse_args()

	folder = args.folder
	plugin_folder = "../../RenderServiceStorage"
	match = False
	_50GB = 5 * 10^9
	installer_name = ""

	for rootdir, dirs, files in os.walk(folder):
		for file in files:
			if file.endswith('.msi') or file.endswith('.run') or file.endswith('.dmg'):
				installer_path = os.path.join(rootdir, file)
				installer_name = file

	path_size = get_size(plugin_folder)

	for rootdir, dirs, files in os.walk(folder):
		for file in files:
			if file == installer_name:
				copyfile(os.path.join(plugin_folder, installer_name), os.path.split(installer_path))
				match = True

	print('Match')
	print('OK')

def get_size(folder):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


	
if __name__ == "__main__":

	main()