import os
import argparse
from shutil import copyfile
import hashlib


def file_md5(file_path):
	with open(file_path, 'rb') as file:
		file_as_bytes = file.read()
	return hashlib.md5(file_as_bytes).hexdigest()


def get_size(folder):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(folder):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	parser.add_argument('--plugin_md5')
	args = parser.parse_args()

	plugin_folder = "../../RenderServiceStorage"
	match = False
	_20GB = 20 * 10**9

	if not os.path.exists(plugin_folder):
		os.makedirs(plugin_folder)

	path_size = get_size(plugin_folder)
	for rootdir, dirs, files in os.walk(plugin_folder):
		for file in files:
			current_md5 = file_md5(os.path.join(rootdir, file))
			if args.plugin_md5 == current_md5:
				installer_path = os.path.join(rootdir, file)
				match = True

	if path_size < _20GB and not match:
		print('DOWNLOAD_COPY')
	elif path_size > _20GB and not match:
		print('ONLY_DOWNLOAD')
	elif match:
		print(installer_path)


if __name__ == "__main__":

	main()