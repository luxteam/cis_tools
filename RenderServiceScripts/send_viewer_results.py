import requests
import config
import json
import argparse


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--status')
	parser.add_argument('--id')
	parser.add_argument('--django_ip')
	parser.add_argument('--jenkins_job')
	parser.add_argument('--build_number')
	args = parser.parse_args()

	django_url = args.django_ip

	get_json = requests.get("http://rpr.cis.luxoft.com/job/{jenkins_job}/{build_number}/api/json?pretty=true".format(jenkins_job=args.jenkins_job, build_number=args.build_number), \
		auth=(config.jenkins_username, config.jenkins_password))

	job_json = json.loads(get_json.text)

	artifacts = {}
	for job in job_json['artifacts']:
		artifacts[job['fileName']] = "http://172.30.23.112:8088/job/{jenkins_job}/{build_number}/artifact/{art}"\
																			.format(jenkins_job=args.jenkins_job, build_number=args.build_number, art=job['fileName'])
	post_data = {'status': args.status, 'artifacts':str(artifacts), 'id': args.id, 'build_number': args.build_number}
	response = requests.post(django_url, data=post_data)
	print(response)

if __name__ == "__main__":

	main()

