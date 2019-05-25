import requests
import json
import argparse


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--status')
	parser.add_argument('--id')
	parser.add_argument('--django_ip')
	args = parser.parse_args()

	post_data = {'status': args.status, 'tool': args.tool, 'id': args.id}
	response = requests.post(args.django_ip, data=post_data)
	print(response)

if __name__ == "__main__":
	main()

