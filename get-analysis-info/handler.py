import json
import os
import logging

import requests

def handle(req):
    graphql_url = os.environ["GRAPHQL_URL"]

    parsed_req = json.loads(req)

    analyses = parsed_req["analyses"]

    retval = {
        "analyses" : []
    }

    for analysis in analyses:
        response = requests.post(
            graphql_url,
            json={
                'query' : """
                    query GetAnalysisByID($analysisID: String!) {
                        analysis: analysisByID(analysisID: $analysisID) {
                            id
                            name
                            description
                            username
                            status
                            system_id
                            start_date
                            planned_end_date
                            end_date
                            result_folder_path
                            type
                            subdomain
                            deleted
                            notify
                            app {
                                id
                                name
                                description
                            }

                        }
                    }
                """,
                'variables' : {
                    "analysisID" : analysis
                }
            }
        )

        response.raise_for_status()

        logging.warning("response: %s" % response.text)

        parsed_response = response.json()

        if parsed_response["data"]["analysis"] != None:
            retval["analyses"].append(parsed_response["data"]["analysis"])

    return json.dumps(retval)
