import json
import os
import logging

import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException

has_loaded_k8s_config = False

vice_namespace = "vice-apps"

def init_k8s_config():
    global has_loaded_k8s_config

    if not has_loaded_k8s_config:
        config.load_incluster_config()
        has_loaded_k8s_config = True

def get_external_id(analysis_id):
    graphql_url = os.environ["GRAPHQL_URL"]

    response = requests.post (
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

    logging.debug("response: %s" % response.text)

    parsed_response = response.json()

    return parsed_response["data"]["analysis"]["steps"][0]["external_id"]

def handle(req):
    global vice_namespace

    init_k8s_config()

    api = client.AppsV1Api()
    extv1b1 = client.ExtensionsV1beta1Api()
    corev1 = client.CoreV1Api()

    parsed_req = json.loads(req)
    analyses = parsed_req["analyses"]

    for analysis_id in analyses:
        external_id = get_external_id(analysis_id)

        # Delete the deployment
        try:
            response = api.delete_namespaced_deployment(external_id, vice_namespace)
            logging.warning("delete deployment %s response: %s" % (external_id, response))
        except ApiException as e:
            logging.Warning("error deleting deployment %s: %s" % (external_id, e))

        # Delete the ingress
        try:
            response = extv1b1.delete_namespaced_ingress(external_id, vice_namespace)
            logging.warning("delete ingress %s response: %s", (external_id, response))
        except ApiException as e:
            logging.Warning("error deleting ingress %s: %s" % (external_id, e))

        # Delete the service
        svc = "vice-%s" % external_id
        try:
            response = corev1.delete_namespaced_service(svc, vice_namespace)
            logging.warning("delete service %s response: %s" % (svc, response))
        except ApiException as e:
            logging.Warning("error deleting service %s: %s" % (svc, e))

        # Delete the input-path-list config map
        input_path_list_cfgmap = "input-path-list-%s" % external_id
        try:
            response = corev1.delete_namespaced_config_map(input_path_list_cfgmap, vice_namespace)
            logging.warning("delete configmap %s response: %s" % (input_path_list_cfgmap, response))
        except ApiException as e:
            logging.Warning("error deleting configmap %s: %s" % (input_path_list_cfgmap, e))

        # Delete the excludes-file config map
        excludes_file_cfgmap = "excludes-file-%s" % external_id
        try:
            response = corev1.delete_namespaced_config_map(excludes_file_cfgmap, vice_namespace)
            logging.warning("delete configmap %s response: %s" % (excludes_file_cfgmap, response))
        except ApiException as e:
            logging.Warning("error deleting configmap %s: %s" % (excludes_file_cfgmap, e))
    
    return json.dumps({
        "analyses" : analyses
    })

