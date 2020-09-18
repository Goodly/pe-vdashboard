import json


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
    if "httpMethod" in event and event["httpMethod"] == "GET":
        # Pybossa does a GET on initial setting to validate URL
        # so must acknowledge GET
        return simple_response(200, "200 OK")
    if "httpMethod" in event and event["httpMethod"] == "PUT":
        path = event.get("path", "")
        headers = event["multiValueHeaders"]
        body = event.get("body", "{}")
        try:
            webhook_data = json.loads(body)
        except json.decoder.JSONDecodeError:
            return simple_response(400, "Bad Request")
        if ("project_short_name" in webhook_data and
            "project_id" in webhook_data and
            "task_id" in webhook_data and
            "result_id" in webhook_data and
            "event" in webhook_data):
            # Notify external party of webhook
            return simple_response(200, "200 OK")
    # Shouldn't reach here under normal use.
    print(body)
    return simple_response(400, "Bad Request")

def simple_response(status_code, status_desc, payload=""):
    return {
        "statusCode": status_code,
        "statusDescription": status_desc,
        "multiValueHeaders": {
            "Content-Type": ["text/plain; charset=utf-8"],
        },
        "isBase64Encoded": False,
        "body": payload
    }
