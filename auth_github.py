import json
import os
import time
import argparse

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

    parser.add_argument('--key', required=True)
    parser.add_argument('--github_app_id', required=True)
    parser.add_argument('--algorithm', required=False, default="RS256")
    parser.add_argument('--duration', required=False, default=600)

    args = parser.parse_args()

    time_since_epoch_in_seconds = int(time.time())

    args.key = args.key.replace("-----BEGIN RSA PRIVATE KEY-----", "").replace("-----END RSA PRIVATE KEY-----", "").replace(" ", "\n")
    args.key = "-----BEGIN RSA PRIVATE KEY-----\n" + args.key + "-----END RSA PRIVATE KEY-----\n"
    key_bytes = args.key.encode()
    print(key_bytes)
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

    resp = requests.get("https://api.github.com/app/installations", headers=headers)
    installation_id = json.loads(resp.content.decode())[0]["id"]

    resp = requests.post("https://api.github.com/app/installations/{}/access_tokens".format(str(installation_id)), headers=headers)
    installation_token = json.loads(resp.content.decode())["token"]

    print(installation_token)
