import json
import os
import os.path
import logging

import requests

from urllib.parse import urljoin

def get_analysis_external_id(analysis_id):
    graphql_url = os.environ["GRAPHQL_URL"]

    response = requests.post(
        graphql_url,
        json={
            'query' : """
                query GetExternalID($analysisID: String!) {
                    analysis: analysisByID(analysisID: $analysisID) {
                        steps {
                            external_id
                        }
                    }
                }
            """,
            'variables' : {
                'analysisID' : analysis_id
            }
        }
    )

    response.raise_for_status()

    logging.warning("response: %s" % response.text)

    parsed_response = response.json()

    if parsed_response["data"] == None or parsed_response["data"]["analysis"] == None:
        return None

    return parsed_response["data"]["analysis"]["steps"][0]["external_id"]

def call_save_and_exit(external_id):
    app_exposer_url = os.environ["APP_EXPOSER_URL"]
    request_url = urljoin(app_exposer_url, os.path.join("vice", external_id, "save-and-exit"))
    response = requests.post(request_url)
    response.raise_for_status()
    logging.warning("response %s" % response.text)

def handle(req):
    parsed_req = json.loads(req)
    analysis_ids = parsed_req["analyses"]

    logging.warning("analyses to save-and-complete: %s" % analysis_ids)

    external_ids = list(map(get_analysis_external_id, analysis_ids))

    for external_id in external_ids:
        call_save_and_exit(external_id)

    return json.dumps({
        "analyses" : analysis_ids
    })
