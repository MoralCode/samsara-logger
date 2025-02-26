import requests
from pathlib import Path
import json
import argparse



def get_csrf(use_cache=True):
	tokencache = Path("token.json")
	cookiecache = Path("cookie.txt")
	if use_cache:
		if tokencache.exists() and cookiecache.exists():
			return json.loads(tokencache.read_text(encoding='utf8')).get("csrf_token"), cookiecache.read_text(encoding='utf8')
	r = requests.get("https://us6-ws.cloud.samsara.com/r/auth/csrf")

	cookie = r.headers.get("Set-Cookie")

	result = r.json()
	tokencache.write_text(json.dumps(result))
	cookiecache.write_text(cookie)

	return result.get("csrf_token"), cookie


print(get_csrf())

parser = argparse.ArgumentParser()

parser.add_argument('--nocache', action='store_true', help='disables the cache')

args = parser.parse_args()

