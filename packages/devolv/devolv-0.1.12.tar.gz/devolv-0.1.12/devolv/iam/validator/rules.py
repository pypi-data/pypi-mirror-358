import json

def _find_statement_line(stmt, raw_lines):
    if raw_lines is None:
        return None
    stmt_text = json.dumps(stmt, indent=2).splitlines()[0].strip()
    for i, line in enumerate(raw_lines):
        if stmt_text in line:
            return i + 1
    return None

def check_wildcard_actions(policy, raw_lines=None):
    statements = policy.get("Statement", [])
    if not isinstance(statements, list):
        statements = [statements]

    for stmt in statements:
        if stmt.get("Effect", "Allow") != "Allow":
            continue

        actions = stmt.get("Action", [])
        resources = stmt.get("Resource", [])

        if isinstance(actions, str):
            actions = [actions]
        if isinstance(resources, str):
            resources = [resources]

        for a in actions:
            if a == "*" or a.endswith(":*"):
                if any(r == "*" for r in resources):
                    line_num = _find_statement_line(stmt, raw_lines)
                    return {
                        "id": "IAM001",
                        "level": "high",
                        "message": (
                            f"Policy uses wildcard action '{a}' with wildcard resource '*' — overly permissive."
                            + (f" Statement starts at line {line_num}." if line_num else "")
                        )
                    }
                else:
                    line_num = _find_statement_line(stmt, raw_lines)
                    return {
                        "id": "IAM001",
                        "level": "high",
                        "message": (
                            f"Policy uses wildcard action '{a}' — overly permissive."
                            + (f" Statement starts at line {line_num}." if line_num else "")
                        )
                    }
    return None


def check_passrole_wildcard(policy, raw_lines=None):
    statements = policy.get("Statement", [])
    if not isinstance(statements, list):
        statements = [statements]

    for stmt in statements:
        if stmt.get("Effect", "Allow") != "Allow":
            continue

        actions = stmt.get("Action", [])
        resources = stmt.get("Resource", [])

        if isinstance(actions, str):
            actions = [actions]
        if isinstance(resources, str):
            resources = [resources]

        if any(a.lower() == "iam:passrole" for a in actions) and "*" in resources:
            line_num = _find_statement_line(stmt, raw_lines)
            return (
                f"iam:PassRole with wildcard Resource ('*') can lead to privilege escalation."
                + (f" Statement starts at line {line_num}." if line_num else "")
            )
    return None

RULES = [
    {
        "id": "IAM001",
        "level": "high",
        "description": "Wildcard in Action (e.g. * or service:*) is overly permissive",
        "check": check_wildcard_actions,
    },
    {
        "id": "IAM002",
        "level": "high",
        "description": "PassRole with wildcard Resource",
        "check": check_passrole_wildcard,
    },
]
