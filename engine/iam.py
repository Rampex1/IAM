import fnmatch


class IAM:
    def __init__(self, users_data, policies_data):
        self.users = users_data
        self.policies = policies_data

    def _matches(self, policy_pattern, requested_item):
        return fnmatch.fnmatch(requested_item, policy_pattern)

    def evaluate(self, username, action, resource):
        if username not in self.users:
            return "DENIED (Implicit)"

        user = self.users[username]
        user_policies = user["policies"]

        matched_allow = False

        for policy_name in user_policies:
            if policy_name not in self.policies:
                continue

            statements = self.policies[policy_name]["Statements"]

            for s in statements:
                action_match = any(
                    self._matches(pattern, action) for pattern in s["Actions"]
                )
                resource_match = any(
                    self._matches(pattern, resource) for pattern in s["Resources"]
                )

                if action_match and resource_match:
                    if s["Effect"] == "Deny":
                        return "DENIED (Explicit)"
                    elif s["Effect"] == "Allow":
                        matched_allow = True

        if matched_allow:
            return "ALLOWED"

        return "DENIED (Implicit)"
