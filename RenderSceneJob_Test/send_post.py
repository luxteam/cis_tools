import requests
import config
import json
import argparse


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--tool')
	parser.add_argument('--status')
	parser.add_argument('--id')
	parser.add_argument('--django_ip')
	parser.add_argument('--jenkins_job')
	args = parser.parse_args()

	django_url = args.django_ip

	get_json = requests.get("http://172.30.23.112:8088/job/{jenkins_job}/{build_number}/api/json?pretty=true".format(jenkins_job=args.jenkins_job, build_number=args.build_number), \
		auth=(config.username, config.password))

	job_json = json.loads(get_json.text)

	
	artifacts = {}
	for job in job_json['artifacts']:
		artifacts[job['fileName']] = "http://172.30.23.112:8088/job/{jenkins_job}/{build_number}/artifact/Output/{art}"\
																			.format(jenkins_job=args.jenkins_job, build_number=args.build_number, art=job['fileName'])

	zip_link = "http://172.30.23.112:8088/job/{jenkins_job}/{build_number}/artifact/*zip*/archive.zip"\
																					.format(jenkins_job=args.jenkins_job, build_number=args.build_number)

	post_data = {'status': args.status, 'tool': args.tool, 'zip_link': zip_link, 'artifacts':str(artifacts), 'id': args.id}
	response = requests.post(django_url, data=post_data)
	print(response)

if __name__ == "__main__":

	main()

