import re
import os
import sys
import argparse
import subprocess
import getpass

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
		sys.exit(-1)


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
	exit(-1)
	if "Used Licenses" in used_license and not "None" in used_license:
		return False
	return True


def get_parent_dir(path):
	return os.path.abspath(os.path.join(path, os.pardir))


def get_houdini_install_dir(houdini_version, houdini_is_python3):
	if Windows():
		return r"C:\Program Files\Side Effects Software\Houdini {}{}".format(houdini_version, ' Python3' if houdini_is_python3 else '') 
		
	elif MacOS():
		return r'/Applications/Houdini/Houdini{}{}'.format(houdini_version, '-py3' if houdini_is_python3 else '-py2')

	else:
		return r"/home/{}/Houdini/hfs{}{}".format(getpass.getuser(), houdini_version, '-py3' if houdini_is_python3 else '') 


def activate_license(browser, houdini_version, houdini_is_python3):

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
		return

	servername, servercode = get_server_info(houdini_sessictrl_path)

	print('Server name: {}'.format(servername))
	print('Server code: {}'.format(servercode))

	url = 'https://www.sidefx.com/services/non-commercial-license/'
	headers = {
		'referer': url,
		'X-Requested-With': 'XMLHttpRequest'
	}

	request_data = {
		'product': 'HOUDINI-NC',
		'servername': servername,
		'servercode': servercode,
		'csrfmiddlewaretoken': get_csrf()
	}
	response = browser._session.post(url, data=request_data, headers=headers).json()

	if response['errors']:
		for error in response['errors']:
			print('Error: {}'.format(error))
	else:
		lic_response = response['lic_response']
		for key in lic_response['license_keys'] + [lic_response['server_key']]:
			print(key)
			if Windows():
				output = subprocess.check_output("{} -I {}".format(houdini_sessictrl_path, key)).decode()
			else:
				output = subprocess.check_output("{} -I {}".format(houdini_sessictrl_path, key), shell=True).decode()
			print(output)


def download_houdini(browser, houdini_version, houdini_is_python3):

	binaries_path = os.path.join(os.getenv("CIS_TOOLS"), "..", "PluginsBinaries")
	if not os.path.exists(binaries_path):
		os.makedirs(binaries_path)

	houdini_name = 'houdini'
	if houdini_is_python3:
		houdini_name += '-py3'
	houdini_name += '-' + houdini_version

	if Windows():
		file_ext = ".exe"
	elif MacOS():
		file_ext = ".dmg"
	else:
		file_ext = ".tar.gz"
	filepath = os.path.join(binaries_path, houdini_name + file_ext)

	if os.path.exists(filepath):
		print("Installer is already exist on PC.")
		return filepath

	url = 'https://www.sidefx.com/download/daily-builds/'
	headers = {
		'referer': url,
		'X-Requested-With': 'XMLHttpRequest'
	}

	response = browser._session.get(url, headers=headers)
	if response.status_code == 200:
		for line in response.text.split():
			if houdini_name in line and file_ext in line:
				download_link = 'https://www.sidefx.com' + line.split("\">")[0][6:]
				print("Download link: {}".format(download_link))
				break

		else:
			print("No required build on daily-builds page.")
			exit(-1)

	else:
		print("Can't get daily daily-builds page. Return code: {}".format(response.status_code))
		exit(-1)

	response = browser._session.get(download_link)
	if response.status_code == 200:
		for line in response.text.split():
			# In this line we can find redirect URL
			if "Retry" in line:
				download_link = line.split("\">")[0][6:].replace("&amp;", "&")
				print("Redirect download link: {}".format(download_link))
				break

		else:
			print('No redirect download link.')
			exit(-1)

	else:
		print("Can't download houdini version from sidefx page. Return code: {}".format(response.status_code))
		exit(-1)

	response = browser._session.get(download_link, cookies=response.cookies, stream=True)
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
		print("Can't download houdini version from cloudfront. Return code: {}".format(response.status_code))
		exit(-1)

	return filepath


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
		launchCommand("{}/installHoudini.sh {} {}".format(os.getenv("CIS_TOOLS"), houdini_installer, houdini_install_dir))
		launchCommand("hdiutil detach /Volumes/Houdini")
		if is_python3:
			os.rename(houdini_install_dir[0:-4], houdini_install_dir)

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


if __name__ == "__main__":

	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-l', '--username', required=True)
	parser.add_argument('-p', '--password', required=True)
	parser.add_argument('-v', '--version', required=True)
	parser.add_argument('--python3', action='store_true')
	args = parser.parse_args()

	# authorization 
	browser = twill.commands.browser
	twill.commands.go('https://www.sidefx.com/login/')
	submit_form({'sfx-login-username': args.username, 'sfx-login-password': args.password})

	# True if target version is already installed 
	if not checkInstalledHoudini(args.version, args.python3):
		filepath = download_houdini(browser, args.version, args.python3)
		installHoudini(args.version, args.python3, filepath)
		if not checkInstalledHoudini(args.version, args.python3):
			#os.remove(filepath)
			filepath = download_houdini(browser, args.version, args.python3)
			installHoudini(args.version, args.python3, filepath)
		else:
			print("Houdini is successfully installed. Verification passed.")

	activate_license(browser, args.version, args.python3)

	print("FINISHED")
