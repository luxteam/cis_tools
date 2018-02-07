import argparse
import sys
import re

def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--file', required = True, help = 'File with build version string')
	parser.add_argument('--prefix', required = True, help = 'Prefix before build version')
	parser.add_argument('--delimiter', default = ".", required = True, help = 'Delimiter between numbers in version')

	args = parser.parse_args()

	file = args.file
	prefix = args.prefix
	delimiter = args.delimiter

	old_version = []

	with open(file) as f:
		for line in f:
			if line.find(prefix) != -1:
				prefix_line = line

	try:

		old_version = re.findall('\d'+ delimiter +'\d'+ delimiter+'\d'+ delimiter + '\d+', prefix_line)

		if len(old_version) == 0:
			old_version = re.findall('\d'+ delimiter +'\d'+ delimiter+'\d', prefix_line)
			if len(old_version) == 0:
				old_version = re.findall('\d'+ delimiter +'\d', prefix_line)
				if len(old_version) == 0: 
					old_version = re.findall('\d+', prefix_line)

		if len(old_version) == 0:
			print("Unsupported version. No numbers in prefix line.")
		else:	
			print(old_version[0])
				
	except UnboundLocalError:
		print("Error. No search string.")
		exit(0)
	

if __name__ == "__main__":

	main()
