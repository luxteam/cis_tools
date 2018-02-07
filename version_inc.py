import argparse
import sys
import re

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--index', type=int, default = 1, help = 'Index of inc number (default = 1)')
    parser.add_argument('--version', required = True, help = 'Version of build')
    parser.add_argument('--inc', type=int, default = 1, help = 'Increment number (default = 1)')
    parser.add_argument('--delimiter', default = ".", help = 'Delimiter between numbers in version')

    args = parser.parse_args()

    index = args.index
    version = args.version
    inc = args.inc
    delimiter = args.delimiter

    version_split = re.split("\\" + delimiter, version)
    version_split[index - 1] = str(int(version_split[index-1])+ inc)
    print(delimiter.join(version_split))

if __name__ == "__main__":

    main()
