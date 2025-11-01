import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()
GITLAB_URL = os.getenv("GITLAB_URL", "http://localhost")
PRIVATE_TOKEN = os.getenv("GITLAB_TOKEN")

HEADERS = {
    "Private-Token": PRIVATE_TOKEN,
    "Content-Type": "application/json"
}

def set_user_role(username: str, repo_or_group: str, role: str):
    """
    This function grants or updates permissions for an existing user on a repository or group.
    - username: the GitLab username of the user
    - repo_or_group: the full namespace path of the group or project
    - role: the role name (Guest / Reporter / Developer / Maintainer / Owner)
    """

    ROLE_MAP = {
        "Guest": 10,
        "Reporter": 20,
        "Developer": 30,
        "Maintainer": 40,
        "Owner": 50
    }

    if role not in ROLE_MAP:
        return {"error": f"Invalid role '{role}'"}, 400

    try:
        # find user id by 'username'
        user_resp = requests.get(f"{GITLAB_URL}/api/v4/users?username={username}", headers=HEADERS)
        if user_resp.status_code != 200:
            return {"error": f"Failed to search user ({user_resp.status_code})"}, user_resp.status_code

        users = user_resp.json()
        if not users:
            return {"error": f"User '{username}' not found"}, 404

        user_id = users[0]["id"]

        # Check whether the target is a group or a project
        encoded_path = urllib.parse.quote(repo_or_group, safe='') # encode slashes to %2F

        group_resp = requests.get(f"{GITLAB_URL}/api/v4/groups/{encoded_path}", headers=HEADERS)
        if group_resp.status_code == 200:
            target = f"groups/{encoded_path}/members"
        else:
            proj_resp = requests.get(f"{GITLAB_URL}/api/v4/projects/{encoded_path}", headers=HEADERS)
            if proj_resp.status_code == 200:
                target = f"projects/{encoded_path}/members"
            else:
                return {"error": f"Group or project '{repo_or_group}' not found"}, 404

        # Check if the user is already a member
        members_resp = requests.get(f"{GITLAB_URL}/api/v4/{target}", headers=HEADERS)
        if members_resp.status_code == 200:
            members = members_resp.json()
            existing = None
            for member in members:
                if member["id"] == user_id:
                    existing = member
                    break
            if existing:
                # The user is already a member → update their role (PUT)
                update_url = f"{GITLAB_URL}/api/v4/{target}/{user_id}"
                update_payload = {"access_level": ROLE_MAP[role]}
                update_resp = requests.put(update_url, headers=HEADERS, json=update_payload)
                if update_resp.status_code == 200:
                    return {
                        "message": f"Updated role to '{role}' for user '{username}'",
                        "check": f"{GITLAB_URL}/api/v4/{target}"}, 200
                else:
                    return {"error": f"Failed to update role ({update_resp.text})"}, update_resp.status_code

        # The user is not a member → grant access (POST)
        payload = {"user_id": user_id, "access_level": ROLE_MAP[role]}
        resp = requests.post(f"{GITLAB_URL}/api/v4/{target}", headers=HEADERS, json=payload)

        if resp.status_code in (200, 201):
            return {"message": f"Granted role '{role}' to user '{username}' on '{repo_or_group}'",
            "check": f"{GITLAB_URL}/api/v4/{target}"}, resp.status_code
        else:
            return {"error with grante": resp.text, "check": f"{GITLAB_URL}/api/v4/{target}"}, resp.status_code

    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}, 503
    except KeyError as e:
        return {"error": f"Invalid response from GitLab API: missing key {str(e)}"}, 500
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}, 500


def get_gitlab_data(data_type: str, year: int):
    """
    Fetch all issues or merge requests created during a given year.
    - data_type: 'issues' or 'mr'
    - year: 4-digit year (e.g., 2024)
    """

    if data_type not in ["issues", "mr"]:
        return {"error": "Invalid type. Must be 'issues' or 'mr'."}, 400

    try:
        # Choose endpoint based on type
        endpoint = "merge_requests" if data_type == "mr" else "issues"

        url = f"{GITLAB_URL}/api/v4/{endpoint}"
        params = {
            "created_after": f"{year}-01-01T00:00:00Z",
            "created_before": f"{year}-12-31T23:59:59Z",
            "scope": "all"  # ensures it fetches all projects/groups in the system
        }

        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            return {"error": f"GitLab API returned {response.status_code}: {response.text}"}, response.status_code

        data = response.json()

        # Create a simplified list with only the id, title, and creation date of each item
        result = []
        for item in data:
            entry = {
                "id": item["id"],
                "title": item.get("title", ""),
                "created_at": item.get("created_at", "")
            }
            result.append(entry)

        return result, 200
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}, 503
    except KeyError as e:
        return {"error": f"Invalid response from GitLab API: missing key {str(e)}"}, 500
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}, 500
