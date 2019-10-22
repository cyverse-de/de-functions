import json
import os
import logging
from flask import abort

from urllib.parse import urlparse, urlunparse

import requests
import requests.exceptions as HTTPError

def handle(req):
    graphql_url = os.environ["GRAPHQL_URL"]

    parsed_req = json.loads(req)
    analysis_to_check = parsed_req["id"]
    user = parsed_req["user"]

    response = requests.post(
        graphql_url,
        json={
            'query' : """
                query GetAnalysisInfo($user: String, $id: String) {
                    analysis(username: $user, analysisID: $id) {
                        id
                        name
                        description
                        can_share
                        batch_status {
                            total
                            completed
                            running
                            submitted
                        }
                        batch
                        startdate
                        enddate
                        status
                        parent_id
                        interactive_urls
                        wiki_url
                        notify
                        resultfolderid
                        app {
                            id
                            app_type
                            beta
                            can_favor
                            can_rate
                            can_run
                            debug
                            deleted
                            description
                            disabled
                            edited_date
                            groups
                            integration_date
                            integrator_email
                            integrator_name
                            is_favorite
                            is_public
                            label
                            name
                            permission
                            pipeline_eligibility {
                                is_valid
                                reason
                            }
                            rating {
                                average
                                total
                                user
                                comment_id
                            }
                            requirements {
                                min_cpu_cores
                                min_memory_limit
                                min_disk_space
                                max_cpu_cores
                                memory_limit
                                step_number
                            }
                            step_count
                            system_id
                            wiki_url
                        }
                        steps {
                            step_number
                            external_id
                            enddate
                            startdate
                            status
                            updates {
                                status
                                message
                                timestamp
                            }
                            app_step_number
                            step_type
                        }
                        parameters {
                            data_format
                            param_type
                            param_id
                            info_type
                            is_default_value
                            param_name
                            parameter_value {
                                value
                            }
                            is_visible
                            full_param_id
                            data_format
                        }
                    }
                }
            """,
            'variables' : {
                "user" : user,
                "id" : analysis_to_check
            }
        }
    )

    response.raise_for_status()

    logging.warning("response: %s" % response.text)

    parsed_response = response.json()

    retval = {}

    if parsed_response["data"]["analysis"] != None:
        retval = parsed_response["data"]["analysis"]

    return json.dumps(retval)
