import json
import os
import logging

import requests

def handle(req):
    graphql_url = os.environ["GRAPHQL_URL"]

    parsed_req = json.loads(req)
    external_id = parsed_req["external_id"]

    response = requests.post(
        graphql_url,
        json={
            'query' : """
                query GetAnalysisID($externalID: String!) {
                    analysis: analysisByExternalID(externalID: $externalID) {
                        id
                    }
                }
            """,
            'variables' : {
                'externalID' : external_id
            }
        }
    )

    response.raise_for_status()

    logging.warning("response: %s" % response.text)

    parsed_response = response.json()

    return parsed_response["data"]["analysis"]
