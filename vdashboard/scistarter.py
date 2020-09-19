import os

import json
import iso8601
from hashlib import sha256
import requests
from requests.compat import urlencode


PYBOSSA_API_KEY = os.environ.get("PYBOSSA_API_KEY")
SCISTARTER_API_KEY = os.environ.get("SCISTARTER_API_KEY")

def retrieve_email(user_id):
    """ 

    Input: A user_id mapping to some User Profile in Public Editor
    Output: The email that belongs to the user with the userid input

    """

    # Construct and call a GET request to public editor to get email given id
    url = f"https://pe.goodlylabs.org/api/user/{user_id}?api_key={PYBOSSA_API_KEY}"

    req = requests.get(url, headers={"Content-Type": "application/json"})

    # error handling
    if req.status_code != 200:
        raise Exception(req.status_code, req.reason)

    data = req.json()

    return data["email_addr"]


def retrieve_taskrun(taskrun_id):
    """ 

    Input: A taskrun_id mapping to some Taskrun in Public Editor
    Output: A json representing the data of a taskrun instance

    """

    url = f"https://pe.goodlylabs.org/api/taskrun/{taskrun_id}?api_key={PYBOSSA_API_KEY}"
    req = requests.get(url, headers={"Content-Type": "application/json"})

    # error handling
    if req.status_code != 200:
        raise Exception(req.status_code, req.reason)

    data = req.json()
    return data


def record_participation(taskrun_id, project_slug):
    """ 

    Input: A userid mapping to some User Profile in Public Editor, A project_slug representing a unique project on SciStarter
    Action: 

    Retrieves the email associated with userid and hashes the email. 
    Record participation for the specified user in the specified project

    This will appear to succeed, regardless of whether the user is
    actually a SciStarter user or not. However, in that case this API
    call is a no-op. It only reports an error if the request is
    incorrect in some way.

    If the email address does *not* belong to a SciStarter user, all
    we've received is an opaque hash value, which preserves the user's
    privacy; we have no way of reversing the hashing process to
    discover the email.

    The project_slug parameter should contain the textual unique
    identifier of the project. It is easily accesible from the project
    URL. In the URL https://scistarter.org/airborne-walrus-capture the
    slug is the string airborne-walrus-capture

    """

    # retrieve necessary data from a specific taskrun
    taskrun_json = retrieve_taskrun(taskrun_id)

    # calculate the total seconds user spent on task
    pybossa_created = iso8601.parse_date(taskrun_json.get('created'))
    pybossa_finish_time = iso8601.parse_date(taskrun_json.get('finish_time'))
    elapsed_time = pybossa_finish_time - pybossa_created
    total_seconds = int(elapsed_time.total_seconds())

    # retrieve email from user_id and hash the email
    email = retrieve_email(taskrun_json.get('user_id'))
    hashed = sha256(email.encode("utf8")).hexdigest()

    # construct parameters for POST request to SciStarter
    url = "https://scistarter.org/api/participation/hashed/" + \
        project_slug + "?key=" + SCISTARTER_API_KEY

    data = {
        "hashed": hashed,
        "type": "classification",  # other options: 'collection', 'signup'
        "duration": total_seconds,  # Seconds the user spent participating, or an estimate
    }

    req = requests.post(url=url, data=urlencode(data).encode("utf8"))
    if req.status_code != 200:
        raise Exception(req.status_code, req.reason)

    return req.json()


if __name__ == "__main__":
    print(record_participation(input("TaskRun ID: "), input("Project slug: ")))
