import requests
import argparse
import config
import urllib3

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--version')
	args = parser.parse_args()

	urllib3.disable_warnings()

	try_count = 0
	while try_count < 3:
		try:
			headers_response = requests.head("https://rpr.cis.luxoft.com/job/RadeonProViewerAuto/job/master/{}/artifact/RprViewer.zip"\
				.format(args.version), auth=(config.jenkins_username, config.jenkins_password), verify=False)
			size = headers_response.headers['Content-Length']

			response = requests.get("https://rpr.cis.luxoft.com/job/RadeonProViewerAuto/job/master/{}/artifact/RprViewer.zip"\
				.format(args.version), auth=(config.jenkins_username, config.jenkins_password), verify=False, timeout=None)
			downloaded_size = response.headers['Content-Length']

			if size != downloaded_size:
				print("Server error. Retrying ...")
				raise Exception("Server error")

			if response.status_code == 200:
				print("GET request successfuly done. Saving file.")
				with open("RprViewer.zip", 'wb') as f:
					f.write(response.content)
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