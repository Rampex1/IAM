"""
Tests for cloud/ modules. All tests here are expected to FAIL until the
modules are implemented.
"""
import importlib
from cloud import storage, metadata

cloud_lambda = importlib.import_module("cloud.lambda")


# --- storage ---

def test_put_object_returns_success():
    result = storage.put_object("bucket/photo.jpg", b"image data")
    assert result is not None and result.get("status") == "ok"

def test_get_object_returns_stored_content():
    storage.put_object("bucket/hello.txt", b"hello")
    content = storage.get_object("bucket/hello.txt")
    assert content == b"hello"

def test_delete_object_removes_key():
    storage.put_object("bucket/temp.txt", b"tmp")
    assert storage.get_object("bucket/temp.txt") == b"tmp"  # must exist before delete
    storage.delete_object("bucket/temp.txt")
    assert storage.get_object("bucket/temp.txt") is None

def test_get_object_returns_none_for_missing_key_after_round_trip():
    storage.put_object("bucket/a.txt", b"a")
    assert storage.get_object("bucket/a.txt") == b"a"
    assert storage.get_object("bucket/b.txt") is None


# --- metadata ---

def test_put_item_returns_success():
    result = metadata.put_item("obj-1", {"size": 42, "type": "image/jpeg"})
    assert result is not None and result.get("status") == "ok"

def test_get_item_returns_stored_metadata():
    metadata.put_item("obj-2", {"size": 10, "type": "text/plain"})
    item = metadata.get_item("obj-2")
    assert item == {"size": 10, "type": "text/plain"}

def test_get_item_returns_none_for_missing_key_after_round_trip():
    metadata.put_item("obj-3", {"size": 1})
    assert metadata.get_item("obj-3") == {"size": 1}
    assert metadata.get_item("nonexistent-key") is None


# --- lambda handler ---

def test_allowed_request_returns_200():
    request = {
        "user": "david",
        "action": "storage:GetObject",
        "resource": "arn:storage:bucket/photo.jpg",
        "body": {},
    }
    response = cloud_lambda.handle_request(request)
    assert response is not None
    assert response.get("status_code") == 200

def test_denied_request_returns_403():
    request = {
        "user": "david",
        "action": "storage:PutObject",
        "resource": "arn:storage:bucket/photo.jpg",
        "body": {},
    }
    response = cloud_lambda.handle_request(request)
    assert response is not None
    assert response.get("status_code") == 403

def test_explicit_deny_returns_403():
    request = {
        "user": "david",
        "action": "storage:GetObject",
        "resource": "arn:storage:bucket/secret/key.pem",
        "body": {},
    }
    response = cloud_lambda.handle_request(request)
    assert response is not None
    assert response.get("status_code") == 403
