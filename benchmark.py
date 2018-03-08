import os
import time
import subprocess
import datetime
import argparse


def create_arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('output')

    return parser.parse_args()

def main():
    args = create_arg_parse()
    while True:
        filesystem_time = str(filesystem_benchmark())
        cpu_time = str(cpu_benchmark())
        with open(os.path.join(args.output, 'benchmark.csv'), 'a') as file:
            file.write(str(datetime.datetime.today()) +";"+ filesystem_time +";"+ cpu_time + "\n") 

        time.sleep(600)


def filesystem_benchmark():
    start_time = time.time()
    if os.name == 'nt':
        os.chdir('c:')
        subprocess.run(['tree'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif os.name == 'posix':
        subprocess.run(['ls -R /'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return time.time() - start_time


def cpu_benchmark():
    start_time = time.time()
    for i in [1000000]:
        for j in [1000000]:
            a = i ** j

    return time.time() - start_time


if __name__ == '__main__':
    main()
