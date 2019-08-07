import requests
import json
import argparse


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--tool')
	parser.add_argument('--status')
	parser.add_argument('--id')
	parser.add_argument('--django_ip')
	parser.add_argument('--current_frame')
	parser.add_argument('--render_time')
	args = parser.parse_args()

	django_url = args.django_ip

	post_data = {'status': args.status, 'tool': args.tool, 'id': args.id}
	response = requests.post(django_url, data=post_data)
	print(response)

if __name__ == "__main__":
	main()
	exit(0)

