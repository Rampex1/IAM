from cloud import metadata, storage
from engine.iam import IAM
import json

with open("data/users.json") as f:
    users = json.load(f)
with open("data/policies.json") as f:
    policies = json.load(f)

evaluator = IAM(users, policies)


def parse_resource(resource):
    """
    arn:storage:bucket/photo.jpg -> photo.jpg
    """
    return resource.split("bucket/")[-1]


def handle_request(request):
    """
    request = {
        "user": "david",
        "action": "storage:PutObject",
        "resource": "arn:storage:bucket/photo.jpg",
        "body": {...}
    }
    """
    user = request["user"]
    action = request["action"]
    resource = request["resource"]
    body = request.get("body", {})

    result = evaluator.evaluate(user, action, resource)

    if result != "ALLOWED":
        return {"status_code": 403, "status": "DENIED", "reason": result}

    service, operation = action.split(":")
    key = parse_resource(resource)

    if service == "storage":
        if operation == "PutObject":
            content = body.get("content", "")
            storage.put_object(key, content)
            return {"status_code": 200, "status": "OK", "message": "Object stored"}

        elif operation == "GetObject":
            data = storage.get_object(key)
            return {"status_code": 200, "status": "OK", "data": data}

        elif operation == "DeleteObject":
            storage.delete_object(key)
            return {"status_code": 200, "status": "OK", "message": "Deleted"}

    elif service == "metadata":
        if operation == "PutItem":
            metadata.put_item(key, body)
            return {"status_code": 200, "status": "OK"}

        elif operation == "GetItem":
            item = metadata.get_item(key)
            return {"status_code": 200, "status": "OK", "data": item}

    return {"status_code": 500, "status": "ERROR", "message": "Invalid action"}
