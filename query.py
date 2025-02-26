import requests
from pathlib import Path
import json



def get_csrf(use_cache=True):
	tokencache = Path("token.json")
	if use_cache:
		if tokencache.exists():
			return json.loads(tokencache.read_text()).get("csrf_token")
	r = requests.get("https://us6-ws.cloud.samsara.com/r/auth/csrf")

	result = r.json()
	tokencache.write_text(json.dumps(result))

	return result.get("csrf_token")

print(get_csrf())

