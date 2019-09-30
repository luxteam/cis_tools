import requests
import config
import json
import argparse


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--status')
	parser.add_argument('--id')
	parser.add_argument('--django_ip')
	parser.add_argument('--build_number')
	parser.add_argument('--fail_reason')
	args = parser.parse_args()

	post_data = {'status': args.status, 'fail_reason': args.fail_reason, 'id': args.id, 'build_number': args.build_number}
	response = requests.post(args.django_ip, data=post_data)
	print(response)

if __name__ == "__main__":
	main()


