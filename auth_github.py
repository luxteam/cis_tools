import json
import os
import time
import argparse

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", "--user", package])

try:
    import jwt
    import requests
    from cryptography.hazmat.backends import default_backend
except Exception as ex:
    print("Required modules are missing, trying to install...")
    try:
        install("pyjwt")
        install("requests")
        install("cryptography")
        import jwt
        import requests
        from cryptography.hazmat.backends import default_backend
    except Exception as ex:
        print(ex)
        print("Failed to install dependency automatically.")
        print("Run: 'pip pyjwt requests cryptography' manually.")
        exit(-1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--github_app_id', required=True)
    parser.add_argument('--organization_name', required=True)
    parser.add_argument('--algorithm', required=False, default="RS256")
    parser.add_argument('--duration', required=False, default=600)

    args = parser.parse_args()

    key = os.getenv("github_app_key")

    time_since_epoch_in_seconds = int(time.time())

    key = key.replace("-----BEGIN RSA PRIVATE KEY-----", "").replace("-----END RSA PRIVATE KEY-----", "").replace(" ", "\n")
    key = "-----BEGIN RSA PRIVATE KEY-----\n" + key + "-----END RSA PRIVATE KEY-----\n"
    key_bytes = key.encode()
    private_key = default_backend().load_pem_private_key(key_bytes, None)

    payload = {
        # issued at time
        "iat": time_since_epoch_in_seconds,
        # JWT expiration time (10 minute maximum)
        "exp": time_since_epoch_in_seconds + int(args.duration),
        # GitHub App's identifier
        "iss": args.github_app_id
    }

    jwt_token = jwt.encode(payload, private_key, args.algorithm)
    headers = {"Authorization": "Bearer {}".format(jwt_token.decode())}

    response = requests.get("https://api.github.com/app/installations", headers=headers)
    installations_info = json.loads(response.content.decode())
    for installation in installations_info:
        if installation["account"]["html_url"].endswith(args.organization_name):
            installation_id = installation["id"]
            break
    else:
        print("Installation with specific organization or user name couldn't be found!")
        exit(-1)

    response = requests.post("https://api.github.com/app/installations/{}/access_tokens".format(str(installation_id)), headers=headers)
    installation_token = json.loads(response.content.decode())["token"]

    print(installation_token)
