import os
import argparse
from shutil import copyfile


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--link')
	args = parser.parse_args()

	link = args.link

	plugin_folder = "../../RenderServiceStorage"
	match = False
	_20GB = 2 * 10^9

	installer_name = os.path.split(link)[-1]

	if not os.path.exists(plugin_folder):
		os.makedirs(plugin_folder)
	path_size = get_size(plugin_folder)
	for rootdir, dirs, files in os.walk(plugin_folder):
		for file in files:
			if file == installer_name:
				match = True

	if path_size < _20GB and not match:
		print('DOWNLOAD_COPY')
	elif path_size > _20GB and not match:
		print('ONLY_DOWNLOAD')
	elif match:
		print('COPY')

def get_size(folder):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(folder):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size


	
if __name__ == "__main__":

	main()