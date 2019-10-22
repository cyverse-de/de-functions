# filter-running-analyses
#
# Accepts a list of analysis ID and filters out those that are listed as 
# Running by the DE DB.
# 
# A use case would be to get the list of VICE analyses running in the k8s
# cluster with the vice-running-in-cluster function and then use this function 
# to filter out the analyses that are marked as running in DB. The result 
# would be a list of analyses that are running when they probably shouldn't be.

import json
import os
import logging

from urllib.parse import urlparse, urlunparse

import requests

def handle(req):
    graphql_url = os.environ["GRAPHQL_URL"]

    parsed_req = json.loads(req)
    analyses_to_check = parsed_req["analyses"]

    logging.warning("analyses to check: %s" % analyses_to_check)

    # Get the list of running analyses from the DE DB
    response = requests.post(
        graphql_url,
        json={
            'query' : """
                query GetAnalysesByStatus($status: String!) {
                    analysesByStatus(status: $status) {
                        id
                    }
                }
            """,
            'variables' : {
                'status' : "Running"
            }
        }
    )

    response.raise_for_status()

    logging.warning("response %s" % response.text)

    parsed_results = response.json()
    running_analyses = list(map(lambda x : x["id"], parsed_results["data"]["analysesByStatus"]))
    filtered_list = list(filter(lambda x : not x in running_analyses, analyses_to_check))
    
    return json.dumps({
        "analyses" : filtered_list
    })
