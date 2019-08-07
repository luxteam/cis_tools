import requests
import json
import argparse


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--status')
	parser.add_argument('--id')
	parser.add_argument('--django_ip')
	args = parser.parse_args()

	post_data = {'status': args.status, 'id': args.id}
	
	try_count = 0
	while try_count < 3:
		try:
			response = requests.post(args.django_ip, data=post_data)
			if response.status_code  == 200:
				print("POST request successfuly sent.")
				break
			else:
				print("POST reques failed, status code: " + str(response.status_code))
				break
		except Exception as e:
			if try_count == 2:
				print("POST request try 3 failed. Finishing work.")
				break
			try_count += 1
			print("POST request failed. Retry ...")
				
			

if __name__ == "__main__":
	main()
	exit(0)

