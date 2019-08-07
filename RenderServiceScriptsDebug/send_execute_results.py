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

	try_count = 0
	while try_count < 3:
		try:
			response = requests.get("http://rpr.cis.luxoft.com/job/{jenkins_job}/{build_number}/api/json?pretty=true".format(jenkins_job=args.jenkins_job, build_number=args.build_number), \
				auth=(config.jenkins_username, config.jenkins_password))
			if response.status_code  == 200:
				print("GET request successfuly done.")
				break
			else:
				print("GET request failed, status code: " + str(response.status_code))
				break
		except Exception as e:
			if try_count == 2:
				print("GET request try 3 failed. Finishing work.")
				break
			try_count += 1
			print("GET request failed. Retry ...")
		

	job_json = json.loads(response.text)

	artifacts = {}
	for job in job_json['artifacts']:
		artifacts[job['fileName']] = "http://172.30.23.112:8088/job/{jenkins_job}/{build_number}/artifact/Output/{art}"\
			.format(jenkins_job=args.jenkins_job, build_number=args.build_number, art=job['fileName'])
	zip_link = "http://172.30.23.112:8088/job/{jenkins_job}/{build_number}/artifact/Output/*zip*/Output.zip"\
																					.format(jenkins_job=args.jenkins_job, build_number=args.build_number)

	post_data = {'status': args.status, 'artifacts':str(artifacts), 'id': args.id, 'build_number': args.build_number, 'zip_link': zip_link}

	try_count = 0
	while try_count < 3:	
		try:
			response = requests.post(django_url, data=post_data)
			if response.status_code  == 200:
				print("POST request successfuly sent.")
				break
			else:
				print("POST request failed, status code: " + str(response.status_code))
				break
		except Exception as e:
			if try_count == 2:
				print("POST request try 3 failed. Finishing work.")
				break
			try_count += 1
			print("POST request failed. Retry ...")
		
if __name__ == "__main__":
	main()


