import pytest
from engine.iam import IAM

USERS = {
    "david": {"policies": ["ReadOnlyStore"]},
    "admin_user": {"policies": ["AdminAccess"]},
    "no_policy_user": {"policies": []},
}

POLICIES = {
    "AdminAccess": {
        "Statements": [{"Effect": "Allow", "Actions": ["*"], "Resources": ["*"]}]
    },
    "ReadOnlyStore": {
        "Statements": [
            {
                "Effect": "Allow",
                "Actions": ["storage:Get*"],
                "Resources": ["arn:storage:bucket/*"],
            },
            {
                "Effect": "Deny",
                "Actions": ["storage:Get*"],
                "Resources": ["arn:storage:bucket/secret/*"],
            },
        ]
    },
}


@pytest.fixture
def iam():
    return IAM(USERS, POLICIES)


# --- Unknown user ---


def test_unknown_user_is_implicitly_denied(iam):
    assert (
        iam.evaluate("ghost", "storage:GetObject", "arn:storage:bucket/file.txt")
        == "DENIED (Implicit)"
    )


# --- david (ReadOnlyStore) ---


def test_read_allowed_bucket_object(iam):
    assert (
        iam.evaluate("david", "storage:GetObject", "arn:storage:bucket/photo.jpg")
        == "ALLOWED"
    )


def test_read_wildcard_action_allowed(iam):
    assert (
        iam.evaluate("david", "storage:GetFile", "arn:storage:bucket/data.csv")
        == "ALLOWED"
    )


def test_write_is_implicitly_denied(iam):
    assert (
        iam.evaluate("david", "storage:PutObject", "arn:storage:bucket/photo.jpg")
        == "DENIED (Implicit)"
    )


def test_delete_is_implicitly_denied(iam):
    assert (
        iam.evaluate("david", "storage:DeleteObject", "arn:storage:bucket/photo.jpg")
        == "DENIED (Implicit)"
    )


def test_secret_path_is_explicitly_denied(iam):
    assert (
        iam.evaluate(
            "david", "storage:GetObject", "arn:storage:bucket/secret/passwords.txt"
        )
        == "DENIED (Explicit)"
    )


def test_secret_subpath_is_explicitly_denied(iam):
    assert (
        iam.evaluate(
            "david", "storage:GetFile", "arn:storage:bucket/secret/deep/key.pem"
        )
        == "DENIED (Explicit)"
    )


def test_unrelated_service_is_implicitly_denied(iam):
    assert (
        iam.evaluate("david", "compute:TerminateInstance", "arn:compute:instance/42")
        == "DENIED (Implicit)"
    )


# --- admin_user (AdminAccess wildcard) ---


def test_admin_can_do_anything_on_any_resource(iam):
    assert (
        iam.evaluate(
            "admin_user", "compute:TerminateInstance", "arn:compute:instance/42"
        )
        == "ALLOWED"
    )


def test_admin_can_access_secret_path(iam):
    assert (
        iam.evaluate(
            "admin_user", "storage:GetObject", "arn:storage:bucket/secret/key.pem"
        )
        == "ALLOWED"
    )


def test_admin_can_delete(iam):
    assert (
        iam.evaluate(
            "admin_user", "storage:DeleteObject", "arn:storage:bucket/file.txt"
        )
        == "ALLOWED"
    )


# --- no_policy_user ---


def test_user_with_no_policies_is_implicitly_denied(iam):
    assert (
        iam.evaluate(
            "no_policy_user", "storage:GetObject", "arn:storage:bucket/file.txt"
        )
        == "DENIED (Implicit)"
    )


# --- Policy not in registry ---


def test_missing_policy_is_skipped_and_implicitly_denied(iam):
    users = {"orphan": {"policies": ["NonExistentPolicy"]}}
    iam_orphan = IAM(users, POLICIES)
    assert (
        iam_orphan.evaluate("orphan", "storage:GetObject", "arn:storage:bucket/x")
        == "DENIED (Implicit)"
    )
