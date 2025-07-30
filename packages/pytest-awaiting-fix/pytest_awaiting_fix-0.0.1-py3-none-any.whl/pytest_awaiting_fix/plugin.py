import pytest
from jira import JIRA

_bug_numbers = set()
_jira_status_cache = {}
_test_names = {}


def awaiting_fix(bug_number):
    def decorator(func):
        marker = pytest.mark.awaiting_fix(bug_number)
        return marker(func)
    return decorator


def pytest_addoption(parser):
    parser.addoption(
        "--jira-server",
        action="store",
        help="JIRA server URL"
    )
    parser.addoption(
        "--jira-user",
        action="store",
        help="JIRA email address"
    )
    parser.addoption(
        "--jira-token",
        action="store",
        help="JIRA API token"
    )
    parser.addoption(
        "--jira-statuses",
        action="store",
        default="Ready for QA,QA",
        help="Comma-separated list of statuses to check and add commenting IE - QA, Sign Off"
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "awaiting_fix(bug_number): mark test as awaiting fix"
    )
    pytest.awaiting_fix = awaiting_fix

    # Read values from CLI
    jira_server = config.getoption("--jira-server")
    jira_user = config.getoption("--jira-user")
    jira_token = config.getoption("--jira-token")
    statuses = config.getoption("--jira-statuses")

    if not all([jira_server, jira_user, jira_token, statuses]):
        raise RuntimeError("Missing required Jira CLI args: --jira-server, --jira-user, --jira-token --jira-statuses")

    global jira_client, _jira_check_statuses
    _jira_check_statuses = set(s.strip() for s in statuses.split(","))

    try:
        jira_client = JIRA(server=jira_server, basic_auth=(jira_user, jira_token))
    except Exception as e:
        raise RuntimeError(f"Failed to authenticate to Jira: {e}")


def get_jira_status(bug_number):
    if bug_number not in _jira_status_cache:
        try:
            issue = jira_client.issue(bug_number)
            status = issue.fields.status.name
            _jira_status_cache[bug_number] = status
        except Exception as e:
            _jira_status_cache[bug_number] = "UNKNOWN"
    return _jira_status_cache[bug_number]


def pytest_runtest_setup(item):
    marker = item.get_closest_marker("awaiting_fix")
    if marker:
        bug_number = marker.args[0] if marker.args else None
        if bug_number:
            _bug_numbers.add(bug_number)
            _test_names.setdefault(bug_number, set()).add(item.nodeid)
            status = get_jira_status(bug_number)
            pytest.skip(f"Skipped awaiting fix for bug {bug_number} (status: {status})")


def pytest_sessionfinish(session, exitstatus):
    tagline = "🤖[*awaiting-fix*]🤖"
    if _bug_numbers:
        for bug in sorted(_bug_numbers):
            status = _jira_status_cache.get(bug, "UNKNOWN")
            if status in _jira_check_statuses:
                comments = jira_client.comments(bug)
                already_exists = any(tagline in comment.body for comment in comments)

                if not already_exists:
                    test_names = _test_names.get(bug, [])
                    tests = "\n".join(f"➡️ {test_name}" for test_name in sorted(test_names))
                    body = (
                        f"{tagline}\n"
                        f"🔔 When resolved, please re-enable automated test(s):\n{tests}"
                    )
                    try:
                        jira_client.add_comment(bug, body)
                        print(f"✅ Comment added to {bug}")
                    except Exception as e:
                        raise RuntimeError(f"❌ Failed to add comment to {bug}: {e}")
                else:
                    print(f"⚠️ Comment already exists for {bug}, skipping.")
