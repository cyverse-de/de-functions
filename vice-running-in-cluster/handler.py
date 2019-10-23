import json
import os
import logging

import requests
from kubernetes import client, config

has_loaded_k8s_config = False

vice_namespace = "vice-apps"

def init_k8s_config():
    global has_loaded_k8s_config

    if not has_loaded_k8s_config:
        config.load_incluster_config()
        has_loaded_k8s_config = True

def get_analysis_id(external_id):
    global vice_namespace
    
    graphql_url = os.environ["GRAPHQL_URL"]

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

    return parsed_response["data"]["analysis"]["id"]

def handle(req):
    init_k8s_config()

    api = client.AppsV1Api()

    response = api.list_namespaced_deployment(vice_namespace)
    external_ids = list(map(lambda x : x.metadata.name, response.items))
    analysis_ids = list(map(get_analysis_id, external_ids))

    return json.dumps({
        "analyses" : analysis_ids
    })
