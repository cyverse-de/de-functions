import json
import os
import logging
from flask import abort

from urllib.parse import urlparse, urlunparse

import requests
import requests.exceptions as HTTPError

def handle(req):
    apps_base_url = os.environ["APPS_URL"]

    apps_url = urlparse(apps_base_url)
    apps_url = apps_url._replace(path="/analyses")
    apps_url_str = urlunparse(apps_url)

    parsed_req = json.loads(req)
    analysis_to_check = parsed_req["analysis"]
    user = parsed_req["user"]

    response  = requests.get(
        apps_url_str,
        params={
            'user' : user,
            'filter' : json.dumps([{'field' : 'id', 'value' : analysis_to_check}])
        }
    )
    response.raise_for_status()

    logging.warning("response: %s" % response.text)

    parsed_response = response.json()

    retval = {}

    if len(parsed_response["analyses"]) < 1:
        abort(404)
    else:
        retval = parsed_response["analyses"][0] # looking up analysis by id, so there should only be one.

    return json.dumps(retval)
