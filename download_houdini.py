import re
import os
import sys
import argparse
import subprocess


def install(package):
	subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
	import twill
	import platform
	import shutil
	import requests
except Exception as ex:
	print("Required modules are missing, installing")
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
		print("Not able to install dependency automatically")
		print("Run: pip install twill platform shutil requests")
		sys.exit(-1)


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
	used_license = subprocess.check_output([hserver, '-f']).decode()
	print(used_license)
	if "None" in used_license:
		return True
	return False


def activate_license(browser, os_name, houdini_version):

	houdini_sessictrl_path = None
	houdini_hserver_path = None
	servername, servercode = None, None
	
	if os_name == "Windows":
		houdini_sessictrl_path = r"C:\Program Files\Side Effects Software\Houdini {}\bin\sesictrl.exe".format(houdini_version) 
		houdini_hserver_path = "hserver.exe"
		
	elif os_name == "Darwin":
		houdini_sessictrl_path = r"/Applications/Houdini/Houdini{}/Frameworks/Houdini.framework/Versions/Current/Resources/houdini/sbin/sesictrl".format(houdini_version) 
		houdini_hserver_path = r"/Applications/Houdini/Houdini{}/Frameworks/Houdini.framework/Versions/Current/Resources/bin/hserver".format(houdini_version) 
	else:
		houdini_sessictrl_path = r"/opt/hfs{}/houdini/sbin/sesictrl".format(houdini_version) 
		houdini_hserver_path = r"/opt/hfs{}/bin/hserver".format(houdini_version) 
		
	if not is_license_expired(houdini_hserver_path):
		print("License is already installed.")
		exit(0)

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
			if system_pl == "Windows":
				output = subprocess.check_output("{} -I {}".format(houdini_sessictrl_path, key)).decode()
			else:
				output = subprocess.check_output("{} -I {}".format(houdini_sessictrl_path, key), shell=True).decode()
			print(output)


def download_houdini(browser, os_name, houdini_version):

	binaries_path = os.path.join(os.getenv("CIS_TOOLS"), "..", "PluginsBinaries")
	if not os.path.exists(binaries_path):
		os.makedirs(binaries_path)

	if os_name == "Windows":
		file_ext = "exe"
	elif os_name == "Darwin":
		file_ext = "dmg"
	else:
		file_ext = "tar.gz"
	filepath = os.path.join(binaries_path, "houdini-{}.".format(houdini_version) + file_ext)

	if os.path.exists(filepath):
		return filepath

	url = 'https://www.sidefx.com/download/daily-builds/'
	headers = {
		'referer': url,
		'X-Requested-With': 'XMLHttpRequest'
	}

	response = browser._session.get(url, headers=headers)
	if response.status_code == 200:
		for line in response.text.split():
			if os_name == "Windows" and "houdini-{}".format(houdini_version) in line and ".exe" in line:
				break
			elif os_name == "Darwin" and "houdini-{}".format(houdini_version) in line and ".dmg" in line:
				break
			elif "houdini-{}".format(houdini_version) in line and ".tar.gz" in line:
				break

		download_link = 'https://www.sidefx.com' + line.split("\">")[0][6:]
		print("Download link: {}".format(download_link))
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
	else:
		print("Can't download houdini version from sidefx page. Return code: {}".format(response.status_code))
		exit(-1)

	response = browser._session.get(download_link, cookies=response.cookies, stream=True)
	if response.status_code == 200:
		
		with open(filepath, "wb") as file:
			for chunk in response.iter_content(chunk_size=1024*1024):
				if chunk:
					file.write(chunk)
	else:
		print("Can't download houdini version from cloudfront. Return code: {}".format(response.status_code))
		exit(-1)

	return filepath


def installHoudini(os_name, houdini_installer):

	if os_name == "Windows":
		cmd = '"{houdini_installer}" /S /AcceptEula=yes /LicenseServer=Yes /DesktopIcon=No ' \
		  '/FileAssociations=Yes /HoudiniServer=Yes /EngineUnity=No ' \
		  '/EngineMaya=No /EngineUnreal=No /HQueueServer=No ' \
		  '/HQueueClient=No /IndustryFileAssociations=Yes ' \
		  '/ForceLicenseServer=Yes /MainApp=Yes /Registry=Yes' \
		  .format(houdini_installer=houdini_installer)
	elif os_name == "Darwin":
		cmd = 'sudo hdiutil attach {houdini_installer} \
				cd /Volumes/Houdini \
				sudo installer -pkg Houdini.pkg -target / \
			'.format(houdini_installer=houdini_installer)
	else:
		houdini_installer_path = houdini_installer.split(".tar.gz")[0]
		cmd = 'tar -xzf {houdini_installer} \
				cd {houdini_installer_path} \
				./houdini.install --auto-install --accept-EULA'.format(houdini_installer=houdini_installer, \
					houdini_installer_path=houdini_installer_path)

	print("Execute command: {}".format(cmd))
	print("Start install...")

	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.communicate()

	try:
		rc = p.wait(timeout=600)
	except psutil.TimeoutExpired as err:
		rc = -1
		for child in reversed(p.children(recursive=True)):
			child.terminate()
		p.terminate()

	# os.remove(houdini_installer)


def checkInstalledHoudini(os_name, target_version):

	target_version_installed = False

	if os_name == "Windows":
		houdini_paths = os.listdir(r"C:\Program Files\Side Effects Software")
		for path in houdini_paths:
			if target_version in path:
				target_version_installed = True
			else:
				print("{} wil be deleted.".format(path))
				try:
					shutil.rmtree(os.path.join(r"C:\Program Files\Side Effects Software", path))
				except Exception as ex:
					print(ex)
		
	elif os_name == "Darwin":
		houdini_paths = os.listdir("/Applications/Houdini")
		for path in houdini_paths:
			if target_version in path:
				target_version_installed = True
			else:
				print("{} wil be deleted.".format(path))
				try:
					shutil.rmtree(os.path.join("/Applications/Houdini", path))
				except Exception as ex:
					print(ex)

	else:
		houdini_paths = os.listdir("/opt")
		for path in houdini_paths:
			if target_version in path:
				target_version_installed = True
			elif "hfs" in path and path != "hfs18.0":
				print("{} wil be deleted.".format(path))
				try:
					shutil.rmtree(os.path.join("/opt", path))
				except Exception as ex:
					print(ex)

	return target_version_installed


if __name__ == "__main__":

	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-l', '--username', required=True)
	parser.add_argument('-p', '--password', required=True)
	parser.add_argument('-v', '--version', required=True)
	args = parser.parse_args()

	os_name = platform.system()

	# True if target version is already installed 
	if not checkInstalledHoudini(os_name, args.version):
	
		# authorization 
		browser = twill.commands.browser
		twill.commands.go('https://www.sidefx.com/login/')
		submit_form({'sfx-login-username': args.username, 'sfx-login-password': args.password})

		filepath = download_houdini(browser, os_name, args.version)
		installHoudini(os_name, filepath)
		activate_license(browser, os_name, args.version)

	print("FINISHED")

	
