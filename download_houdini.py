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
			if os_name == "Windows" and "houdini-{}".format(houdini_version) in line and file_ext in line:
				break
			elif os_name == "Darwin" and "houdini-{}".format(houdini_version) in line and file_ext in line:
				break
			elif "houdini-{}".format(houdini_version) in line and file_ext in line:
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


def installHoudini(os_name, version, houdini_installer):
	binaries_path = os.path.join(os.getenv("CIS_TOOLS"), "..", "PluginsBinaries")

	if os_name == "Windows":
		cmd = '"{houdini_installer}" /S /AcceptEula=yes /LicenseServer=Yes /DesktopIcon=No ' \
		  '/FileAssociations=Yes /HoudiniServer=Yes /EngineUnity=No ' \
		  '/EngineMaya=No /EngineUnreal=No /HQueueServer=No ' \
		  '/HQueueClient=No /IndustryFileAssociations=Yes ' \
		  '/ForceLicenseServer=Yes /MainApp=Yes /Registry=Yes' \
		  .format(houdini_installer=houdini_installer)
		launchCommand(cmd)
	elif os_name == "Darwin":
		launchCommand('./installHoudini.sh {}'.format(houdini_installer))
	else:
		launchCommand('tar -xzf {} -C {}'.format(houdini_installer, binaries_path))
		bin_paths = os.listdir(binaries_path)
		for path in bin_paths:
			if version in path and not "tar.gz" in path:
				os.chdir(os.path.join(binaries_path, path))
				launchCommand('./houdini.install --auto-install --install-houdini --install-hfs-symlink --install-license \
					--install-bin-symlink --make-dir --no-root-check --accept-EULA')

	# os.remove(houdini_installer)


def checkInstalledHoudini(os_name, target_version):

	try:
		if os_name == "Windows":
			houdini_sessictrl_path = r"C:\Program Files\Side Effects Software\Houdini {}\bin\sesictrl.exe".format(target_version) 
			houdini_paths = os.listdir(r"C:\Program Files\Side Effects Software")
			for path in houdini_paths:
				if target_version in path and os.path.exists(houdini_sessictrl_path):
					launchCommand("hserver.exe")
					return True
				else:
					print("{} wil be deleted.".format(path))
					try:
						shutil.rmtree(os.path.join(r"C:\Program Files\Side Effects Software", path))
					except Exception as ex:
						print(ex)
			
		elif os_name == "Darwin":
			houdini_hserver_path = r"/Applications/Houdini/Houdini{}/Frameworks/Houdini.framework/Versions/Current/Resources/bin/hserver".format(target_version)
			houdini_paths = os.listdir("/Applications/Houdini")
			for path in houdini_paths:
				if target_version in path and os.path.exists(houdini_hserver_path):
					launchCommand(houdini_hserver_path)
					return True
				else:
					print("{} wil be deleted.".format(path))
					try:
						launchCommand("./removeHoudini {}".format(os.path.join("/Applications/Houdini", path)))
					except Exception as ex:
						print(ex)

		else:
			houdini_hserver_path = r"/opt/hfs{}/bin/hserver".format(target_version)
			houdini_paths = os.listdir("/opt")
			for path in houdini_paths:
				if target_version in path and os.path.exists(houdini_hserver_path):
					launchCommand(houdini_hserver_path)
					return True
				elif "hfs" in path and path != "hfs18.0":
					print("{} wil be deleted.".format(path))
					try:
						shutil.rmtree(os.path.join("/opt", path))
					except Exception as ex:
						print(ex)

	except Exception as ex:
		print("Failed to check installed Houdini. Exception: {}".format(ex))

	return False


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
		installHoudini(os_name, args.version, filepath)
		activate_license(browser, os_name, args.version)
		if not checkInstalledHoudini(os_name, args.version):
			os.remove(filepath)
			filepath = download_houdini(browser, os_name, args.version)
			installHoudini(os_name, args.version, filepath)
			activate_license(browser, os_name, args.version)
		else:
			print("Houdini is successfully installed. Verification passed.")

	print("FINISHED")

	
