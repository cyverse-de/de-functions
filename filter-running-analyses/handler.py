import json
import os
import logging

from urllib.parse import urlparse, urlunparse

import requests
import requests.exceptions as HTTPError

def handle(req):
    apps_base_url = os.environ["APPS_URL"]
    apps_user = os.environ["APPS_USER"]

    apps_url = urlparse(apps_base_url)
    apps_url = apps_url._replace(path="/analyses")
    apps_url_str = urlunparse(apps_url)

    logging.warning("apps url: %s" % apps_url_str)

    parsed_req = json.loads(req)
    analyses_to_check = parsed_req["analyses"]

    retval = {
        "analyses" : []
    }

    logging.warning("analyses to check: %s" % analyses_to_check)
    for analysis in analyses_to_check:
        response = requests.get(
            apps_url_str,
            params={
                'user' : apps_user,
                'filter' : json.dumps([{'field':'id', 'value': analysis}])
            }
        )

        parsed_response = response.json()

        logging.warning("parsed response: %s" % parsed_response)

        for lookup in parsed_response["analyses"]:
            if not lookup["status"].lower() in ["completed", "failed", "cancelled", "canceled"]:
                retval["analyses"].append(analysis)

    return json.dumps(retval)
