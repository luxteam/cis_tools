import argparse
import sys
import re

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('--index', type=int, default = 1, help = 'Index of inc number (default = 1)')
    parser.add_argument('--version', required = True, help = 'Version of build')
    parser.add_argument('--inc', type=int, default = 1, help = 'Increment number (default = 1)')

    args = parser.parse_args()

    index = args.index
    version = args.version
    inc = args.inc

    version_split = re.split(r'\.', version)
    index_version = str(version_split[index-1])
    new_index_version = str(int(index_version) + inc) 
    result = version.replace(index_version, new_index_version)
    print(result)

if __name__ == "__main__":

    main()
