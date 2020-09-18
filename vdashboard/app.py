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
    path = event.get("path", "")
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
            result_id = webhook_data["result_id"]
            event = webhook_data["event"]
        except (json.decoder.JSONDecodeError, KeyError):
            return simple_response(400, "Bad Request")
        print("Calling external API.")
        return simple_response(200, "200 OK", payload="Notification sent.")
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
