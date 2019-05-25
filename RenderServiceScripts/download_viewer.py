import requests
import argparse
import config

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--version')
	args = parser.parse_args()

	r = requests.get("https://rpr.cis.luxoft.com/job/RadeonProViewerAuto/job/master/{}/artifact/RprViewer.zip"\
		.format(args.version), auth=(config.jenkins_username, config.jenkins_password), verify=False)

	with open("RprViewer.zip", 'wb') as f:
		f.write(r.content)
		
	print ("SUCCESS")

	
if __name__ == "__main__":

	main()