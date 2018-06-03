import os
import argparse


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--folder')
	args = parser.parse_args()

	folder = args.folder

	files = os.listdir(folder)
	scene = list(filter(lambda x: x.endswith('.blend'), files))
	print (scene[0])

	
if __name__ == "__main__":

	main()