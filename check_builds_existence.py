from glob import glob
import os
import re
import requests
from requests.auth import HTTPBasicAuth
from shutil import rmtree
import traceback

# ----- CONFIGUTATION -----
JENKINS_URL = ''
USER = ''
TOKEN = ''
REPORTS_PATH = ''
# -------------------------


def do_request(endpoint):
    return requests.get(
        JENKINS_URL + endpoint,
        auth=HTTPBasicAuth(USER, TOKEN)
    )


def get_directories(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]


def find_build(path):
    try:
        directories = get_directories(path)

        # check that specified job exists (can prevent run with incorrect path in configuration)
        job_exist = check_existence(path)

        if not job_exist:
            print("Could not find job for its content by path: {}".format(path))

        builds_found = False

        if job_exist:
            for directory in directories:
                # directory which name contains only numbers - is root directory for build content
                if re.match("^[0-9]+$", directory):
                    builds_found = True
                    build_path = os.path.join(path, directory)
                    if check_existence(path, directory):
                        print("Found build for its content by path: {}".format(build_path))
                    else:
                        print("Could not find build for its content by path: {}. Delete it".format(build_path))
                        rmtree(os.path.join(path, directory))

            # if current directory doesn't contain directories with builds - continue
            if not builds_found:
                for directory in directories:
                    find_build(os.path.join(path, directory))
                
    except Exception as e:
        print("Could not process {}. Reason: {}".format(path, str(e)))
        traceback.print_exc()


def check_existence(path, build_number = ""):
    # replace REPORTS_PATH, backslashes by slashes and add "job" between packages and package and job name
    build_endpoint = os.path.join(path.replace(REPORTS_PATH, "", 1).replace("\\", "/").replace("/", "/job/"), build_number)
    response = do_request(build_endpoint)
    return response.status_code == 200


if __name__ == '__main__':
    root_directories = get_directories(REPORTS_PATH)

    for directory in root_directories:
        find_build(os.path.join(REPORTS_PATH, directory))
