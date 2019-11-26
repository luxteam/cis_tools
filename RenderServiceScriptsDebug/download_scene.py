import requests
import os
import config
import logging
import argparse

# logging
logging.basicConfig(filename="python_log.txt", level=logging.INFO)
logger = logging.getLogger(__name__)

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--url')
	parser.add_argument('--id')
	parser.add_argument('--scene_name')
	args = parser.parse_args()

	url_login = "{}/accounts/login/".format(args.url) 
	client = requests.session()
	client.get(url_login)
	csrftoken = client.cookies['csrftoken']

	login_data = {'username': config.django_username, 'password': config.django_password, 'csrfmiddlewaretoken': csrftoken}

	try:
		client.post(url_login, data=login_data)
	except:
		pass

	downloaded_file = client.post('{}/upload/download/{}'.format(args.url, args.id), data=login_data)

	with open(args.scene_name, 'wb') as f:
		f.write(downloaded_file.content)
	
	
if __name__ == "__main__":
	main()
