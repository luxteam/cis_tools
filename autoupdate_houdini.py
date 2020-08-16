import re
import os
import twill
import argparse
import subprocess
import platform

# install twill?

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
	if "None" in used_license:
		return True
	return False


if __name__ == "__main__":

	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-l', '--username', required=True)
	parser.add_argument('-p', '--password', required=True)
	parser.add_argument('-v', '--version', required=True)
	args = parser.parse_args()

	houdini_sessictrl_path = None
	houdini_hserver_path = None
	servername, servercode = None, None
	system_pl = platform.system()
	
	if system_pl == "Windows":
		houdini_sessictrl_path = r"C:\Program Files\Side Effects Software\Houdini {}\bin\sesictrl.exe".format(args.version) 
		houdini_hserver_path = "hserver.exe"
		
	elif system_pl == "Darwin":
		houdini_sessictrl_path = r"/Applications/Houdini/Houdini{}/Frameworks/Houdini.framework/Versions/Current/Resources/houdini/sbin/sesictrl".format(args.version) 
		houdini_hserver_path = r"/Applications/Houdini/Houdini{}/Frameworks/Houdini.framework/Versions/Current/Resources/bin/hserver".format(args.version) 
	else:
		houdini_sessictrl_path = r"/opt/hfs{}/houdini/sbin/sesictrl".format(args.version) 
		houdini_hserver_path = r"/opt/hfs{}/bin/hserver".format(args.version) 
		
	if not is_license_expired(houdini_hserver_path):
		print("License is already installed.")
		#exit(0)
	servername, servercode = get_server_info(houdini_sessictrl_path)

	print('Server name: {}'.format(servername))
	print('Server code: {}'.format(servercode))

	browser = twill.commands.browser

	twill.commands.go('https://www.sidefx.com/login/')
	submit_form({'sfx-login-username': args.username, 'sfx-login-password': args.password})

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
			print("{} -I {}".format(houdini_sessictrl_path, key))
			output = subprocess.check_output("{} -I {}".format(houdini_sessictrl_path, key)).decode()
			print(output)
