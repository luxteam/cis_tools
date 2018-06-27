import requests
import config
import json
import argparse
from ast import literal_eval


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--build_number')
	parser.add_argument('--status')
	args = parser.parse_args()

	django_url = config.django_url

	get_json = requests.get("https://rpr.cis.luxoft.com/job/RenderSceneJob/{build_number}/api/json?pretty=true".format(build_number=args.build_number), \
		auth=(config.username, config.password))

	job_json = json.loads(get_json.text)

	
	artifacts = {}
	for job in job_json['artifacts']:
		artifacts[job['fileName']] = "https://rpr.cis.luxoft.com/job/RenderSceneJob/{build_number}/artifact/Output/{art}".format(build_number=args.build_number, art=job['fileName'])

	post_data = {'status': args.status, 'Build_number': args.build_number, 'artifacts':str(artifacts)}
	response = requests.post(django_url, data=post_data)

if __name__ == "__main__":

	main()

