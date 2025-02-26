import requests
from pathlib import Path
import json
import argparse
from urllib.parse import urlparse


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


def get_locations_batch(csrf_token, cookie, samsara_token, org_id):

	headers = {
		'Accept': 'application/json; version=2',
		'Content-Type': 'application/json',
		'X-Csrf-Token': csrf_token,
		'Origin': 'https://cloud.samsara.com',
		'Cookie': cookie
	}
	query = """ 
query FleetViewer($token: string!, $duration: int64!) {
  fleetViewerToken(token: $token) {
    ...FleetViewerInfo
  }
}
fragment FleetViewerInfo on FleetViewerToken {
  description
  devices(feature: \"fleetTrackable\") {
    ...FleetViewerDevice
  }
  destinationName
  destinationAddress: address
  destinationLatitude: latitude
  destinationLongitude: longitude
  group {
    id
  }
  organization {
    name
    logoType
    logoDomain
    logoS3Location
  }
}
fragment FleetViewerDevice on Device {
  name
  id
  orgId
  location: fleetViewerLocation(duration: $duration) {
    time
    latitude
    longitude
    heading
    speed
    formatted
    locationSource
  }
  engineState: objectStat(statTypeEnum: osDEngineState, duration: $duration) {
    time: changedAtMs
    value: intValue
  }
  isAsset: hasFeature(featureKey: freight)
  deviceCable {
    powerStatusEvents(invalidateIfStale: true) {
      isOn
    }
  }
  currentDriver {
    id
    name
  }
  unpoweredDormantSince: objectStat(statTypeEnum: osDUnpoweredDormantSinceMs, duration: $duration) {
    value: intValue
  }
  hasLocationAdvertisement: hasFeature(featureKey: location_advertisement)
}
"""

	r = requests.post('https://us6-ws.cloud.samsara.com/r/graphql?q=FleetViewer', headers=headers, json={
		"query": query,
		"variables": {"token": samsara_token ,"duration":30000},"extensions":{"route":"/o/:org_id/fleet/viewer/:token","orgId":org_id,"stashOutput":True,"storeDepSet":True}
	})
	r.raise_for_status()
	return r.json()

parser = argparse.ArgumentParser()

parser.add_argument("url", help="the samsara url to get information from")
parser.add_argument('--nocache', action='store_true', help='disables the cache')

args = parser.parse_args()


url = urlparse(args.url)
path = url.path.split("/")
samsara_token = path[2]
org_id = path[5]


csrf, cookie = get_csrf(not args.nocache)
print(get_locations_batch(csrf, cookie, samsara_token, org_id))
