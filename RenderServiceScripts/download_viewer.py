import requests
import argparse
import config
import urllib3
import logging
import os


# logging
logging.basicConfig(filename="python_log.txt", level=logging.INFO)
logger = logging.getLogger(__name__)

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--version')
	args = parser.parse_args()

	urllib3.disable_warnings()

	try_count = 0
	while try_count < 3:
		try:
			response = requests.get("https://rpr.cis.luxoft.com/job/RadeonProViewerAuto/job/master/{}/artifact/RprViewer_Windows.zip"\
				.format(args.version), auth=(config.jenkins_username, config.jenkins_password), verify=False, timeout=None)
			original_size = response.headers['Content-Length']
			logger.info("Original size: " + original_size)
		
			if response.status_code == 200:
				print("GET request successfuly done. Saving file.")
				with open("RprViewer.zip", 'wb') as f:
					f.write(response.content)

				downloaded_size = os.path.getsize('RprViewer.zip')
				logger.info("Downloaded size: " + str(downloaded_size))
				if int(original_size) != downloaded_size:
					logger.error("Server error. Retrying ...")
					print("Server error. Retrying ...")
					raise Exception("Server error")
				break
			else:
				print("GET request failed, status code: " + str(response.status_code))
				break
		except Exception as e:
			if try_count == 2:
				print("GET request try 3 failed. Finishing work.")
				break
			try_count += 1
			print("GET requests failed. Retry ...")
	
	
if __name__ == "__main__":
	main()