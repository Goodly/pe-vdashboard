import os
import json

from scistarter import record_participation

def lambda_handler(event, context):
    """Handle a Pybossa webhook

    Parameters
    ----------
    event: dict, required

    context: object, required
        Lambda Context runtime methods and attributes
        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    """
    # If a project's SciStarter URL is https://scistarter.org/an-example, then the slug is
    # "an-example". This icoming path is "/project/an-example", so take the basename
    # as the SciStarter project slug.
    path = event.get("path", "")
    project_slug = os.path.basename(path)
    headers = event.get("multiValueHeaders", {})
    body = event.get("body", "")
    if "httpMethod" in event and event["httpMethod"] == "GET":
        # Pybossa does a GET on initial setting to validate URL
        # so must acknowledge GET
        return simple_response(200, "200 OK", payload="Ready for webhook.")
    if "httpMethod" in event and event["httpMethod"] == "POST":
        try:
            webhook_data = json.loads(body)
            project_short_name = webhook_data["project_short_name"]
            project_id = webhook_data["project_id"]
            task_id = webhook_data["task_id"]
            # taskrun_id is only provided by a patched version of Pybossa
            taskrun_id = int(webhook_data.get("taskrun_id", -1))
            user_id = int(webhook_data.get("user_id", -1))
            result_id = webhook_data["result_id"]
            event = webhook_data["event"]
        except (json.decoder.JSONDecodeError, KeyError, ValueError, TypeError):
            return simple_response(400, "Bad Request")
        if taskrun_id != -1:
            print(
                f"Notified of taskrun {taskrun_id} "
                f"by user {user_id} in project {project_short_name}. "
                f"Crediting to SciStarter project {project_slug}."
            )
            try:
                record_participation(taskrun_id, project_slug)
                return simple_response(200, "200 OK", payload="Notification sent.")
            except Exception as e:
                return simple_response(400, "Bad Request", payload=f"Exception: {str(e)}")
        else:
            return simple_response(400, "Bad Request", payload="Webhook did not provide taskrun_id.")
    # Shouldn't reach here under normal use.
    print(path)
    print(json.dumps(headers))
    print(body)
    return simple_response(400, "Bad Request")

def simple_response(status_code, status_desc, payload=""):
    print(f"RETURN STATUS CODE: {status_code}")
    return {
        "statusCode": status_code,
        "statusDescription": status_desc,
        "multiValueHeaders": {
            "Content-Type": ["text/plain; charset=utf-8"],
        },
        "isBase64Encoded": False,
        "body": payload
    }
