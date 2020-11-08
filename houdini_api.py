import re
import os
import sys
import time
import hashlib
import getpass
import argparse
import traceback
import subprocess


def install(package):
	subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
	import twill
	import platform
	import shutil
	import requests
except Exception as ex:
	print("Required modules are missing, trying to install...")
	try:
		install("twill")
		install("shutil")
		install("platform")
		install("requests")
		import twill
		import platform
		import shutil
		import requests
	except Exception as ex:
		print(ex)
		print("Failed to install dependency automatically.")
		print("Run: pip install twill platform shutil requests manually.")
		exit(-1)

import sidefx


def Windows():
	return platform.system() == "Windows"


def MacOS():
	return platform.system() == "Darwin"


def get_form(field_ids):
	for form in browser.forms:
		for field_id in field_ids:
			for field in form.inputs:
				if field.get('id') == field_id:
					break
			else:
				break
		else:
			return form
	print('Failed to find form with field_ids={}'.format(field_ids))


def submit_form(fields):
	form = get_form(fields.keys())
	for name, value in fields.items():
		field = browser.form_field(form, name)
		twill.utils.set_form_control_value(field, value)
	browser.clicked(form, field)
	twill.commands.submit()


def get_csrf():
	csrf_token = 'csrfmiddlewaretoken'
	for form in browser.forms:
		if csrf_token in form.inputs:
			return form.inputs[csrf_token].value


def get_server_info(sesictrl_path):
	return re.split(' |\t', subprocess.check_output([sesictrl_path, '-n']).decode().splitlines()[1].lstrip())[1:]


def is_license_expired(hserver):
	used_license = subprocess.check_output([hserver, '-l']).decode()
	print(used_license)
	if "Used Licenses" in used_license and not "None" in used_license:
		return False
	return True


def get_parent_dir(path):
	return os.path.abspath(os.path.join(path, os.pardir))


def parse_houdini_version(version):
	return ".".join(version.split(".")[:-1]), version.split(".")[-1]


def get_houdini_install_dir(houdini_version, houdini_is_python3):
	if Windows():
		return r"C:\Program Files\Side Effects Software\Houdini {}{}".format(houdini_version, ' Python3' if houdini_is_python3 else '') 
		
	elif MacOS():
		return r'/Applications/Houdini/Houdini{}{}'.format(houdini_version, '-py3' if houdini_is_python3 else '-py2')

	else:
		return r"/home/{}/Houdini/hfs{}{}".format(getpass.getuser(), houdini_version, '-py3' if houdini_is_python3 else '-py2') 


def activate_license(sidefx_client, houdini_version, houdini_is_python3):

	version, build = parse_houdini_version(houdini_version)

	install_dir = get_houdini_install_dir(houdini_version, houdini_is_python3)

	if Windows():
		houdini_sessictrl_path = install_dir + r'\bin\sesictrl.exe'
		houdini_hserver_path = "hserver.exe"
		
	elif MacOS():
		houdini_sessictrl_path = install_dir + r"/Frameworks/Houdini.framework/Versions/Current/Resources/houdini/sbin/sesictrl"
		houdini_hserver_path = install_dir + r"/Frameworks/Houdini.framework/Versions/Current/Resources/bin/hserver"

	else:
		houdini_sessictrl_path = install_dir + r'/houdini/sbin/sesictrl'
		houdini_hserver_path = install_dir + r'/bin/hserver'

	if not is_license_expired(houdini_hserver_path):
		print("License is already installed.")
		# return

	server_name, server_code = get_server_info(houdini_sessictrl_path)

	print('Server name: {}'.format(server_name))
	print('Server code: {}'.format(server_code))

	license_strings = sidefx_client.license.get_non_commercial_license(
        server_name=server_name, server_code=server_code, version=version, products='HOUDINI-NC')

	licenses = license_strings['license_keys']
	for key in licenses:
		print(key)
		if Windows():
			output = subprocess.check_output("{} -I {}".format(houdini_sessictrl_path, key)).decode()
		else:
			output = subprocess.check_output("{} -I {}".format(houdini_sessictrl_path, key), shell=True).decode()
		print(output)


def validate_file_hash(filepath, hash):
	file_hash = hashlib.md5()
	with open(filepath, 'rb') as f:
		for chunk in iter(lambda: f.read(4096), b''):
			file_hash.update(chunk)
	if file_hash.hexdigest() != hash:
		return False
	return True


def download_houdini(sidefx_client, houdini_version, houdini_is_python3):

	binaries_path = os.path.join(os.getenv("CIS_TOOLS"), "..", "PluginsBinaries")
	if not os.path.exists(binaries_path):
		os.makedirs(binaries_path)

	if Windows():
		platform = "win64"
	elif MacOS():
		platform = "macosx"
	else:
		platform = "linux"
	
	version, build = parse_houdini_version(houdini_version)

	if houdini_is_python3:
		product = "houdini-py3"
	else:
		product = "houdini"

	# Retrieve the latest daily build available
	latest_release = sidefx_client.download.get_daily_build_download(
		product=product, version=version, build=build, platform=platform)

	filepath = os.path.join(binaries_path, latest_release['filename'])
	if os.path.exists(filepath):
		print("Installer is already exist on PC.")
		if validate_file_hash(filepath, latest_release['hash']):
			return filepath
		os.remove(filepath)
		print("Local installer doesn't pass hash validation. Downloading new one...")

	response = requests.get(latest_release['download_url'], stream=True)
	if response.status_code == 200:
		block_size = 1024*1024*10
		dl = 0
		print("Starting downloading...")
		total_length = int(response.headers.get('content-length'))
		print("Total size {}Mb".format(int(total_length/1024.0/1024.0)))
		with open(filepath, "wb") as file:
			for chunk in response.iter_content(chunk_size=block_size):
				if chunk:
					file.write(chunk)
					file.flush()
					dl += len(chunk)
					done = int(50 * dl / total_length)
					print("Downloaded {}mb of {}mb".format(int(dl/1024.0/1024.0), int(total_length/1024.0/1024.0)))
	else:
		raise Exception("Can't download houdini version from cloudfront. Return code: {}".format(response.status_code))

	if validate_file_hash(filepath, latest_release['hash']):
		return filepath
	else:
		raise Exception('Checksum does not match!')


def launchCommand(cmd):
	print("Execute command: {}".format(cmd))

	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.communicate()

	try:
		rc = p.wait(timeout=600)
	except psutil.TimeoutExpired as err:
		rc = -1
		for child in reversed(p.children(recursive=True)):
			child.terminate()
		p.terminate()
	except Exception as ex:
		print("launch command exception:".format(ex))

	print("Executing finished.")


def installHoudini(version, is_python3, houdini_installer):

	houdini_install_dir = get_houdini_install_dir(version, is_python3)
	print(houdini_install_dir)

	if Windows():
		cmd = '"{houdini_installer}" /S /AcceptEULA=2020-05-05 /LicenseServer=Yes /DesktopIcon=No ' \
		  '/MainApp=Yes /Registry=Yes'.format(houdini_installer=houdini_installer)
		launchCommand(cmd)
		if is_python3:
			os.rename(houdini_install_dir[0:-8], houdini_install_dir)

	elif MacOS():
		launchCommand("hdiutil attach {} -mountpoint /Volumes/Houdini".format(houdini_installer))
		launchCommand("{}/installHoudini.sh {} {}".format(os.getenv("CIS_TOOLS"), houdini_install_dir[0:-4], houdini_install_dir))
		launchCommand("hdiutil detach /Volumes/Houdini")
		if is_python3:
			# need sudo 
			# os.rename(houdini_install_dir[0:-4], houdini_install_dir)
			pass

	else:
		binaries_path = os.path.join(os.getenv("CIS_TOOLS"), "..", "PluginsBinaries")
		launchCommand('tar -xzf {} -C {}'.format(houdini_installer, binaries_path))
		bin_paths = os.listdir(binaries_path)
		for path in bin_paths:
			if version in path and not "tar.gz" in path:

				houdini_install_parent_dir = get_parent_dir(houdini_install_dir)
				if not os.path.exists(houdini_install_parent_dir):
					os.makedirs(houdini_install_parent_dir)

				houdini_installer_path = os.path.join(binaries_path, path)
				launchCommand("{}/installHoudini.sh {} {}".format(os.getenv("CIS_TOOLS"), houdini_installer_path, houdini_install_dir))


def checkInstalledHoudini(target_version, target_is_python3):

	install_dir = get_houdini_install_dir(target_version, target_is_python3)

	if Windows():
		houdini_required_file = install_dir + r'\bin\sesictrl.exe'
		houdini_test_command = 'hserver.exe'

	elif MacOS():
		houdini_required_file = install_dir + r"/Frameworks/Houdini.framework/Versions/Current/Resources/bin/hserver"
		houdini_test_command = houdini_required_file

	else:
		houdini_required_file = install_dir + '/bin/hserver'
		houdini_test_command = houdini_required_file

	try:
		for path in os.listdir(get_parent_dir(install_dir)):
			if target_version in path and os.path.exists(houdini_required_file):
				launchCommand(houdini_test_command)
				return True
	except Exception as ex:
		print("Failed to check installed Houdini. Exception: {}".format(ex))

	print("Houdini isn't installed.")

	return False


def execute(sidefx, args):
	# True if target version is already installed 
	if not checkInstalledHoudini(args.version, args.python3):
		filepath = download_houdini(sidefx_client, args.version, args.python3)
		installHoudini(args.version, args.python3, filepath)
		if checkInstalledHoudini(args.version, args.python3):
			print("Houdini is successfully installed. Verification passed.")


if __name__ == "__main__":

	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-l', '--client_id', required=True)
	parser.add_argument('-p', '--client_secret_key', required=True)
	parser.add_argument('-v', '--version', required=True)
	parser.add_argument('--python3', action='store_true')
	args = parser.parse_args()

	# authorization 
	sidefx_client = sidefx.service(
		access_token_url="https://www.sidefx.com/oauth2/application_token",
		client_id=args.client_id,
		client_secret_key=args.client_secret_key,
		endpoint_url="https://www.sidefx.com/api/",
	)

	try:
		print("Try #1")
		execute(sidefx, args)
	except Exception as ex:
		traceback.print_exc()
		print("Failed to execute download and install scripts.")
		print("Try #2 after 60 seconds")
		time.sleep(60)
		execute(sidefx, args)

	activate_license(sidefx_client, args.version, args.python3)
	
	print("FINISHED")
